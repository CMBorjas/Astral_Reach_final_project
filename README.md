# Astral Reach — Final Project

This repository contains the Astral Reach final project: a multi-module robotics system combining an Arduino controller, a LEGO car module, a LiDAR processing module, and Raspberry Pi integration for higher-level control and communication.

## Overview

- **Purpose:** Demonstrate an integrated robotics stack that reads LiDAR data, runs control logic on a Raspberry Pi, interacts with an Arduino for low-level actuation, and includes a Lego car module for mobility experiments.
- **Languages & tools:** Python, Arduino (C++), shell; uses common libraries listed per module.

## Repository Structure

```
README.md
requirement.txt
Arduino_module/
	main.ino
	README.md
Lego_car_module/
	README.md
lidar_module/
	CalcLidarData.py
	main.py
	README.md
	requirements.txt
rasberry_pi_module/
	Ar2Pi.py
	control.py
```

## Modules

- `Arduino_module/` — Arduino sketch(s) for motor and sensor control (`main.ino`). Use the Arduino IDE or `arduino-cli` to upload.
- `Lego_car_module/` — Documentation and files specific to the LEGO car chassis and wiring.
- `lidar_module/` — LiDAR processing scripts. Key files: `main.py` (runner) and `CalcLidarData.py` (processing utilities).
- `rasberry_pi_module/` — Raspberry Pi scripts for bridging sensors, higher-level control, and communication with the Arduino.

## Requirements

- System: Linux (development), Raspberry Pi (deployment) recommended for the Pi module.
- Python 3.8+ for Python modules.
- Install Python dependencies:

```bash
# Root (general deps if any)
pip install -r requirement.txt

# LiDAR module deps
pip install -r lidar_module/requirements.txt
```

Note: some modules may not have a `requirements.txt`; install dependencies listed in their `README.md` if present.

## Quick Start

1. Install dependencies (see Requirements above).
2. Connect hardware (Arduino, LiDAR, motors) and note serial ports.
3. Start the LiDAR processing (example):

```bash
cd lidar_module
python3 main.py
```

4. Run Raspberry Pi control scripts (on the Pi):

```bash
cd rasberry_pi_module
python3 control.py
# or
python3 Ar2Pi.py
```

5. Upload Arduino sketch using Arduino IDE or CLI:

```bash
# Using arduino-cli (example)
arduino-cli compile --fqbn <board_fqbn> Arduino_module
arduino-cli upload -p /dev/ttyUSB0 --fqbn <board_fqbn> Arduino_module
```

Replace `/dev/ttyUSB0` and `<board_fqbn>` with your device port and board FQBN.

## Module Notes

- LiDAR: `CalcLidarData.py` contains helper functions to parse and preprocess LiDAR frames. Confirm the LiDAR serial port and baud rate inside `main.py` before running.
- Raspberry Pi: `Ar2Pi.py` and `control.py` expect specific serial/USB mappings; update the port paths and any GPIO pin numbers to match your hardware.
- Arduino: Verify motor driver wiring and power requirements before powering motors.

## Troubleshooting

- Serial port not found: run `ls /dev/tty*` before/after plugging devices to identify new device names.
- Permission errors on serial ports: add your user to the `dialout` group or run with `sudo` (preferred: add user to group):

```bash
sudo usermod -a -G dialout $USER
newgrp dialout
```

## Contributing

If you want to contribute:

- Open an issue describing the feature or bug.
- Make a branch: `git checkout -b feat/your-feature`.
- Send a PR with a clear description and testing steps.

## Next Steps / Suggestions

- Add per-module examples and small recorded datasets for LiDAR tests.
- Add automated tests for Python modules (unit tests for `CalcLidarData.py`).
- Provide a wiring diagram and a parts list (BOM) in each hardware module folder.

---
If you'd like, I can also:

- Add wiring diagrams and a parts list.
- Create example run scripts to start all needed modules together.
- Add unit tests for `lidar_module` functions.

Contact: Project owner or check module READMEs for module-specific maintainers.

