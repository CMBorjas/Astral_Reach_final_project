import serial
import time

def most_common(lst):
    """Return the most common element in a list."""
    return max(set(lst), key=lst.count)

class ArduinoReader:
    def __init__(self, port='/dev/tty.usbmodem1101', baud=9600, timeout=1):
        self.ser = serial.Serial(port, baud, timeout=timeout)
        # time.sleep(2)  # Uncomment if Arduino requires reset wait

    def read_value(self):
        reply_list = []
        for _ in range(10):
            raw = self.ser.readline().decode().strip()
            reply_list.append(raw)

        common = most_common(reply_list)
        if common:
            return int(common)
        return None

    def send_cmd(self, cmd):
        """Send a command string with newline."""
        self.ser.write((cmd + "\n").encode())

    def get_arduino(self):
        """Main logic to read sensor values and send commands."""
        try:
            while True:
                value = self.read_value()
                if value is None:
                    continue

                if value < 20:
                    self.send_cmd("ON")
                    return 1

                elif value > 500:
                    self.send_cmd("ON")
                    time.sleep(0.1)
                    self.send_cmd("OFF")
                    return 2

                else:
                    self.send_cmd("OFF")
                    return 3

        except KeyboardInterrupt:
            time.sleep(0.1)
            self.send_cmd("OFF")
            print("serial connection interrupted")
