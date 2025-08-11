import os
import joblib

# =====================================================================
# SCRIPT TO CLEAN AND OVERWRITE JOBLIB INDEX FILES
#
# PURPOSE:
#   - This script iterates through all participant folders.
#   - It loads the 'P{pid}_feature_indices.joblib' file.
#   - It removes the large, unnecessary 'combined' data array key.
#   - It overwrites the original file with the cleaned dictionary.
#
# USAGE:
#   - Run this script ONCE to clean up the files. It is safe to
#     run multiple times, but it will have no effect after the
#     first successful run.
# =====================================================================


# ---------------------------------------------------------------------
# 1) Global Parameters
# ---------------------------------------------------------------------
BASE_DIR = r"C:\Users\schmi\Documents\Studium\TUM\Masterthesis\Experimental Data"
PARTICIPANTS = [1, 2, 3, 4, 5, 6, 7, 8]


# ---------------------------------------------------------------------
# 2) Main Cleanup Function
# ---------------------------------------------------------------------
def clean_joblib_files():
    """
    Loads each participant's feature_indices.joblib file, removes the
    'combined' key if it exists, and saves the file back in place.
    """
    print(f"\n{'='*60}\n       RUNNING: Joblib File Cleanup Utility\n{'='*60}")
    
    total_cleaned = 0
    for pid in PARTICIPANTS:
        print(f"\n--- Checking Participant {pid} ---")
        
        # Construct the full path to the target joblib file
        indices_path = os.path.join(
            BASE_DIR,
            f"P({pid})",
            "Preprocessed_Data_Matrix",
            f"P{pid}_feature_indices.joblib"
        )

        # Check if the file exists before trying to modify it
        if not os.path.exists(indices_path):
            print(f"[WARN] File not found: {os.path.basename(indices_path)}. Skipping.")
            continue

        try:
            # Load the existing data from the file
            data_dict = joblib.load(indices_path)

            # Check if the key to be removed exists in the dictionary
            if 'combined' in data_dict:
                print(f"[INFO] Found unnecessary 'combined' data key in {os.path.basename(indices_path)}.")
                
                # Remove the key from the dictionary
                del data_dict['combined']
                
                # Overwrite the original file with the cleaned dictionary
                joblib.dump(data_dict, indices_path)
                
                print(f"[SUCCESS] Cleaned and overwrote the file.")
                total_cleaned += 1
            else:
                print(f"[INFO] File is already clean. No action needed.")

        except Exception as e:
            print(f"[ERROR] Could not process file for P({pid}). Reason: {e}")
            
    print(f"\n{'='*60}\n       CLEANUP COMPLETE: {total_cleaned} file(s) were modified.\n{'='*60}")


# ---------------------------------------------------------------------
# 3) Script Execution
# ---------------------------------------------------------------------
if __name__ == "__main__":
    clean_joblib_files()
