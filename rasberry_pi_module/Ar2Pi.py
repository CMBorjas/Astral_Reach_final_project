import serial
import time

def most_common(lst): #https://stackoverflow.com/questions/1518522/find-the-most-common-element-in-a-list
    return max(set(lst), key=lst.count)


ser = serial.Serial('/dev/tty.usbmodem1101', 9600, timeout=1)
# time.sleep(2)  # wait for Arduino to reset
try: 
    while True:
        reply_list = []
        for each_reply in range(10):
            each_reply = ser.readline().decode().strip()
            reply_list.append(each_reply)
        reply = most_common(reply_list)
        if reply:
            reply = int(reply)
            print("Arduino says:", reply)
            if reply < 10:
                cmd = "ON"
                ser.write((cmd + "\n").encode())
            elif reply > 500:
                cmd = "ON"
                ser.write((cmd + "\n").encode())
                time.sleep(0.1)
                cmd = "OFF"
                ser.write((cmd + "\n").encode())
            else:
                cmd = "OFF"
                ser.write((cmd + "\n").encode())
except KeyboardInterrupt:
    time.sleep(0.1)
    cmd = "OFF"
    ser.write((cmd + "\n").encode())
    ser.close()
    print("serial connection disconnected")
# ser.close()

