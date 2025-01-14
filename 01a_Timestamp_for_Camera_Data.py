
'''
Log Timestamp Processor (from seconds to milliseconds)

Description:
     This script processes log files and recording folders for multiple participants.
     It extracts timestamps from the respective log entries indicating when recordings were activated,
     matches these timestamps with correspondent recording start times based on the timestamp of the folder names,
     and renames the recording folders to include more precise timestamps with milliseconds accuracy.

Features:
    - **Log Parsing:** Scans all `.log` files within specified log directories to extract
       timestamps from lines containing "Setting active recording".
    - **Recording Folder Processing:** Identifies recording folders named in the format
       `recording_HH_MM_SS(.mmm)?(_gmt+X)?...`, extracts the time components, and matches
       them with log timestamps.
    - **Timestamp Matching:** Finds the closest log timestamp to the approximate time derived
       from folder names to ensure accurate synchronization.
    - **Folder Renaming:** Renames recording folders to include milliseconds for precise
       timestamping (e.g., `recording_14_47_20.123`).
    - **Error Handling:** Skips folders that do not conform to expected naming patterns,
       contain invalid time components, or lack corresponding log entries.
    - **Participant Iteration:** Processes multiple participants' data directories, handling
       each participant's recordings and logs independently.
'''

import os
from datetime import datetime

