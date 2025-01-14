"""
EMG Data Acquisition and Real-Time Visualization

This script facilitates the acquisition of electromyography (EMG) data from multiple devices 
via a TCP socket connection. It performs the following key functions:

- **Configuration:** Sets up device parameters, including enabling specific devices, 
  selecting EMG modes, and defining the number of channels per device.
  
- **Data Acquisition:** Connects to the specified TCP server, sends configuration commands, 
  and continuously receives EMG data in real-time. It handles data processing, including 
  CRC8 checksum validation and conversion of raw bytes to meaningful voltage values.

- **Real-Time Plotting:** Utilizes a Tkinter-based GUI integrated with Matplotlib to display 
  live plots of selected EMG channels. The interface includes start and stop buttons to control 
  data recording.

- **Data Saving:** Upon stopping the recording, the script saves the acquired EMG data to both 
  `.npy` and `.csv` files with timestamped filenames for further analysis.

**Usage:**
1. Configure the device settings and network parameters as needed.
2. Run the script to launch the GUI.
3. Click "Start Recording" to begin data acquisition and visualization.
4. Click "Stop Recording" to end the session and save the data.

Ensure that the EMG devices are properly connected and the TCP server is accessible at the 
configured IP address and port before starting the recording.
"""

import datetime
import socket
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import struct
import tkinter as tk
from tkinter import messagebox
import threading
import queue
import time
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Function to calculate CRC8
def CRC8(Vector, Len):
    crc = 0
    j = 0

    while Len > 0:
        Extract = Vector[j]
        for i in range(8, 0, -1):
            Sum = crc % 2 ^ Extract % 2
            crc //= 2

            if Sum > 0:
                crc ^= 140
            Extract //= 2

        Len -= 1
        j += 1

    return crc

# Configuration parameters
TCPPort = 54320
OffsetEMG = 1000
PlotTime = 1  # Duration of data blocks in seconds

# Device configuration
DeviceEN = [0, 0, 0, 0, 1, 1] + [0]*10  # Enable devices 5 and 6
EMG = [1]*16
Mode = [0]*16
NumChan = [38]*4 + [70]*2 + [8]*10 

# Error checking
Error = any(DeviceEN[i] > 1 for i in range(16))
if Error:
    print("Error, set DeviceEN values equal to 0 or 1")
    exit()

Error = any(EMG[i] > 1 for i in range(16))
if Error:
    print("Error, set EMG values equal to 0 or 1")
    exit()

Error = any(Mode[i] > 3 for i in range(16))
if Error:
    print("Error, set Mode values between 0 and 3")
    exit()

SizeComm = sum(DeviceEN)

sampFreq = 2000  # Hz
TotNumChan = 0
TotNumByte = 0
ConfStrLen = 1
ConfString = [0]*18

ConfString[0] = SizeComm * 2 + 1

DeviceStartIndex = [0]*16
ChanStartIndex = 0

for i in range(16):
    if DeviceEN[i] == 1:
        DeviceStartIndex[i] = ChanStartIndex  # Record starting index
        ConfString[ConfStrLen] = (i * 16) + EMG[i] * 8 + Mode[i] * 2 + 1

        NumChannels = NumChan[i]

        TotNumChan += NumChannels
        ChanStartIndex += NumChannels

        if EMG[i] == 1:
            TotNumByte += NumChannels * 2
        else:
            TotNumByte += NumChannels * 3

        if EMG[i] == 1:
            sampFreq = 2000

        ConfStrLen += 1

SyncStatChan = list(range(TotNumChan, TotNumChan + 6))
TotNumChan += 6
TotNumByte += 12

ConfString[ConfStrLen] = 0  # Placeholder for CRC8 calculation

# Calculate CRC8 and update ConfString
ConfString[ConfStrLen] = CRC8(ConfString, ConfStrLen)
ConfStrLen += 1

# Global variables
recording = False
data_thread = None
start_time = None
emg_data = []
data_queue = queue.Queue()

