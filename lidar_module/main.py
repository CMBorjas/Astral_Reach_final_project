import serial
from CalcLidarData import CalcLidarData
import matplotlib.pyplot as plt
import math

# Create a Figure using matplotlib.pyplot
# A Figure is like a canvas where you can draw multiple plots
fig = plt.figure(figsize=(1,1))


# Create a plot on the Figure
# Subplot 111: i.e., a (1, 1) grid with index = 1 on the figure
# Polar coordinate system, commonly used for radar / circular plots
ax = fig.add_subplot(111, projection='polar')
# Title for the plot
ax.set_title('Lidar LD19 (exit: Key E)', fontsize=18)

# COM port for serial connection
com_port = "/dev/tty.usbserial-0001"

# Create an event for pyplot
# 'key_press_event': event when a key is pressed
# One function is triggered by the event
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

        # Draw scatter plot (point plot)
        # Typically represents the relationship between two values; here angle + distance
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

            # Sau khi đọc full 1 gói data Lidar sẽ có kích thước = 90, lấy string và đưa vào hàm CalcLidarData()
            lidarData = CalcLidarData(tmpString[0:-5])
            # Get giá trị của góc và distance
            angles.extend(lidarData.Angle_i)
            distances.extend(lidarData.Distance_i)
            print("Angles:", lidarData.Angle_i)
            print("Distances:", lidarData.Distance_i)

            #print(distances)

            tmpString = ""
            loopFlag = False
        else:
            tmpString += b.hex()+ " "

        flag2c = False

    i += 1

ser.close()