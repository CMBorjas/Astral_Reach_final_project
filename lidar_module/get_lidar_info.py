import serial
from CalcLidarData import CalcLidarData

def detect_close_object(com_port="/dev/tty.usbserial-0001", fov_deg=0.5, threshold=0.1):
    """
    Parameters:
        com_port (str): Serial port path, e.g. "/dev/tty.usbserial-0001"
        fov_deg (float): Field of view centered at 0°, in degrees
        threshold (float): Distance threshold in meters (default 0.1)
    """
    ser = serial.Serial(
        port=com_port,
        baudrate=230400,
        timeout=1.0,
        bytesize=8,
        parity='N',
        stopbits=1
    )

    tmpString = ""
    angles = []
    distances = []
    flag2c = False

    try:
        while True:
            b = ser.read()
            if not b:
                continue

            tmpInt = int.from_bytes(b, 'big')

            if tmpInt == 0x54:
                tmpString += b.hex() + " "
                flag2c = True
                continue

            elif tmpInt == 0x2c and flag2c:
                tmpString += b.hex()

                if not len(tmpString[0:-5].replace(' ', '')) == 90:
                    tmpString = ""
                    flag2c = False
                    continue

                # Decode Lidar data
                lidarData = CalcLidarData(tmpString[0:-5])

                # Process angles and distances
                for deg, ang, dist in zip(lidarData.Degree_angle,
                                          lidarData.Angle_i,
                                          lidarData.Distance_i):
                    # Normalize to [-180, 180)
                    diff = ((deg - 0 + 180) % 360) - 180
                    if abs(diff) <= (fov_deg / 2.0):
                        angles.append(ang)
                        distances.append(dist)

                        # Check threshold
                        if dist < threshold:
                            ser.close()
                            return 1
                        else:
                            return 0

                # Reset for next packet
                tmpString = ""
                flag2c = False
                angles.clear()
                distances.clear()

            else:
                tmpString += b.hex() + " "
                flag2c = False

    except KeyboardInterrupt:
        ser.close()
        print("Stopped by user.")
        return 0
