import os
import numpy as np
import matplotlib.pyplot as plt
import joblib

def inspect_loaded_data(data_matrix, index_dict, participant_id, trial_id):
    """
    Inspects a loaded data matrix to verify the content of OTB, Myo, and Kinematic data.
    Includes a detailed per-channel check for flat or zeroed-out channels.

    Args:
        data_matrix (np.ndarray): The data segment to inspect (e.g., lift_p1).
        index_dict (dict): The dictionary containing the feature indices.
        participant_id (int): The ID of the participant for titling.
        trial_id (int): The ID of the trial for titling.
    """
    print("\n" + "="*80)
    print(f"--- DATA INSPECTION REPORT | Participant {participant_id}, Trial {trial_id} ---")
    print("="*80)

    # --- 1. Extract Slices based on Indices ---
    try:
        otb_start, otb_end = index_dict['otb_indices']
        myo_start, myo_end = index_dict['myo_indices']
        kin_hand_start, kin_hand_end = index_dict['kin_hand_indices']

        otb_data = data_matrix[:, otb_start:otb_end]
        myo_data = data_matrix[:, myo_start:myo_end]
        kin_data = data_matrix[:, kin_hand_start:kin_hand_end]

    except KeyError as e:
        print(f"ERROR: Missing key in index_dict: {e}")
        return
    except Exception as e:
        print(f"ERROR: Failed to slice data: {e}")
        return

    # --- 2. Print Statistical Fingerprints ---
    print("\n[INFO] Statistical Fingerprint of Loaded Data Slices:")
    
    print("\n--- OTB Data ---")
    if otb_data.size > 0:
        print(f"  Shape: {otb_data.shape}")
        print(f"  Mean:  {np.mean(otb_data):.6f}")
        print(f"  Std:   {np.std(otb_data):.6f}")
        print(f"  Min:   {np.min(otb_data):.6f}")
        print(f"  Max:   {np.max(otb_data):.6f}")
    else:
        print("  OTB data slice is empty!")

    print("\n--- Myo Data ---")
    if myo_data.size > 0:
        print(f"  Shape: {myo_data.shape}")
        print(f"  Mean:  {np.mean(myo_data):.6f}")
        print(f"  Std:   {np.std(myo_data):.6f}")
        print(f"  Min:   {np.min(myo_data):.6f}")
        print(f"  Max:   {np.max(myo_data):.6f}")
    else:
        print("  Myo data slice is empty!")

    print("\n--- Kinematic Hand Data ---")
    if kin_data.size > 0:
        print(f"  Shape: {kin_data.shape}")
        print(f"  Mean:  {np.mean(kin_data):.6f}")
        print(f"  Std:   {np.std(kin_data):.6f}")
        print(f"  Min:   {np.min(kin_data):.6f}")
        print(f"  Max:   {np.max(kin_data):.6f}")
    else:
        print("  Kinematic data slice is empty!")

    # --- 3. NEW: Per-Channel Content Check ---
    print("\n[INFO] Per-Channel Content Verification (checking for flat channels):")
    flat_channel_found = False
    for name, data, start_idx in [("OTB", otb_data, otb_start), 
                                  ("Myo", myo_data, myo_start), 
                                  ("Kinematic", kin_data, kin_hand_start)]:
        if data.size == 0: continue
        for i in range(data.shape[1]):
            channel = data[:, i]
            # Check percentage of values that are very close to zero
            near_zero_percentage = np.sum(np.isclose(channel, 0)) / len(channel) * 100
            if near_zero_percentage > 95.0:
                print(f"  [WARNING] {name} channel {start_idx + i} appears to be flat. "
                      f"({near_zero_percentage:.1f}% of values are near-zero).")
                flat_channel_found = True
    
    if not flat_channel_found:
        print("  All channels appear to have valid, non-flat data.")


    # --- 4. Plot Sample OTB Channels for Visual Verification ---
    if otb_data.size > 0:
        num_channels_to_plot = min(5, otb_data.shape[1])
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for i in range(num_channels_to_plot):
            ax.plot(otb_data[:, i], label=f'OTB Channel {otb_start + i}')
            
        ax.set_title(f'Visual Check: Sample OTB Channels | P{participant_id}, Trial {trial_id}', fontsize=16)
        ax.set_xlabel('Time (Samples)', fontsize=12)
        ax.set_ylabel('Standardized Amplitude', fontsize=12)
        ax.legend()
        ax.grid(True, linestyle='--', alpha=0.6)
        
        # Save the plot to a file
        output_filename = f"P{participant_id}_T{trial_id:02d}_otb_data_check.png"
        plt.savefig(output_filename)
        plt.close(fig)
        
        print(f"\n[SUCCESS] Saved visual check plot to: {output_filename}")
    
    print("\n" + "="*80)
    print("--- END OF REPORT ---")
    print("="*80 + "\n")


def main():
    """
    Main function to load real preprocessed data and call the inspection function.
    """
    print("--- Running Real Data Inspection ---")
    
    # --- 1. Define Paths and Parameters ---
    # !!! IMPORTANT: Update this path to your actual base directory !!!
    BASE_DIR = r"C:\Users\schmi\Documents\Studium\TUM\Masterthesis\Experimental Data"
    PREPROCESSED_DIR_NAME = "Preprocessed_Data_Matrix"
    
    # Define which participant and trial to inspect
    participant_id = 1
    trial_id = 1 # Note: this is for titling, the loaded matrix contains all trials.
    
    # --- 2. Construct File Paths ---
    participant_str = f"P({participant_id})"
    participant_dir = os.path.join(BASE_DIR, participant_str)
    preprocessed_dir = os.path.join(participant_dir, PREPROCESSED_DIR_NAME)
    
    matrix_path = os.path.join(preprocessed_dir, f"P{participant_id}_combined_matrix_phase1.npy")
    indices_path = os.path.join(preprocessed_dir, f"P{participant_id}_feature_indices.joblib")

    # --- 3. Load the Real Data ---
    if not os.path.exists(matrix_path) or not os.path.exists(indices_path):
        print(f"ERROR: Data files not found for Participant {participant_id}.")
        print(f"  - Searched for matrix at: {matrix_path}")
        print(f"  - Searched for indices at: {indices_path}")
        return

    print(f"Loading data for P{participant_id}...")
    # The loaded matrix contains ALL trials for phase 1 concatenated.
    # We will inspect the full matrix.
    full_data_matrix = np.load(matrix_path)
    index_dict = joblib.load(indices_path)
    
    # --- 4. Call the Inspection Function ---
    # We pass the full matrix to get an overall sense of the data.
    # To inspect a specific trial, you would need to use the 'phase1_trial_lengths'
    # from the index_dict to slice the correct segment. For now, we check all data.
    inspect_loaded_data(full_data_matrix, index_dict, participant_id, trial_id)
    
    print("--- Real Data Inspection Finished ---")


if __name__ == "__main__":
    # This block makes the script runnable.
    main()
