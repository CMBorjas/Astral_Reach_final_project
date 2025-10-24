# Astral Reach — Final Project

This repository contains the components for the Astral Reach robotics project. It is split into multiple modules so you can develop, test and run each subsystem independently:

- `Arduino_module/` — Arduino firmware and sketches
- `Lego_car_module/` — (documentation) Lego car related code
- `lidar_module/` — Lidar reading, parsing and visualisation (Python)
- `rasberry_pi_module/` — Raspberry Pi integration and control scripts

This README provides an overview of each module, setup instructions, and how to run the lidar visualiser which is the primary runnable component in this repo.

## Repository layout

- Arduino_module/
	- `main.ino` — Arduino sketch for the microcontroller
	- `README.md` — Arduino-specific notes
- Lego_car_module/
	- `README.md` — Notes for the Lego car module
- lidar_module/
	- `main.py` — Python visualiser that reads LD19 packets from the LIDAR and plots them
	- `CalcLidarData.py` — packet parsing and angle/distance extraction
	- `requirements.txt` — Python dependencies for the lidar module (if present)
- rasberry_pi_module/
	- `Ar2Pi.py`, `control.py` — Pi-side scripts and integration helpers

## Key notes

- The lidar parser (`lidar_module/CalcLidarData.py`) outputs angles in both degrees (`Degree_angle`) and radians (`Angle_i`).
- The lidar visualiser (`lidar_module/main.py`) now limits the displayed field-of-view (FOV) to 120° (centered around 0°). If you need full 360° behaviour, change the `FOV_DEG` constant in that file.

## Requirements

- Python 3.8+ (tested with 3.8–3.11)
- matplotlib
- pyserial

There is a `requirement.txt` at the repo root and `lidar_module/requirements.txt` — prefer the lidar-specific file when running the lidar visualiser.

## Setup (Windows — PowerShell)

1. Create and activate a virtual environment (recommended):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install lidar module dependencies (from the lidar module folder):

```powershell
cd lidar_module
pip install -r requirements.txt
```

If the `requirements.txt` in `lidar_module/` is missing, install the minimal deps directly:

```powershell
pip install matplotlib pyserial
```

## Running the Lidar visualiser

1. Edit `lidar_module/main.py` and set the `com_port` variable to the correct serial port for your platform.
	 - Windows example: `com_port = "COM3"`
	 - Linux example: `com_port = "/dev/ttyUSB0"`
	 - macOS example: `com_port = "/dev/tty.usbserial-XXXX"`

2. Run the visualiser from the `lidar_module` directory:

```powershell
python .\main.py
```

3. Controls:
	 - Press `e` (lowercase) in the matplotlib window to exit.

Notes:
- The visualiser expects LD19-style packets; the parser lives in `CalcLidarData.py`.
- The plotted FOV is controlled by the `FOV_DEG` constant in `main.py` (currently set to `120`). The script filters parsed points so only those within ±60° of 0° are displayed.

## Arduino module

See `Arduino_module/README.md` for flashing instructions and wiring notes. Typical workflow:

1. Open `Arduino_module/main.ino` in the Arduino IDE
2. Select board and COM port
3. Upload

## Raspberry Pi module

See `rasberry_pi_module/README.md` (if present) for Pi-specific setup. The `rasberry_pi_module` contains integration scripts for bridging sensors and actuators to higher-level control code.

## Lego car module

See `Lego_car_module/README.md` for details on that subsystem.

## Troubleshooting

- If you see no data in the visualiser, confirm the serial port and baud rate in `main.py` match your device. Default baudrate used in the script is 230400.
- If parsing fails, check the LD19 packet format and confirm wiring and power to the lidar.

## Contributing

If you want to extend this project:

1. Fork the repo
2. Create a branch for your feature
3. Submit a PR describing your changes

Please include testing steps in PR descriptions and keep changes scoped to one logical feature per PR.

## License & Contact

This repository does not include a license file. Add one if you intend to open-source the code. For questions, contact the maintainers or open an issue in the repository.

---

Last updated: October 24, 2025
