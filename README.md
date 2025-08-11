# Analyzing Kinematic-Muscular Synergies in Object Manipulation: The Impact of Task Knowledge on Anticipatory Information during Reach and Grasp Phases


## Getting started

To make it easy for you to get started with extracting combined kinematic- muscular synergies, see the description below and refer to the Method section of the Master´s Thesis.


## Description
In this Master´s thesis kinematic and muscular synergies in the human grasp are analyzed through a human motor control study. The participants have to perform a lift and hold task with different 3D printed handle under various weight conditions. The movements of the hand are recorded by three webcams and the kinematics are extracted through the media pipeline neural network using the free motion capture software freemocap. The myoelctric signals from forearm and thenar muscles are recorded via two OTB+ Grid electrodes (2x64) while the muscle activity of extensor muscles in the forearm as well as Biceps and Triceps are recorded by Myobock EMG sensors. 

# Data Structure and Analysis Workflow

This document describes the file structure and data organization for the experimental data, designed for cross-participant and cross-trial analysis.

### 1. Directory and File Structure

The data for each participant is stored in a structured directory. For a given participant (e.g., Participant 1), the key files are located in the `Preprocessed_Data_Matrix` folder:

```
Experimental Data/
└── P(1)/
    └── Preprocessed_Data_Matrix/
        ├── P1_combined_matrix_phase1.npy
        ├── P1_combined_matrix_phase2.npy
        ├── P1_feature_indices.joblib
        └── P1_global_scaler.joblib
```

### 2. Data Matrices (`.npy` files)

There are two primary data matrices for each participant, corresponding to the two experimental phases (e.g., "reach" and "lift").

- **`P1_combined_matrix_phase1.npy`**: Contains all data for Phase 1.
- **`P1_combined_matrix_phase2.npy`**: Contains all data for Phase 2.

#### Matrix Organization:

- **Rows are Time Samples**: Each row represents a single, discrete moment in time.
- **Columns are Features**: Each column represents a specific sensor or kinematic measurement. The order of features is consistent across all files and is defined by the `..._indices` keys in the `joblib` file. Based on the verification script for Participant 1, the feature order is:
    - **OTB Features**: Columns 0-111
    - **Myo Features**: Columns 112-116
    - **Kinematic Hand Features**: Columns 117-179
- **Concatenated Trials**: The trials within each phase are **concatenated vertically**. All time samples from Trial 1 are followed by all time samples from Trial 2, and so on. The matrix itself does not contain explicit markers separating the trials.

### 3. Feature Indices and Trial Lengths (`.joblib` file)

The `P1_feature_indices.joblib` file is the "table of contents" for the data matrices. It is a Python dictionary containing the necessary metadata to interpret the data.

#### Dictionary Structure:

```python
{
    # Defines the column ranges for each data modality
    'otb_indices': (start_col, end_col),
    'myo_indices': (start_col, end_col),
    'kin_hand_indices': (start_col, end_col),

    # Lists of integers defining the length (number of rows) of each trial
    'phase1_trial_lengths': [len_trial_1, len_trial_2, ...],
    'phase2_trial_lengths': [len_trial_1, len_trial_2, ...]
}
```

- **Feature Indices (`..._indices`)**: These tuples define which columns in the data matrices belong to which sensor modality. For P1, this was `otb_indices: (0, 112)`, `myo_indices: (112, 117)`, and `kin_hand_indices: (117, 180)`.
- **Trial Lengths (`..._trial_lengths`)**: These are the most critical keys for trial-based analysis. They are lists where each element is the duration (in time samples/rows) of a single trial, in sequential order.

### 4. Standard Analysis Workflow

To correctly analyze data across trials and participants, follow this workflow:

1.  **Select Participant and Phase**: Choose the participant (`pid`) and the phase (`phase1` or `phase2`) you want to analyze.
2.  **Load Data**: Load the corresponding data matrix (e.g., `P{pid}_combined_matrix_phase1.npy`) and the `P{pid}_feature_indices.joblib` file.
3.  **Identify Trial Boundaries**:
    - Access the correct trial length list (e.g., `indices_data['phase1_trial_lengths']`).
    - Use `numpy.cumsum()` on this list to get the end-row index for each trial.
    - The start-row index of a trial is the end-row index of the previous trial (or 0 for the first trial).
4.  **Slice the Trial Data**: Use the calculated start and end indices to slice the specific trial's data from the large phase matrix.
5.  **Time Normalization (Resampling)**:
    - Since each trial has a variable time duration, it must be resampled to a standard length (e.g., 101 data points to represent 0-100% of the movement). This is essential for averaging or comparing trials across different participants.
6.  **Aggregate and Analyze**: Once trials from multiple participants have been isolated and normalized to the same length, they can be stacked, averaged, or compared statistically.


## Usage
Download the jupiter notebook scripts and install VS Code to open it. The Scripts are written in Python. Install necessary libraries and packages through the python terminal. The numbering of the files serves as guidance how the recording, processing and analysis pipeline was conducted.

## Authors and acknowledgment
B. Sc. Patrick Schmidt  
Dr. Patricia Capsi Morales  
Prof. Dr. Cristina Piazza

## License
Ownership by TUM  

## Project status
Pilot Study Phase
