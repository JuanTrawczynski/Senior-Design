import face_recognition
import cv2
import numpy as np
import csv
import os
from datetime import datetime
from picamera2 import Picamera2

# Set tuning file path for Arducam
TUNING_FILE = "/home/chroma/Arducam-477P-Pi4.json"

# Directory to save captured images
SAVE_PATH = "/home/chroma/Desktop/Face Recognition/SD_Midterm_Test"

# Ensure the folder exists
os.makedirs(SAVE_PATH, exist_ok=True)

# Load Monk Skin Tone Reference Data
def load_monk_skin_tones(csv_path):
    skin_tones = {}
    with open(csv_path, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            tone = row[0]
            rgb = (int(row[1]), int(row[2]), int(row[3]))

            # Store multiple RGB values per tone
            if tone not in skin_tones:
                skin_tones[tone] = []
            skin_tones[tone].append(rgb)

    return skin_tones

def classify_skin_tone(face_rgb, reference_rgb):
    """Find the closest Monk Skin Tone by comparing against multiple RGB samples."""
    min_distance = float("inf")
    closest_tone = None

    for tone, rgb_samples in reference_rgb.items():
        for ref_rgb in rgb_samples:
            distance = np.sqrt(
                (face_rgb[0] - ref_rgb[0])**2 +
                (face_rgb[1] - ref_rgb[1])**2 +
                (face_rgb[2] - ref_rgb[2])**2
            )

            if distance < min_distance:
                min_distance = distance
                closest_tone = tone

    return closest_tone

# Initialize camera with tuning file
def initialize_camera():
    picam2 = Picamera2(tuning=TUNING_FILE)
    config = picam2.create_preview_configuration(main={"size": (1280, 960)})
    picam2.configure(config)
    picam2.start()
    return picam2

# Get average RGB from forehead region
def get_average_face_rgb(frame, face_location):
    """Extract and compute the average RGB value from the forehead region."""
    (top, right, bottom, left) = face_location
    face_roi = frame[top:bottom, left:right]

    # Focus only on the forehead
    h, w, _ = face_roi.shape
    forehead_roi = face_roi[:int(h * 0.4), :]

    avg_r = int(np.mean(forehead_roi[:, :, 0]))
    avg_g = int(np.mean(forehead_roi[:, :, 1]))
    avg_b = int(np.mean(forehead_roi[:, :, 2]))

    return (avg_r, avg_g, avg_b)

# Initialize camera and skin tone data
MONK_SKIN_TONES = load_monk_skin_tones("monk_skin_tones.csv")
picam2 = initialize_camera()

# Frame Buffer for Smoother Classification
classification_buffer = []

print("Press 'SPACE' to capture an image. Press 'Q' to exit.")

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert to OpenCV format

    face_locations = face_recognition.face_locations(frame, model="hog")
    
    for face_location in face_locations:
        avg_rgb = get_average_face_rgb(frame, face_location)
        closest_tone = classify_skin_tone(avg_rgb, MONK_SKIN_TONES)

        # Store in buffer and take median classification
        classification_buffer.append(closest_tone)
        if len(classification_buffer) > 5:  # Keep only last 5 readings
            classification_buffer.pop(0)

        most_common_tone = max(set(classification_buffer), key=classification_buffer.count)

        # Draw bounding box around face
        (top, right, bottom, left) = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)

        # Display detected skin tone
        cv2.rectangle(frame, (left, bottom + 20), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, most_common_tone, (left + 6, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Debugging Output
        print(f"Detected RGB: {avg_rgb} -> Classified as: {most_common_tone}")

    cv2.imshow("Skin Tone Detection", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    elif key == ord(" "):  # Spacebar to capture an image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{SAVE_PATH}/captured_{timestamp}.jpg"
        cv2.imwrite(image_filename, frame)
        print(f"Image saved to {image_filename}")

cv2.destroyAllWindows()
picam2.stop()