def gather_log_timestamps(log_folder):
    """
    Reads every .log file in the given log_folder and collects all timestamps
    from lines containing 'Setting active recording'. 
    Returns a list of (datetime, line).
    """
    all_timestamps = []
    
    log_files = [
        f for f in os.listdir(log_folder)
        if f.startswith("log_") and f.endswith(".log")
    ]
    log_files.sort()

    for log_fname in log_files:
        log_path = os.path.join(log_folder, log_fname)
        try:
            with open(log_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if "setting active recording" in line.lower():
                        try:
                            # Typically: [YYYY-MM-DDTHH:MM:SS.ssssss]
                            bracket_text = line.split(']')[0]
                            timestamp_str = bracket_text[1:]  # remove leading '['
                            log_time = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%S.%f")
                            all_timestamps.append((log_time, line.strip()))
                        except (ValueError, IndexError):
                            continue
        except FileNotFoundError:
            pass
    return all_timestamps

def find_recording_start_timestamp(log_folder, approx_time):
    """
    From all 'Setting active recording' timestamps in log_folder, 
    return the one closest to approx_time. If none found, return None.
    """
    all_timestamps = gather_log_timestamps(log_folder)
    if not all_timestamps:
        return None

    # Sort by how close they are to approx_time
    all_timestamps.sort(key=lambda x: abs((x[0] - approx_time).total_seconds()))
    
    return all_timestamps[0][0]  # The closest timestamp

def process_recording_folder(session_dir, recording_folder, session_date, log_folder):
    """
    Attempts to parse a folder name of the form:
      recording_14_47_20(.123)?(_gmt+X)?...
    1) Skips if 'calibration' in folder name.
    2) Extracts HH, MM, SS by ignoring any fractional part and trailing tokens.
    3) Builds an approximate datetime from session_date + HH:MM:SS.
    4) Finds the closest log timestamp and renames the folder to recording_HH_MM_SS.mmm.
    """
    folder_name = os.path.basename(recording_folder)
    
    # Skip calibration folders
    if "calibration" in folder_name.lower():
        print(f"  Skipping calibration folder '{folder_name}'.")
        return

    # Example patterns we might see:
    #   recording_14_47_20
    #   recording_14_47_20_gmt+1
    #   recording_14_47_20.123
    #   recording_14_47_20.123_gmt+1
    #   recording_14_47_60.999_gmt+2 (invalid seconds --> skip)
    
    parts = folder_name.split('_')
    # Minimum: ["recording", HH, MM, SSorSS.xxx...]
    if len(parts) < 4:
        print(f"  Skipping folder '{folder_name}' – cannot parse HH,MM,SS.")
        return

    try:
        hh = int(parts[1])  # e.g. "14"
        mm = int(parts[2])  # e.g. "47"
    except ValueError:
        print(f"  Skipping folder '{folder_name}' – hour/minute not numeric.")
        return

    # Handle the "seconds" part (which could be "20", "20.123", "20.123_gmt+1", etc.)
    ss_part = parts[3]

    # 1) If there's a dot, split on it and keep only what's before the dot
    #    e.g. "20.123" -> "20", or "20.123_gmt+1" -> "20"
    if '.' in ss_part:
        ss_part = ss_part.split('.')[0]

    # 2) If there's an underscore left, e.g. "20_gmt+1", split on '_' and keep first chunk
    if '_' in ss_part:
        ss_part = ss_part.split('_')[0]

    # Now ss_part should be purely integer-like (e.g., "20")
    try:
        ss = int(ss_part)
    except ValueError:
        print(f"  Skipping folder '{folder_name}' – could not parse seconds from '{ss_part}'.")
        return

    # Check the valid range for seconds
    if not (0 <= ss <= 59):
        print(f"  Skipping folder '{folder_name}' – seconds={ss} not in 0..59.")
        return

    # Combine session_date's Y/M/D with parsed HH:MM:SS
    try:
        approx_time = datetime(
            year=session_date.year,
            month=session_date.month,
            day=session_date.day,
            hour=hh,
            minute=mm,
            second=ss
        )
    except ValueError as e:
        print(f"  Skipping folder '{folder_name}' – invalid date/time: {e}")
        return
    
    # Find best match in logs
    actual_start_time = find_recording_start_timestamp(log_folder, approx_time)
    if not actual_start_time:
        print(f"  No suitable timestamp found for '{folder_name}' in logs.")
        return
    
    # Construct a new folder name with ms
    # e.g. "recording_14_47_20.123"
    new_time_str = actual_start_time.strftime("%H_%M_%S.%f")[:-3]  # remove last 3 digits of microseconds
    new_folder_name = f"recording_{new_time_str}"
    old_folder_path = os.path.join(session_dir, folder_name)
    new_folder_path = os.path.join(session_dir, new_folder_name)

    try:
        os.rename(old_folder_path, new_folder_path)
        print(f"  Renamed '{folder_name}' -> '{new_folder_name}'")
    except Exception as e:
        print(f"  Could not rename '{folder_name}' -> '{new_folder_name}' due to: {e}")

def process_session_folder(session_folder, log_folder):
    """
    session_folder might look like "session_YYYY-MM-DD_HH_MM_SS".
    Parse that, then process any subfolder starting with "recording_".
    """
    folder_name = os.path.basename(session_folder)
    if not folder_name.startswith("session_"):
        return

    # Example: "session_2024-11-18_14_15_03"
    date_str = folder_name[len("session_"):]
    try:
        session_dt = datetime.strptime(date_str, "%Y-%m-%d_%H_%M_%S")
    except ValueError:
        print(f"Skipping '{folder_name}' – not matching 'session_YYYY-MM-DD_HH_MM_SS'.")
        return

    for item in os.listdir(session_folder):
        sub_path = os.path.join(session_folder, item)
        if os.path.isdir(sub_path) and item.startswith("recording_"):
            process_recording_folder(session_folder, sub_path, session_dt, log_folder)

def process_all_participants():
    """
    Loops through P(1) to P(8), checks:
      - Camera Data Timestamped\logs_info_and_settings\logs   for .log files
      - Camera Data Timestamped\recording_sessions\session_...
         -> recording_... folders
    Skips calibration folders, handles .ms suffix, gmt+X, etc.
    """
    participants_root = (
        r"C:\Users\schmi\Documents\Studium\TUM\5. Semester\Masterthesis\Experimental Data"
    )

    for i in range(8, 9):
        participant_str = f"P({i})"
        participant_dir = os.path.join(participants_root, participant_str)
        if not os.path.isdir(participant_dir):
            print(f"Participant folder '{participant_str}' not found. Skipping.")
            continue

        camera_data_dir = os.path.join(participant_dir, "Camera Data Timestamped")
        if not os.path.isdir(camera_data_dir):
            camera_data_dir = os.path.join(participant_dir, "Camera Data")  # fallback
            if not os.path.isdir(camera_data_dir):
                print(f"No camera data folder for {participant_str}. Skipping.")
                continue

        # logs folder
        logs_dir = os.path.join(camera_data_dir, "logs_info_and_settings", "logs")
        if not os.path.isdir(logs_dir):
            print(f"No 'logs' folder found for {participant_str}. Skipping.")
            continue

        # sessions folder
        sessions_dir = os.path.join(camera_data_dir, "recording_sessions")
        if not os.path.isdir(sessions_dir):
            print(f"No 'recording_sessions' folder for {participant_str}. Skipping.")
            continue

        print(f"Processing {participant_str} in:\n  {sessions_dir}\n")

        for session_folder_name in os.listdir(sessions_dir):
            session_folder_path = os.path.join(sessions_dir, session_folder_name)
            if os.path.isdir(session_folder_path) and session_folder_name.startswith("session_"):
                process_session_folder(session_folder_path, logs_dir)

        print()

if __name__ == "__main__":
    process_all_participants()
