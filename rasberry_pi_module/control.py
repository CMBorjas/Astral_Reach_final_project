# SPDX-License-Identifier: MIT
# Copyright (c) 2020 Henrik Blidh
# Copyright (c) 2022-2023 The Pybricks Authors

import asyncio
import time
from contextlib import suppress
from typing import Optional, Tuple

from bleak import BleakClient, BleakScanner
import serial
from serial import SerialException

PYBRICKS_COMMAND_EVENT_CHAR_UUID = "c5f50002-8280-46da-89f4-6d8051e4aeef"
HUB_NAME = "Pybricks Hub"

SERIAL_PORT = "/dev/tty.usbmodem1101"  # <-- change to your actual COM/tty port
SERIAL_BAUDRATE = 9600
SERIAL_TIMEOUT = 1
SERIAL_SAMPLE_SIZE = 10

CLOSE_DISTANCE_CM = 10
FAR_DISTANCE_CM = 500


def most_common(values):
    return max(set(values), key=values.count) if values else None


def format_drive_command(direction: str, power: int) -> str:
    clamped = max(0, min(power, 100))
    return f"{direction}{clamped:03d}"


class ArduinoBridge:
    def __init__(self, port: str, baudrate: int, timeout: float, sample_size: int):
        self.serial = serial.Serial(port, baudrate, timeout=timeout)
        self.sample_size = sample_size

    def close(self) -> None:
        if self.serial and self.serial.is_open:
            self.serial.close()

    def poll_command(self) -> Optional[Tuple[int, str]]:
        readings = self._collect_samples()
        if not readings:
            return None

        sample = most_common(readings)
        if sample is None:
            return None

        try:
            distance = int(float(sample))
        except ValueError:
            return None

        self._update_led(distance)
        return distance, self._distance_to_command(distance)

    def _collect_samples(self):
        values = []
        for _ in range(self.sample_size):
            raw = self.serial.readline().decode(errors="ignore").strip()
            if raw:
                values.append(raw)
        return values

    def _update_led(self, distance: int) -> None:
        if distance < CLOSE_DISTANCE_CM:
            self._write("ON")
        elif distance > FAR_DISTANCE_CM:
            self._write("ON")
            time.sleep(0.1)
            self._write("OFF")
        else:
            self._write("OFF")

    def _distance_to_command(self, distance: int) -> str:
        if distance < CLOSE_DISTANCE_CM:
            return format_drive_command("b", 50)
        if distance > FAR_DISTANCE_CM:
            return format_drive_command("f", 100)
        return format_drive_command("f", 50)

    def _write(self, payload: str) -> None:
        self.serial.write((payload + "\n").encode())


async def drive_with_arduino(send):
    try:
        bridge = ArduinoBridge(
            SERIAL_PORT,
            SERIAL_BAUDRATE,
            SERIAL_TIMEOUT,
            SERIAL_SAMPLE_SIZE,
        )
    except SerialException as exc:
        print(f"Unable to open serial port {SERIAL_PORT}: {exc}")
        return

    try:
        while True:
            try:
                result = await asyncio.to_thread(bridge.poll_command)
            except SerialException as exc:
                print(f"Serial connection error: {exc}")
                break

            if not result:
                continue

            distance, command = result
            if not command:
                continue

            print(f"Distance {distance} cm -> '{command}'")

            try:
                await send(command.encode("utf-8"))
            except Exception as exc:
                print(f"Failed to send '{command}' to hub: {exc}")
                await asyncio.sleep(0.5)
    finally:
        bridge.close()


async def main():
    main_task = asyncio.current_task()

    def handle_disconnect(_):
        print("Hub was disconnected.")
        if not main_task.done():
            main_task.cancel()

    ready_event = asyncio.Event()

    def handle_rx(_, data: bytearray):
        if not data:
            return

        if data[0] == 0x01:
            payload = data[1:]
            if payload == b"rdy":
                ready_event.set()
            else:
                try:
                    message = payload.decode()
                except UnicodeDecodeError:
                    message = repr(payload)
                print("Received:", message)

    print(f"Try to Find Device: {HUB_NAME}")
    device = await BleakScanner.find_device_by_name(HUB_NAME)

    if device is None:
        print(f"could not find hub with name: {HUB_NAME}")
        return

    async with BleakClient(device, handle_disconnect) as client:

        async def send(data: bytes, *, wait_for_ready: bool = True):
            if wait_for_ready:
                await ready_event.wait()
                ready_event.clear()

            await client.write_gatt_char(
                PYBRICKS_COMMAND_EVENT_CHAR_UUID,
                b"\x06" + data,
                response=True,
            )

        await client.start_notify(PYBRICKS_COMMAND_EVENT_CHAR_UUID, handle_rx)
        print("Start the program on the hub now with the button.")

        sensor_task = asyncio.create_task(drive_with_arduino(send))

        try:
            await sensor_task
        except asyncio.CancelledError:
            pass
        finally:
            sensor_task.cancel()
            with suppress(asyncio.CancelledError):
                await sensor_task
            with suppress(Exception):
                await send(b"bye", wait_for_ready=False)


if __name__ == "__main__":
    with suppress(asyncio.CancelledError):
        asyncio.run(main())