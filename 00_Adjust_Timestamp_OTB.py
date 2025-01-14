import os
import re
from datetime import datetime, timedelta

def add_time_to_timestamp(timestamp_str, delta_seconds=0.2):
    """
    Parses the timestamp string in the format 'YYYYMMDD_HHMMSSmmm',
    adds delta_seconds to it, and returns the new timestamp string.
    
    Parameters:
    - timestamp_str (str): Timestamp in the format 'YYYYMMDD_HHMMSSmmm'
    - delta_seconds (float): Seconds to add to the timestamp
    
    Returns:
    - new_timestamp_str (str): Adjusted timestamp string in the same format
    """
    try:
        # Example: "20241028_115040600"
        # Split into date and time parts
        date_part, time_part = timestamp_str.split('_')

        # Extract hour, minute, second, millisecond
        hour = int(time_part[0:2])
        minute = int(time_part[2:4])
        second = int(time_part[4:6])
        millisecond = int(time_part[6:9])  # e.g., '600' -> 600 ms

        # Create a datetime object from the date_part
        dt = datetime.strptime(date_part, "%Y%m%d")
        # Replace the hour, minute, second, and microsecond fields
        dt = dt.replace(
            hour=hour, 
            minute=minute, 
            second=second, 
            microsecond=millisecond * 1000
        )

        # Add the requested delta in seconds (default is 0.2)
        adjusted_dt = dt + timedelta(seconds=delta_seconds)

        # Format back to the original structure 'YYYYMMDD_HHMMSSmmm'
        # %f yields microseconds; slicing off the last 3 digits gets 'mmm'
        new_timestamp_str = adjusted_dt.strftime("%Y%m%d_%H%M%S%f")[:-3]
        return new_timestamp_str
    
    except Exception as e:
        print(f"Error parsing or adjusting timestamp '{timestamp_str}': {e}")
        return None

def rename_files_in_folder(folder_path, delta_seconds=0.2):
    """
    Renames all .npy and .png files in the specified folder by adding
    delta_seconds to their timestamp in the filename. There is no dry-run,
    so the renaming is performed immediately.
    
    Parameters:
    - folder_path (str): Path to the folder containing the files to rename
    - delta_seconds (float): Seconds to add to the timestamp
    """
    pattern = re.compile(r"^(processed_emg_data_)(\d{8}_\d{9})(.*\.(npy|png))$")

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)

        # Skip directories
        if not os.path.isfile(file_path):
            continue

        # Match against our pattern
        match = pattern.match(filename)
        if not match:
            continue 

        prefix, timestamp_str, suffix_full, _ = match.groups()
        # suffix_full includes everything after the timestamp, e.g., "_bad_channels.npy"

        # Adjust the timestamp
        new_timestamp_str = add_time_to_timestamp(timestamp_str, delta_seconds=delta_seconds)
        if not new_timestamp_str:
            print(f"Skipping file due to timestamp adjustment error: {filename}")
            continue

        # Construct the new filename
        new_filename = f"{prefix}{new_timestamp_str}{suffix_full}"
        new_file_path = os.path.join(folder_path, new_filename)

        # Check if the new filename already exists to avoid overwriting
        if os.path.exists(new_file_path):
            print(f"Cannot rename '{filename}' -> '{new_filename}': target file already exists.")
            continue

        # Perform the actual rename
        try:
            os.rename(file_path, new_file_path)
            print(f"Renamed '{filename}' -> '{new_filename}'")
        except Exception as e:
            print(f"Error renaming '{filename}' -> '{new_filename}': {e}")

def main():
    # Base directory containing participant folders, e.g., P(1), P(2), ...
    base_path = r"C:\Users\schmi\Documents\Studium\TUM\5. Semester\Masterthesis\Experimental Data"

    # Define your participant range here; e.g., range(1, 9) for P(1) through P(8)
    participant_list = range(1, 9)

    # Subfolder path after participant folder
    subfolder_path = os.path.join("Processed EMG Data", "Processed OTB+")

    for participant in participant_list:
        participant_folder = f"P({participant})"
        target_folder = os.path.join(base_path, participant_folder, subfolder_path)

        if not os.path.exists(target_folder):
            print(f"[Participant P({participant})] Folder not found: {target_folder}")
            continue

        print(f"\n[Participant P({participant})] Renaming files in: {target_folder}")
        rename_files_in_folder(target_folder, delta_seconds=0.2)

    print("\nAll participant folders processed.")

if __name__ == "__main__":
    main()
