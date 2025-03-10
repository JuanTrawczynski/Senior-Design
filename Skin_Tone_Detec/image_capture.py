import os
import cv2
from datetime import datetime
from picamera2 import Picamera2

# Set tuning file path for Arducam
TUNING_FILE = "/home/chroma/Arducam-477P-Pi4.json"

# Folder to save captured images
DATASET_FOLDER = "dataset"
PERSON_NAME = "Camera_Test"

# Create dataset folder if it doesn't exist
def create_folder(name):
    if not os.path.exists(DATASET_FOLDER):
        os.makedirs(DATASET_FOLDER)

    person_folder = os.path.join(DATASET_FOLDER, name)
    if not os.path.exists(person_folder):
        os.makedirs(person_folder)
    return person_folder

# Initialize PiCamera2 with Arducam tuning file
def initialize_camera():
    picam2 = Picamera2(tuning=TUNING_FILE)
    config = picam2.create_preview_configuration(main={"size": (1280, 960)})
    picam2.configure(config)
    picam2.start()
    return picam2

# Capture images on Space key press, quit on "Q"
def capture_photos():
    folder = create_folder(PERSON_NAME)
    picam2 = initialize_camera()

    print("Press SPACE to capture an image, 'Q' to quit.")

    while True:
        frame = picam2.capture_array()
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to OpenCV format

        cv2.imshow("Live Camera Feed", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == ord(' '):  # Space key to capture
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{PERSON_NAME}_{timestamp}.jpg"
            filepath = os.path.join(folder, filename)
            cv2.imwrite(filepath, frame)
            print(f"Photo saved: {filepath}")

        elif key == ord('q'):  # 'Q' key to quit
            print("Exiting program...")
            break

    # Cleanup
    cv2.destroyAllWindows()
    picam2.stop()

# Run the program
if __name__ == "__main__":
    capture_photos()
