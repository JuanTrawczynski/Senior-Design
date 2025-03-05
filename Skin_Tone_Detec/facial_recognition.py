import face_recognition
import cv2
import numpy as np
import csv

# Detect if using Pi Camera or Webcam
USE_PICAMERA = False  # Set to True if using Pi Camera

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

# Initialize
MONK_SKIN_TONES = load_monk_skin_tones("monk_skin_tones.csv")

if USE_PICAMERA:
    from picamera2 import Picamera2
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()

def get_average_face_rgb(frame, face_location):
    """Extract and compute the average RGB value from the forehead region."""
    (top, right, bottom, left) = face_location
    face_roi = frame[top:bottom, left:right]

    if not USE_PICAMERA:
        face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)  # Convert only for webcam input

    # Focus only on the forehead
    h, w, _ = face_roi.shape
    forehead_roi = face_roi[:int(h * 0.4), :]

    avg_r = int(np.mean(forehead_roi[:, :, 0]))
    avg_g = int(np.mean(forehead_roi[:, :, 1]))
    avg_b = int(np.mean(forehead_roi[:, :, 2]))

    return (avg_r, avg_g, avg_b)

# Use OpenCV VideoCapture if using a webcam
if not USE_PICAMERA:
    cap = cv2.VideoCapture(0)

# Frame Buffer for Smoother Classification
classification_buffer = []

while True:
    if USE_PICAMERA:
        frame = picam2.capture_array()
    else:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

    if not USE_PICAMERA:
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  # Convert for webcam only
    else:
        rgb_frame = frame

    face_locations = face_recognition.face_locations(rgb_frame, model="hog")
    
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

    if cv2.waitKey(1) == ord("q"):
        break

cv2.destroyAllWindows()

if USE_PICAMERA:
    picam2.stop()
else:
    cap.release()