# Create the main window
root = tk.Tk()
root.title("EMG Data Acquisition")

# Functions for GUI
def start_recording():
    global recording, data_thread, emg_data
    recording = True
    emg_data = []  # Reset data
    start_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.NORMAL)
    data_thread = threading.Thread(target=data_acquisition)
    data_thread.start()
    print("Data acquisition thread started")

def stop_recording():
    global recording
    recording = False
    start_button.config(state=tk.NORMAL)
    stop_button.config(state=tk.DISABLED)
    data_thread.join()
    save_data()

def data_acquisition():
    global recording, start_time, emg_data
    try:
        # Open the TCP socket
        tcpSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('192.168.76.1', TCPPort)
        print(f"Attempting to connect to {server_address}")
        tcpSocket.connect(server_address)
        print("Connected to Socket!")

        # Get the current timestamp with millisecond precision
        start_time = datetime.now()

        # Send the configuration to SyncStation
        StartCommand = ConfString[0:ConfStrLen]
        packed_data = struct.pack('B' * ConfStrLen, *StartCommand)

        tcpSocket.sendall(packed_data)
        print("Start Command sent")
        print(StartCommand)

        blockSize = TotNumByte * int(sampFreq * PlotTime)  # Total bytes per block
        # Set a timeout for the socket
        tcpSocket.settimeout(30)  # Increased timeout to 30 seconds

        while recording:
            data_buffer = b""

            while len(data_buffer) < blockSize:
                if not recording:
                    break
                try:
                    data_temp = tcpSocket.recv(blockSize - len(data_buffer))
                    if data_temp:
                        print(f"Received {len(data_temp)} bytes")
                    else:
                        print("No data received. Possible disconnection.")
                        recording = False
                        break
                except socket.timeout:
                    print("Socket timeout. Stopping data acquisition.")
                    recording = False
                    break
                except Exception as e:
                    print(f"Socket error: {e}")
                    recording = False
                    break
                data_buffer += data_temp

            if not recording or len(data_buffer) == 0:
                break

            # Process data
            TempArray = np.frombuffer(data_buffer, dtype=np.uint8)
            # Each sample consists of TotNumByte bytes
            num_samples = len(TempArray) // TotNumByte
            if num_samples == 0:
                print("No complete samples received.")
                continue  # Skip if no complete samples
            print(f"Processing {num_samples} samples")

            Temp = np.reshape(TempArray[:num_samples * TotNumByte], (num_samples, TotNumByte))

            # Initialize data array for this block
            data_block = np.zeros((TotNumChan, num_samples))

            TempIndex = 0  # Index to keep track of position in Temp

            for DevId in range(16):
                if DeviceEN[DevId] == 1:
                    num_channels = NumChan[DevId]

                    if EMG[DevId] == 1:
                        num_bytes_per_sample = num_channels * 2
                        data_bytes = Temp[:, TempIndex:TempIndex + num_bytes_per_sample]
                        TempIndex += num_bytes_per_sample

                        # Convert bytes to int16
                        data_int16 = data_bytes.reshape(num_samples, num_channels, 2)
                        data_int16 = data_int16[:, :, 0] * 256 + data_int16[:, :, 1]
                        data_int16[data_int16 >= 32768] -= 65536
                        data_int16 = data_int16.astype(np.int16)

                        # Convert to mV (adjust scaling factor if necessary)
                        data_mV = data_int16.T * 0.000286

                        start_idx = DeviceStartIndex[DevId]
                        data_block[start_idx:start_idx + num_channels, :] = data_mV

                    else:
                        num_bytes_per_sample = num_channels * 3
                        data_bytes = Temp[:, TempIndex:TempIndex + num_bytes_per_sample]
                        TempIndex += num_bytes_per_sample

                        # Convert bytes to int32
                        data_int32 = data_bytes.reshape(num_samples, num_channels, 3)
                        data_int32 = data_int32[:, :, 0] * 65536 + data_int32[:, :, 1] * 256 + data_int32[:, :, 2]
                        data_int32[data_int32 >= 8388608] -= 16777216
                        data_int32 = data_int32.astype(np.int32)

                        # Convert to appropriate units (adjust scaling factor)
                        data_scaled = data_int32.T * 0.000286

                        start_idx = DeviceStartIndex[DevId]
                        data_block[start_idx:start_idx + num_channels, :] = data_scaled

            # Process SyncStatChan (last 6 channels)
            num_syncstat_bytes = 12  # 6 channels * 2 bytes each
            data_bytes = Temp[:, TempIndex:TempIndex + num_syncstat_bytes]
            TempIndex += num_syncstat_bytes

            # Convert bytes to int16
            data_int16 = data_bytes.reshape(num_samples, 6, 2)
            data_int16 = data_int16[:, :, 0] * 256 + data_int16[:, :, 1]
            data_int16[data_int16 >= 32768] -= 65536
            data_int16 = data_int16.astype(np.int16)

            data_mV = data_int16.T * 0.000286

            data_block[-6:, :] = data_mV

            # Append data_block to emg_data
            emg_data.append(data_block)

            # Put the data into the queue for plotting
            data_queue.put(data_block)
            print(f"Data block of shape {data_block.shape} added to queue")

        print("Recording stopped")
        # Send the stop command to SyncStation
        ConfString[0] = 0
        ConfString[1] = CRC8(ConfString, 1)
        StopCommand = ConfString[0:2]
        packed_data = struct.pack('B' * 2, *StopCommand)

        print("Stop Command sent")
        tcpSocket.send(packed_data)

        # Close the TCP socket
        tcpSocket.shutdown(socket.SHUT_RDWR)
        tcpSocket.close()
        print("Socket closed")

    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")
        recording = False

