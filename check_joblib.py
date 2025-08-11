import os
import joblib
import numpy as np

# =====================================================================
# CONFIGURATION
# =====================================================================
# --- SET THIS TO THE PARTICIPANT YOU WANT TO CHECK ---
PARTICIPANT_TO_CHECK = 1
# ---------------------------------------------------------------------

BASE_DIR = r"C:\Users\schmi\Documents\Studium\TUM\Masterthesis\Experimental Data"

# =====================================================================
# VERIFICATION FUNCTION
# =====================================================================
def verify_indices_file(pid):
    """
    Loads and inspects the feature_indices.joblib file for a given
    participant, printing its contents and calculating sample trial indices.
    """
    print(f"\n--- Verifying Indices for Participant {pid} ---")

    # Construct the path to the joblib file
    participant_dir = os.path.join(BASE_DIR, f"P({pid})")
    indices_path = os.path.join(participant_dir, "Preprocessed_Data_Matrix", f"P{pid}_feature_indices.joblib")

    # Check if the file exists
    if not os.path.exists(indices_path):
        print(f"[ERROR] File not found at: {indices_path}")
        print("Please ensure the preprocessing script has been run for this participant.")
        return

    # Load the data from the joblib file
    try:
        indices_data = joblib.load(indices_path)
        print(f"[SUCCESS] Successfully loaded file: {os.path.basename(indices_path)}\n")
    except Exception as e:
        print(f"[ERROR] Failed to load or read the joblib file. Reason: {e}")
        return

    # --- 1. Print the raw contents of the dictionary ---
    print("=" * 50)
    print(" Full Contents of the Joblib File")
    print("-" * 50)
    for key, value in indices_data.items():
        # Shorten long lists for cleaner printing
        if isinstance(value, list) and len(value) > 10:
            print(f"  '{key}': {value[:5]}... (Total {len(value)} items)")
        else:
            print(f"  '{key}': {value}")
    print("=" * 50)


    # --- 2. Calculate and display derived trial indices ---
    print("\n" + "=" * 50)
    print(" Derived Trial Start/End Indices")
    print("-" * 50)

    # Calculate indices for Phase 1
    if 'phase1_trial_lengths' in indices_data:
        p1_lengths = indices_data['phase1_trial_lengths']
        # Calculate cumulative sum to find the end point of each trial
        p1_cumulative_lengths = np.cumsum(p1_lengths)
        
        print("\n  Phase 1 Trials:")
        start_index = 0
        # Display the first 5 trials as an example
        for i, end_index in enumerate(p1_cumulative_lengths[:5]):
            print(f"    - Trial {i+1}: Rows {start_index} to {end_index - 1} (Length: {p1_lengths[i]})")
            start_index = end_index
        if len(p1_cumulative_lengths) > 5:
            print("    ...")

    # Calculate indices for Phase 2
    if 'phase2_trial_lengths' in indices_data:
        p2_lengths = indices_data['phase2_trial_lengths']
        p2_cumulative_lengths = np.cumsum(p2_lengths)

        print("\n  Phase 2 Trials:")
        start_index = 0
        # Display the first 5 trials
        for i, end_index in enumerate(p2_cumulative_lengths[:5]):
            print(f"    - Trial {i+1}: Rows {start_index} to {end_index - 1} (Length: {p2_lengths[i]})")
            start_index = end_index
        if len(p2_cumulative_lengths) > 5:
            print("    ...")
    
    print("\n" + "=" * 50)


# =====================================================================
# EXECUTION
# =====================================================================
if __name__ == "__main__":
    verify_indices_file(PARTICIPANT_TO_CHECK)
