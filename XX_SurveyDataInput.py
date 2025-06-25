# This Python script conducts a survey to collect participant responses on questions related to their post experimental experience. The responses are saved in a structured directory for further analysis. Key functionalities:

# - **Survey Questions**: Presents a list of 17 questions for participants to rate on a scale of 1 (Strongly Disagree) to 7 (Strongly Agree).
# - **Participant Details**: Collects basic demographic details such as Participant ID, Name, Age, Gender, Height, and Handedness.
# - **Response Collection**: Uses a GUI dialog to ask questions one at a time.
# - **Save Responses**: Saves the participant details and survey responses to a `.npy` file in a designated directory structure.
# - **Error Handling**: Ensures all required details and responses are provided and handles incomplete or invalid entries gracefully.

import os
import tkinter as tk
from tkinter import simpledialog, messagebox
import numpy as np

# Survey Questions
questions = [
    "I consciously think about the location of the weight before grasping.",
    "I feel more muscle strain when I do not know the weight location.",
    "I feel more comfortable with my grip when I know the weight location.",
    "I do not adjust my grasp on the handle based on the weight location.",
    "I find it easy to lift the object without tilting when I do not know the weight location.",
    "I feel less muscle strain when I know the weight location.",
    "I find it difficult to lift the object without tilting when I know the weight location.",
    "I feel uncomfortable with my grip on the object when I know the weight location.",
    "I do not consciously think about the location of the weight before grasping.",
    "My muscles feel more fatigued when I know the weight location.",
    "My grip feels just as secure when I do not know the weight location.",
    "I find it easier to lift the object parallel to the table when I know the weight location.",
    "I adjust my grasp on the handle based on the weight location.",
    "My muscles feel less fatigued when I know the weight location.",
    "I find it difficult to lift the object without tilting when I do not know the weight location.",
    "My grip feels safer when I know the weight location.",
    "I regularly engage in strength training exercises for my arm muscles."
]

def save_results(details, responses, base_path):
    """Save survey results to a specified directory."""
    participant_folder = os.path.join(base_path, f"P({details['participant_id']})")
    os.makedirs(participant_folder, exist_ok=True)  # Create folder if it doesn't exist
    
    filename = os.path.join(participant_folder, f"participant_{details['participant_id']}_responses.npy")
    data = {
        "details": details,
        "responses": responses
    }
    np.save(filename, data)
    messagebox.showinfo("Save Successful", f"Responses saved at {filename}")

def survey():
    """Main function to conduct the survey."""
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Base directory for saving files
    base_path = r"C:\Users\schmi\Documents\Studium\TUM\5. Semester\Masterthesis\Experimental Data"
    
    try:
        details = {
            "participant_id": simpledialog.askstring("Participant ID", "Enter Participant ID:"),
            "name": simpledialog.askstring("Name", "Enter your Name:"),
            "age": simpledialog.askinteger("Age", "Enter your Age:"),
            "gender": simpledialog.askstring("Gender", "Enter your Gender (Male/Female/Other):"),
            "height": simpledialog.askfloat("Height", "Enter your Height (in cm):"),
            "handedness": simpledialog.askstring("Handedness", "Enter Handedness (Left or Right):")
        }
        
        # Check if all details are provided
        if not all(details.values()):
            raise ValueError("All participant details are required.")
        
        responses = []
        for question in questions:
            response = simpledialog.askinteger(
                "Survey Question",
                f"{question}\n\nRate from 1 (Strongly Disagree) to 7 (Strongly Agree):",
                minvalue=1,
                maxvalue=7
            )
            if response is None:
                raise ValueError("Survey incomplete. Closing.")
            responses.append(response)
        
        # Save the results
        save_results(details, responses, base_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))
    finally:
        root.destroy()

if __name__ == "__main__":
    survey()