def save_data():
    # Format the timestamp for the filename
    timestamp_str = start_time.strftime("%Y%m%d_%H%M%S%f")[:-3]  # Up to milliseconds
    filename_npy = f"emg_data_{timestamp_str}.npy"
    filename_csv = f"emg_data_{timestamp_str}.csv"

    # Concatenate all data blocks
    if emg_data:
        emg_data_array = np.concatenate(emg_data, axis=1)

        # Save the EMG data to a .npy file
        np.save(filename_npy, emg_data_array)
        print(f"EMG data saved to {filename_npy}")

        # Save the EMG data to a CSV file
        # Transpose the array so that each row corresponds to a sample
        np.savetxt(filename_csv, emg_data_array.T, delimiter=',')
        print(f"EMG data saved to {filename_csv}")
        messagebox.showinfo("Data Saved", f"EMG data saved to {filename_npy} and {filename_csv}")
    else:
        print("No data recorded.")
        messagebox.showinfo("No Data", "No data was recorded.")

# Create buttons
start_button = tk.Button(root, text="Start Recording", command=start_recording)
stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, state=tk.DISABLED)

# Place buttons on the window
start_button.pack(pady=10)
stop_button.pack(pady=10)

# Create a frame for the plot
plot_frame = tk.Frame(root)
plot_frame.pack()

# Initialize real-time plotting
plt.style.use('ggplot')  # Optional: Use a style for better aesthetics
num_channels_to_plot = 12  # Total electrodes to plot
num_rows = 2
num_cols = 6

fig, axs = plt.subplots(num_rows, num_cols, figsize=(12, 6), sharex=True)
fig.suptitle('Real-Time EMG Signals from Selected Electrodes', fontsize=16)
lines = []
time_window = 5  # seconds
max_samples = int(time_window * sampFreq)
time_axis = np.linspace(-time_window, 0, max_samples)

# Initialize data buffer for plotting
plot_data = np.zeros((num_channels_to_plot, max_samples))

