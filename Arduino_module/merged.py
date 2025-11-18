import serial
import time

ARDUINO_PORT = "COM3"
BAUD_RATE = 9600

# Connect to Arduino
try:
    # Establish the connection
    ser = serial.Serial(ARDUINO_PORT, BAUD_RATE, timeout=2)
    print(f"Connected to Arduino on {ARDUINO_PORT}.")
    # Wait 2 seconds for the Arduino to reset after connection
    time.sleep(2)
except serial.SerialException as e:
    print(f"Error: Could not open port {ARDUINO_PORT}. {e}")
    print("Is the Arduino plugged in? Is the port correct?")
    exit()


def send_command(command):
    """Sends a command to the Arduino (e.g., "ON" or "OFF")."""
    # encode the string into bytes and add a newline '\n'
    # since Arduino is using readStringUntil('\n')
    ser.write(command.encode("utf-8") + b"\n")
    print(f"Sent command: {command}")


def read_data():
    """Reads a line of data (e.g., distance) from the Arduino."""
    if ser.in_waiting > 0:
        try:
            # Read a line, decode from bytes to string, and strip whitespace
            line = ser.readline().decode("utf-8").strip()
            if line:  # Make sure the line is not empty
                return line
        except Exception as e:
            print(f"Error reading from serial: {e}")
    return None


# Run program
try:
    print("Sending 'ON' command...")
    send_command("ON")
    time.sleep(3)

    print("Sending 'OFF' command...")
    send_command("OFF")
    time.sleep(1)

    print("\n--- Reading distance data for 5 seconds ---")
    start_time = time.time()
    while time.time() - start_time < 5:
        distance = read_data()
        if distance:
            print(f"Received from Arduino: {distance}")
        time.sleep(0.1)  # minimize cpu spam

except KeyboardInterrupt:
    print("\nExiting program.")
finally:
    # close the connection when done
    ser.close()
    print("Serial connection closed.")
