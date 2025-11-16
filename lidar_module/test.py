import get_lidar_info

port = "/dev/tty.usbserial-0001"
x = get_lidar_info.detect_close_object(port)
print(x)