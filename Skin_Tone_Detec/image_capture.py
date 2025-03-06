import os
import cv2
from datetime import datetime

PERSON_NAME = "Camera_Test"
dataset_folder = "dataset"
tuning_file = "/home/chroma/Arducam-477P-Pi4.json"

def create_folder(name):
    if not os.path.exists(dataset_folder):
        os.makedirs(dataset_folder)

    person_folder = os.path.join(dataset_folder, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

def capture_photo(name):
    folder = create_folder(name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.jpg"
    filepath = os.path.join(folder, filename)

    # Wait for camera initialization
    os.system("sleep 2")

    # Capture image using libcamera-still with tuning file
    os.system(f"libcamera-still -t 2000 --tuning-file {tuning_file} -o {filepath}")
    print(f"Photo saved: {filepath}")

    return filepath

if __name__ == "__main__":
    print(f"Capturing a photo for {PERSON_NAME}...")
    photo_path = capture_photo(PERSON_NAME)

    # Display the captured image
    image = cv2.imread(photo_path)
    if image is not None:
        cv2.imshow("Captured Image", image)
        print("Press 'q' to close the window.")
        
        # Wait for "q" key to close the window
        while True:
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
        
        cv2.destroyAllWindows()
    else:
        print("Error: Could not load the captured image.")
