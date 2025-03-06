import os
from datetime import datetime

# Change this to the name of the person you're photographing
PERSON_NAME = "Monk #3"

# Define paths
dataset_folder = "dataset"
tuning_file = "/home/chroma/Arducam-477P-Pi4.json"

def create_folder(name):
    """Creates a folder for storing captured images."""
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)

    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photo(name):
    """Captures an image using libcamera-still with the tuning file."""
    folder = create_folder(name)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.jpg"
    filepath = os.path.join(folder, filename)
    
    # Capture image using libcamera-still with the tuning file
    os.system(f"libcamera-still -t 1000 --tuning-file {tuning_file} -o {filepath}")
    
    print(f"Photo saved: {filepath}")

if __name__ == "__main__":
    print(f"Capturing a photo for {PERSON_NAME}...")
    capture_photo(PERSON_NAME)
