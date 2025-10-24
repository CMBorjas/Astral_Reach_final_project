try:
    import serial
except ImportError:
    raise ImportError("Module 'serial' (pyserial) not found. Activate the project venv or install pyserial:\n" \
                      "  .\\.venv\\Scripts\\Activate.ps1\n" \
                      "  python -m pip install pyserial")

# Ensure the imported package provides the Serial class (detect conflicting 'serial' packages)
if not hasattr(serial, 'Serial'):
    raise ImportError("Imported 'serial' package does not expose 'Serial'.\n" \
                      "A conflicting package named 'serial' may be installed.\n" \
                      "Fix: pip uninstall serial && pip install --force-reinstall pyserial")
from CalcLidarData import CalcLidarData
import matplotlib.pyplot as plt
import math

# Create a figure with matplotlib's pyplot
# Figure can be understood as a canvas, on which we can use to draw many charts
fig = plt.figure(figsize=(1,1))


# Create a subplot on the Figure
# At coordinates 111, i.e. (1, 1) and has index = 1 on the figure
# Polar coordinate system, circular, often used in radar maps
ax = fig.add_subplot(111, projection='polar')
# Title for the chart
ax.set_title('Lidar LD19 (exit: Key E)',fontsize=18)

# Field of view to display (degrees). Set to 120 for a 120° vision cone.
FOV_DEG = 120

# Serial port for connection
com_port = "COM4"

# Create an event for pyplot
# 'key_press_event': event when a key is pressed
# A function is triggered with the event
# Press E to exit
plt.connect('key_press_event', lambda event: exit(1) if event.key == 'e' else None)


ser = serial.Serial(port=com_port,
                    baudrate=230400,
                    timeout=1.0,
                    bytesize=8,
                    parity='N',
                    stopbits=1)


tmpString = ""
lines = list()
angles = list()
distances = list()

i = 0
while True:
    loopFlag = True
    flag2c = False

    if (i % 40 == 39):
        if ('line' in locals()):
            line.remove()

        # Draw scatter plot (point chart)
            # Often represents the correlation between 2 values, here is angle + distance
            # c: color, s: size of points
        print(len(angles))
        line = ax.scatter(angles, distances, c="blue", s=5)
        ax.set_theta_offset(math.pi / 2)
        ax.set_ylim(0, 1.0)
        plt.pause(0.01)
        angles.clear()
        distances.clear()

        i = 0


    while loopFlag:
        b = ser.read()
        tmpInt = int.from_bytes(b, 'big')

        # 0x54, indicating the beginning of the data packet (LD19 document)
        if (tmpInt == 0x54):
            tmpString += b.hex() + " "
            flag2c = True
            continue

        # 0x2c: fixed value of VerLen (LD19 document)
        elif (tmpInt == 0x2c and flag2c):
            tmpString += b.hex()


            if (not len(tmpString[0:-5].replace(' ','')) == 90):
                tmpString = ""
                loopFlag = False
                flag2c = False
                continue

            # After reading a full Lidar data packet, it will have a size of 90, take the string and pass it to the CalcLidarData() function
            lidarData = CalcLidarData(tmpString[0:-5])
            # Get values of angle and distance
            # Filter points to the configured field-of-view (centered at 0°)
            # lidarData.Degree_angle is in degrees; lidarData.Angle_i is in radians
            for deg, ang, dist in zip(lidarData.Degree_angle, lidarData.Angle_i, lidarData.Distance_i):
                # Normalize to range [-180,180)
                diff = ((deg - 0 + 180) % 360) - 180
                if abs(diff) <= (FOV_DEG / 2.0):
                    angles.append(ang)
                    distances.append(dist)

            # Debug prints (degrees and distances). Prints the filtered values.
            print("Filtered Angles (deg):", [d for d in lidarData.Degree_angle if abs(((d - 0 + 180) % 360) - 180) <= (FOV_DEG / 2.0)])
            print("Filtered Distances:", distances[-12:])

            #print(distances)

            tmpString = ""
            loopFlag = False
        else:
            tmpString += b.hex()+ " "

        flag2c = False

    i += 1

ser.close()