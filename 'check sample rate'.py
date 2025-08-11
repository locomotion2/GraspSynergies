'check sample rate'
import joblib
import os

# --- Configuration ---
BASE_DIR = r"C:\Users\schmi\Documents\Studium\TUM\Masterthesis\Experimental Data"
PARTICIPANT_ID = 1          # <-- Participant to check
TRIAL_TO_CHECK = 5          # <-- Trial number to check (e.g., 1-24)
PHASE_TO_CHECK = "phase1"   # Use "phase1" (reach) or "phase2" (lift)

# --- Verification Logic ---
try:
    # Path to the metadata file created by your preprocessing script
    preprocessed_dir = os.path.join(BASE_DIR, f"P({PARTICIPANT_ID})", "Preprocessed_Data_Matrix")
    indices_path = os.path.join(preprocessed_dir, f"P{PARTICIPANT_ID}_feature_indices.joblib")

    # Load the metadata dictionary
    metadata = joblib.load(indices_path)
    
    # Get the list of trial lengths for the chosen phase
    trial_lengths_key = f"{PHASE_TO_CHECK}_trial_lengths"
    trial_lengths = metadata[trial_lengths_key]
    
    # This logic handles skipped trials to find the correct list index
    P7_SKIPPED_TRIALS = [20, 22] # As defined in your scripts
    skip_list = P7_SKIPPED_TRIALS if PARTICIPANT_ID == 7 else []
    valid_trials = [t for t in range(1, 25) if t not in skip_list]
    
    if TRIAL_TO_CHECK not in valid_trials:
        raise ValueError(f"Trial {TRIAL_TO_CHECK} was skipped for P{PARTICIPANT_ID}.")
    
    # Find the correct 0-based index for the desired trial
    trial_index = valid_trials.index(TRIAL_TO_CHECK)
    
    # Get the number of samples for that specific trial from the list
    num_samples = trial_lengths[trial_index]

    print(f"--- Data Duration Check ---")
    print(f"Participant: {PARTICIPANT_ID}, Trial: {TRIAL_TO_CHECK} ({PHASE_TO_CHECK})")
    print(f"Number of Samples found: {num_samples}")
    print("-" * 35)

    # Calculate duration assuming 500 Hz
    duration_500hz = num_samples / 500.0
    print(f"Implied Duration at 500 Hz:  {duration_500hz:.2f} seconds")

    # Calculate duration assuming 2000 Hz
    duration_2000hz = num_samples / 2000.0
    print(f"Implied Duration at 2000 Hz: {duration_2000hz:.2f} seconds")

except FileNotFoundError:
    print(f"Error: Metadata file not found at -> {indices_path}")
except (KeyError, IndexError, ValueError) as e:
    print(f"Error: Could not process trial information. Details: {e}")