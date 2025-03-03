import face_recognition
import cv2
import numpy as np
import csv
from picamera2 import Picamera2
import time

# Load Monk Skin Tone Reference Data
def load_monk_skin_tones(csv_path):
    skin_tones = {}
    with open(csv_path, "r") as file:
        reader = csv.reader(file)
        next(reader)  # Skip header
        for row in reader:
            tone = row[0]
            rgb = (int(row[1]), int(row[2]), int(row[3]))
            skin_tones[tone] = rgb
    return skin_tones

def classify_skin_tone(face_rgb, reference_rgb):
    """Find the closest Monk Skin Tone based on Euclidean distance without RGB weighting."""
    min_distance = float("inf")
    closest_tone = None

    for tone, ref_rgb in reference_rgb.items():
        distance = np.sqrt(
            (face_rgb[0] - ref_rgb[0])**2 +
            (face_rgb[1] - ref_rgb[1])**2 +
            (face_rgb[2] - ref_rgb[2])**2
        )

        if distance < min_distance:
            min_distance = distance
            closest_tone = tone

    return closest_tone

# Initialize
MONK_SKIN_TONES = load_monk_skin_tones("monk_skin_tones.csv")
picam2 = Picamera2()
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.start()

def get_average_face_rgb(frame, face_location):
    """Extract and compute the average RGB value from the forehead region."""
    (top, right, bottom, left) = face_location
    face_roi = frame[top:bottom, left:right]
    face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)

    # Focus only on the top 30% of the face (forehead region)
    h, w, _ = face_roi.shape
    forehead_roi = face_roi[:int(h * 0.3), :]  # Extract top 30% of the face

    avg_r = int(np.mean(forehead_roi[:, :, 0]))
    avg_g = int(np.mean(forehead_roi[:, :, 1]))
    avg_b = int(np.mean(forehead_roi[:, :, 2]))

    return (avg_r, avg_g, avg_b)

while True:
    frame = picam2.capture_array()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    face_locations = face_recognition.face_locations(rgb_frame, model="hog")
    
    for face_location in face_locations:
        avg_rgb = get_average_face_rgb(frame, face_location)
        closest_tone = classify_skin_tone(avg_rgb, MONK_SKIN_TONES)

        # Draw bounding box around face
        (top, right, bottom, left) = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)

        # Display detected skin tone
        cv2.rectangle(frame, (left, bottom + 20), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, closest_tone, (left + 6, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        # Debugging Output
        print(f"Detected RGB: {avg_rgb} -> Classified as: {closest_tone}")

    cv2.imshow("Skin Tone Detection", cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

    if cv2.waitKey(1) == ord("q"):
        break

cv2.destroyAllWindows()
picam2.stop()
