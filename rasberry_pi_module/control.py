# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Henrik Blidh
# Copyright (c) 2022-2023 The Pybricks Authors

import asyncio
# import aioconsole   # not used at the moment
import sys
from contextlib import suppress
from bleak import BleakScanner, BleakClient
import numpy as np
import Ar2Pi
import get_lidar_info

direction = ['f','b','r','l']
Arduino_port = "/dev/tty.usbmodem1101"
port = "/dev/tty.usbserial-0001"
arduino = Ar2Pi.ArduinoReader(Arduino_port)

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"

# Replace this with the name of your hub if you changed
# it when installing the Pybricks firmware. 
HUB_NAME = "Pybricks Hub"


async def main():
    main_task = asyncio.current_task()

    def handle_disconnect(_):
        print("Hub was disconnected.")
        if not main_task.done():
            main_task.cancel()

    ready_event = asyncio.Event()

    def handle_rx(_, data: bytearray):
        # Defensive: ignore empty notifications
        if not data:
            return

        if data[0] == 0x01:
            payload = data[1:]
            if payload == b"rdy":
                # Hub says it's ready for the next command
                ready_event.set()
            else:
                print("Received:", payload)
        else:
            # Helpful debug if something odd comes back
            print("RX (no 0x01 header):", data)

    # ---------- BLE SCAN ----------
    print(f"Try to find device: {HUB_NAME}")

    device = None
    while device is None:
        device = await BleakScanner.find_device_by_name(HUB_NAME)

        if device is None:
            print(f"Hub '{HUB_NAME}' not found. Retrying...")
            await asyncio.sleep(1)  # prevent busy-loop scanning

    print(f"Found hub: {device}")

    # ---------- CONNECT ----------
    async with BleakClient(device, handle_disconnect) as client:

        # ---- Serial / sensor helpers ----
        async def get_sensor_data(arduino):
            try:
                return await asyncio.wait_for(
                    asyncio.to_thread(arduino.get_arduino),
                    timeout=1
                )
            except asyncio.TimeoutError:
                return -1
            except Exception as e:
                print(f"[Sensor] error: {e!r}")
                return -1

        async def flush_sensor_buffer(duration: float = 1.0):
            """
            Drain the Arduino serial buffer for `duration` seconds,
            so we don't start with 20 seconds of stale readings.
            """
            print(f"[Sensor] Flushing sensor buffer for {duration} s...")
            loop = asyncio.get_running_loop()
            end = loop.time() + duration
            while loop.time() < end:
                await get_sensor_data(arduino)
                # Don’t spam the port too hard
                await asyncio.sleep(0.01)
            print("[Sensor] Flush done, starting with fresh data.")

        # ---- BLE send helper ----
        async def send(data: bytes):
            """
            Send 4-byte ASCII command to hub stdin, waiting for 'rdy' first.
            """
            print("Debug 1 before ready_event.wait()")
            await ready_event.wait()     # wait until hub says 'rdy'
            print("Debug 2")
            ready_event.clear()

            await client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + data,  # prepend "write stdin" command (0x06)
                response=True
            )

        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)

        # Tell user to start program on the hub.
        print("Start the program on the hub now with the button.")

        # 🔴 Wait for the FIRST 'rdy' so we know hub program is running.
        print("Waiting for first 'rdy' from hub...")
        await ready_event.wait()
        # DO NOT clear here: let the first send() consume it.
        print("Got first 'rdy' from hub.")

        # 🔴 Flush old Arduino readings so we don't act on queued data.
        await flush_sensor_buffer(duration=1.0)

        random_number = np.random.randint(0, 4)
        inp = direction[random_number] + '050'

        while inp != "bye":
            # Read raw sensor value
            raw = await get_sensor_data(arduino)
            print("[LiDAR raw]:", raw)

            try:
                lidar_state = int(raw)
            except (TypeError, ValueError):
                lidar_state = -1

            print("[LiDAR int]:", lidar_state)

            if lidar_state == 1:
                inp = 'f' + "000"
                print("Command before send: '{inp}'".format(inp=inp), type(inp))
                await send(inp.encode('utf-8'))
                print("Command after send: '{inp}'".format(inp=inp))
                await asyncio.sleep(0.02)

                random_number = np.random.randint(0, 4)
                random_power = str(np.random.randint(25, 100)).zfill(3)

            elif lidar_state == 0:
                inp = direction[random_number] + "100"
                print("Command before send: '{inp}'".format(inp=inp), type(inp))
                await send(inp.encode('utf-8'))
                print("Command after send: '{inp}'".format(inp=inp))
                await asyncio.sleep(0.02)
                print(".", end="", flush=True)
                random_number = np.random.randint(0, 4)
                random_power = str(np.random.randint(25, 100)).zfill(3)

            elif lidar_state == -1:
                # timeout/error: just wait, don't send
                inp = direction[random_number] + "000"
                print("Command before send (no send): '{inp}'".format(inp=inp), type(inp))
                print("Command after send (no send): '{inp}'".format(inp=inp))
                await asyncio.sleep(0.02)

            else:
                # some other state: drive forward at 100
                inp = "f" + "100"
                print("Command before send: '{inp}'".format(inp=inp), type(inp))
                await send(inp.encode('utf-8'))
                print("Command after send: '{inp}'".format(inp=inp))
                await asyncio.sleep(0.02)
                print(".", end="", flush=True)
                random_number = np.random.randint(0, 4)

        # Send a message to indicate stop.
        await send(b"bye")

    # Hub disconnects here when async with block exits.

# Run the main async program.
if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())