# Choose channels to plot
# Map electrode positions to channel numbers
def get_channel_numbers():
    grid_channels = []
    for grid in range(2):  # Two grids
        grid_positions = []
        channel = 0  # Reset channel for each grid
        for row in range(13):
            for col in range(5):
                if (row == 0 and col == 0):
                    continue  # Skip missing electrode at top-left
                if (row == 12 and col == 4):
                    continue  # Skip missing electrode at bottom-right
                grid_positions.append((row, col, channel))
                channel += 1
        grid_channels.append(grid_positions)
    return grid_channels

grid_channels = get_channel_numbers()

# Electrode positions to select for each grid
selected_positions = [
    (0, 1),  # Top Left Corner
    (0, 4),  # Top Right Corner
    (6, 0),  # Middle Left
    (6, 2),  # Middle Center
    (6, 4),  # Middle Right
    (12, 0)  # Bottom Left
]

# Number of channels in each grid
grid_channel_counts = [70, 70] 
channels_to_plot = []
for grid_index, grid in enumerate(grid_channels):
    offset = sum(grid_channel_counts[:grid_index])  # Calculate cumulative offset
    for pos in selected_positions:
        for (row, col, ch) in grid:
            if (row, col) == pos:
                channels_to_plot.append(ch + offset)
                break

# Sort channels_to_plot and limit to 12
channels_to_plot = sorted(channels_to_plot)[:12]

# Debug: Print TotNumChan and channels_to_plot
print(f"TotNumChan: {TotNumChan}")
print(f"channels_to_plot: {channels_to_plot}")
print(f"Max index in channels_to_plot: {max(channels_to_plot)}")

# Check if channels_to_plot indices are within TotNumChan
if max(channels_to_plot) >= TotNumChan:
    print("Error: channels_to_plot indices are out of range.")
    messagebox.showerror("Error", "Selected channels exceed the total number of channels.")
    exit()

# Flatten axs for consistent indexing
axs = axs.flatten()

for i, ax in enumerate(axs):
    if i >= len(channels_to_plot):
        ax.axis('off')  # Hide unused subplots
        continue
    line, = ax.plot(time_axis, plot_data[i], color='blue', linewidth=0.5)
    ax.set_ylim([-1, 1])  # Set appropriate y-limits
    ax.set_title(f'Ch {channels_to_plot[i]+1}', fontsize=8)
    ax.tick_params(axis='both', which='both', labelsize=6)
    if i % num_cols == 0:
        ax.set_ylabel('Amplitude (mV)', fontsize=8)
    else:
        ax.set_yticklabels([])
    if i >= num_cols * (num_rows - 1):
        ax.set_xlabel('Time (s)', fontsize=8)
    lines.append(line)

plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Embed the plot into the tkinter GUI
canvas = FigureCanvasTkAgg(fig, master=plot_frame)
canvas.draw()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

# Optional toolbar
toolbar = NavigationToolbar2Tk(canvas, plot_frame)
toolbar.update()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

def update_plot():
    try:
        data_updated = False
        while True:
            try:
                data_block = data_queue.get_nowait()
                data_length = data_block.shape[1]
                if data_length == 0:
                    continue
                if data_length >= max_samples:
                    plot_data[:, :] = data_block[channels_to_plot, -max_samples:]
                else:
                    plot_data[:, :-data_length] = plot_data[:, data_length:]
                    plot_data[:, -data_length:] = data_block[channels_to_plot, :]
                data_updated = True
                print(f"Data block of shape {data_block.shape} received from queue")
            except queue.Empty:
                break  # Exit the loop when queue is empty
        if data_updated:
            for i in range(len(lines)):
                lines[i].set_ydata(plot_data[i])
            canvas.draw_idle()
    except Exception as e:
        print(f"Error in update_plot: {e}")
    finally:
        root.after(50, update_plot)  # Schedule next update in 50 ms

# Start the plot update loop
update_plot()

# Start the Tkinter event loop
root.mainloop()
