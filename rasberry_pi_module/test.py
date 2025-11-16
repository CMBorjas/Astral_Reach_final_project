# import Ar2Pi

# arduino = Ar2Pi.ArduinoReader('/dev/tty.usbmodem101')

# while True:
#     result = arduino.get_arduino()
#     print(result)

# ===========================================================

from get_lidar_info import LidarDetector

det = LidarDetector(
    com_port="/dev/tty.usbserial-0001",
    fov_deg=360,
    threshold=0.1
)

result = det.detect()

if result == 1:
    print("Object very close!")
else:
    print("No nearby object.")
