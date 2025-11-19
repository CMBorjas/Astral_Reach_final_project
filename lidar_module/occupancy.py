#!/usr/bin/env python3
"""
Simple occupancy grid visualizer for LD19-style LiDAR scans in this repo.

Usage:
  python3 occupancy.py --port /dev/ttyUSB0 --baud 230400

The script reads packets the same way `main.py` does (0x54 start, 0x2c VerLen),
parses them with `CalcLidarData`, converts polar measurements to Cartesian, and
updates a 2D occupancy grid. Cells along a ray up to the measured distance are
marked free and the hit cell is marked occupied. Visualization updates live.

Requirements: numpy, matplotlib, pyserial
"""

import argparse
import math
import time
from CalcLidarData import CalcLidarData

import numpy as np
import matplotlib.pyplot as plt
import serial


class OccupancyGrid:
    def __init__(self, size_m=10.0, resolution=0.05):
        self.size_m = float(size_m)
        self.res = float(resolution)
        self.width = int(np.ceil(self.size_m / self.res))
        if self.width % 2 == 0:
            self.width += 1
        self.grid = np.zeros((self.width, self.width), dtype=np.int8)
        self.origin = (self.width // 2, self.width // 2)

    def world_to_idx(self, x, y):
        half = self.size_m / 2.0
        ix = int((x + half) / self.res)
        iy = int((y + half) / self.res)
        if 0 <= ix < self.width and 0 <= iy < self.width:
            return ix, iy
        return None

    def mark_free_along_ray(self, angle_rad, distance_m):
        # sample along the ray from 0 to distance_m - small_eps
        if distance_m <= 0:
            return
        step = self.res / 2.0
        # If distance is extremely small, nothing to mark as free
        max_t = max(0.0, distance_m - (self.res / 4.0))
        if max_t <= 0:
            return
        t_vals = np.arange(0.0, max_t, step)
        for t in t_vals:
            x = t * math.cos(angle_rad)
            y = t * math.sin(angle_rad)
            idx = self.world_to_idx(x, y)
            if idx:
                # 1 == free, but don't overwrite occupied (2)
                if self.grid[idx[1], idx[0]] != 2:
                    self.grid[idx[1], idx[0]] = 1

    def mark_occupied(self, angle_rad, distance_m):
        x = distance_m * math.cos(angle_rad)
        y = distance_m * math.sin(angle_rad)
        idx = self.world_to_idx(x, y)
        if idx:
            # 2 == occupied
            self.grid[idx[1], idx[0]] = 2

    def as_display(self):
        # return an image where: unknown=0.5 gray, free=1.0 white, occ=0.0 black
        img = np.ones((self.width, self.width), dtype=np.float32) * 0.5
        img[self.grid == 1] = 1.0
        img[self.grid == 2] = 0.0
        return img


def run_serial(port, baud, grid_size, resolution, refresh=0.2):
    ser = serial.Serial(port=port, baudrate=baud, timeout=1.0,
                        bytesize=8, parity='N', stopbits=1)

    grid = OccupancyGrid(size_m=grid_size, resolution=resolution)

    fig, ax = plt.subplots(figsize=(6, 6))
    im = ax.imshow(grid.as_display(), cmap='gray_r', origin='lower',
                   extent=[-grid_size/2, grid_size/2, -grid_size/2, grid_size/2])
    ax.set_title('Occupancy Grid (unknown=gray, free=white, occ=black)')
    plt.ion()
    plt.show()

    tmpString = ""
    i = 0
    last_draw = time.time()
    try:
        while True:
            loopFlag = True
            flag2c = False

            while loopFlag:
                b = ser.read()
                if not b:
                    # timeout
                    break
                tmpInt = int.from_bytes(b, 'big')

                if (tmpInt == 0x54):
                    tmpString = b.hex() + ' '
                    flag2c = True
                    continue

                elif (tmpInt == 0x2c and flag2c):
                    tmpString += b.hex()

                    if (not len(tmpString[0:-5].replace(' ','')) == 90):
                        tmpString = ""
                        loopFlag = False
                        flag2c = False
                        continue

                    lidarData = CalcLidarData(tmpString[0:-5])

                    angles = lidarData.Angle_i
                    distances = lidarData.Distance_i

                    for a, d in zip(angles, distances):
                        # angles are in radians already (CalcLidarData returns Angle_i)
                        # distances are in meters (CalcLidarData divides by 1000)
                        if d <= 0:
                            continue
                        grid.mark_free_along_ray(a, d)
                        grid.mark_occupied(a, d)

                    tmpString = ""
                    loopFlag = False
                else:
                    tmpString += b.hex() + ' '

                flag2c = False

            # update display at most every `refresh` seconds
            if time.time() - last_draw >= refresh:
                im.set_data(grid.as_display())
                ax.draw_artist(ax.patch)
                ax.draw_artist(im)
                fig.canvas.flush_events()
                last_draw = time.time()

    except KeyboardInterrupt:
        print('\nExiting and closing serial port')
    finally:
        ser.close()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--port', '-p', default='/dev/ttyUSB0', help='LiDAR serial port')
    p.add_argument('--baud', '-b', default=230400, type=int, help='baud rate')
    p.add_argument('--grid-size', default=10.0, type=float, help='grid width (meters)')
    p.add_argument('--resolution', default=0.05, type=float, help='meters per cell')
    p.add_argument('--refresh', default=0.2, type=float, help='visual refresh interval (s)')
    args = p.parse_args()

    run_serial(args.port, args.baud, args.grid_size, args.resolution, args.refresh)


if __name__ == '__main__':
    main()
