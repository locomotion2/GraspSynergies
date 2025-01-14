"""
Serial Data Recorder for the Myobock Sensor Board (8 sensors)

Description:
    This script creates a Tkinter-based GUI application to record sensor data from a serial port
    (Arduino Board). It continuously reads incoming data, parses it, and saves it to a timestamped CSV file (timestamp in ms accuracy).

Features:
    - Establishes a serial connection to COMX at 115200 baud rate.
    - Provides Start and Stop buttons to control data recording.
    - Saves sensor data with 8 sensor values into a CSV file with a timestamped filename.
    - Handles exceptions related to serial communication and file operations.
    - Runs a separate thread to continuously read and record serial data without freezing the GUI.
"""

import serial
import csv
from datetime import datetime
import threading
import tkinter as tk
from tkinter import messagebox
import time  

# Set up the serial connection
try:
    ser = serial.Serial('COM9', 115200)  # Match baud rate with Arduino and check port number, i.e. COM4 or COM9 etc.
    ser.flush()
except serial.SerialException as e:
    print(f"Error: {e}")
    exit()

recording = False
csv_file = None
csv_writer = None

def start_recording():
    global csv_file, csv_writer, recording
    if not recording:
        # Create a timestamped filename with milliseconds
        start_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.%f")[:-3]  # Truncate to milliseconds
        filename = f'C:\\Users\\inreh\\MA_Patrick\\Myobock Sensors\\Myobock Data Recordings\\sensor_data_{start_time}.csv'

        # Open the CSV file
        try:
            csv_file = open(filename, mode='w', newline='')
            csv_writer = csv.writer(csv_file)
            # Write the CSV header
            csv_writer.writerow(["Sensor1", "Sensor2", "Sensor3", "Sensor4", "Sensor5", "Sensor6", "Sensor7", "Sensor8"])
            print(f"Recording started. Data will be saved to: {filename}")
            recording = True
            record_button.config(state=tk.DISABLED)
            stop_button.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("Error", f"Error creating file: {e}")

def stop_recording():
    global csv_file, recording
    if csv_file:
        try:
            csv_file.close()
            print("Recording stopped and file closed.")
        except Exception as e:
            messagebox.showerror("Error", f"Error closing file: {e}")
        csv_file = None
        recording = False
        record_button.config(state=tk.NORMAL)
        stop_button.config(state=tk.DISABLED)

def record_data():
    global recording
    while True:
        if recording and ser.in_waiting > 0:
            # Read the raw data from the serial port
            raw_data = ser.readline()

            # Decode the serial data
            line = raw_data.decode('utf-8', errors='ignore').strip()

            # Split the data into sensor values and write to CSV
            sensor_data = line.split(',')
            if len(sensor_data) == 8:  # Ensure correct number of sensor values
                csv_writer.writerow(sensor_data)
                print(f"Data recorded: {sensor_data}")
            else:
                print(f"Unexpected data format: {line}")
        # Small delay to match Arduino's 1ms delay
        time.sleep(0.001)

# Start the recording thread to continuously read from the serial port
data_thread = threading.Thread(target=record_data)
data_thread.daemon = True  # Ensure the thread will exit when the main program exits
data_thread.start()

# Create the tkinter GUI
root = tk.Tk()
root.title("Serial Data Recorder")

# Create a frame for the buttons
frame = tk.Frame(root)
frame.pack(pady=20)

# Create the Start and Stop buttons
record_button = tk.Button(frame, text="Start Recording", command=start_recording, width=20, height=2)
record_button.pack(side=tk.LEFT, padx=10)

stop_button = tk.Button(frame, text="Stop Recording", command=stop_recording, width=20, height=2, state=tk.DISABLED)
stop_button.pack(side=tk.RIGHT, padx=10)

# Run the GUI loop
root.mainloop()

# Ensure the serial port is closed when the window is closed
ser.close()
