import face_recognition
import cv2
import numpy as np
import csv
import os
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from picamera2 import Picamera2

# Tuning file for Arducam
TUNING_FILE = "/home/chroma/Arducam-477P-Pi4.json"
SAVE_PATH = "/home/chroma/Desktop/Face Recognition/SD_Midterm_Test"
os.makedirs(SAVE_PATH, exist_ok=True)

# MQTT Configuration
MQTT_BROKER = "192.168.1.48"
MQTT_PORT = 1883
MQTT_TOPIC = "wled/main/api"
bucket_mapping = {
    "monk_1": "Bucket1", "monk_2": "Bucket1",
    "monk_3": "Bucket2", "monk_4": "Bucket2",
    "monk_5": "Bucket3", "monk_6": "Bucket3",
    "monk_7": "Bucket4", "monk_8": "Bucket4",
    "monk_9": "Bucket5", "monk_10": "Bucket5",
}

# Load Monk Skin Tone Dataset
def load_monk_skin_tones(csv_path):
    skin_tones = {}
    with open(csv_path, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            tone = row[0]
            rgb = (int(row[1]), int(row[2]), int(row[3]))
            skin_tones.setdefault(tone, []).append(rgb)
    return skin_tones

# Classify skin tone using Euclidean distance
def classify_skin_tone(rgb_sample, reference_dataset):
    min_dist = float("inf")
    closest_tone = None
    for tone, samples in reference_dataset.items():
        for ref_rgb in samples:
            dist = np.linalg.norm(np.array(rgb_sample) - np.array(ref_rgb))
            if dist < min_dist:
                min_dist = dist
                closest_tone = tone
    return closest_tone

# Extract forehead RGB
def get_forehead_rgb(frame, face_location):
    top, right, bottom, left = face_location
    face_height = bottom - top
    forehead_top = top + int(face_height * 0.15)
    forehead_bottom = top + int(face_height * 0.30)
    forehead = frame[forehead_top:forehead_bottom, left:right]
    rgb_forehead = cv2.cvtColor(forehead, cv2.COLOR_BGR2RGB)
    avg_r = int(np.mean(rgb_forehead[:, :, 0]))
    avg_g = int(np.mean(rgb_forehead[:, :, 1]))
    avg_b = int(np.mean(rgb_forehead[:, :, 2]))
    return (avg_r, avg_g, avg_b)

# Initialize Camera
def initialize_camera():
    picam2 = Picamera2(tuning=TUNING_FILE)
    config = picam2.create_preview_configuration(main={"format": "RGB888", "size": (1280, 960)})
    picam2.configure(config)
    picam2.start()
    time.sleep(2)
    return picam2

# Initialize everything
picam2 = initialize_camera()
MONK_SKIN_TONES = load_monk_skin_tones("/home/chroma/Desktop/Face Recognition/monk_skin_tones.csv")
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Buffer for classification voting
classification_buffer = []
max_samples = 7

print("Press 'SPACE' to capture, 'R' to reset, 'Q' to quit.")

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Ensure proper color space

    face_locations = face_recognition.face_locations(frame, model="hog")

    for face_location in face_locations:
        avg_rgb = get_forehead_rgb(frame, face_location)
        skin_tone = classify_skin_tone(avg_rgb, MONK_SKIN_TONES)
        classification_buffer.append(skin_tone)

        if len(classification_buffer) > max_samples:
            classification_buffer.pop(0)

        most_common = max(set(classification_buffer), key=classification_buffer.count)

        # Draw box and label
        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)
        cv2.rectangle(frame, (left, bottom + 20), (right, bottom), (0, 255, 0), cv2.FILLED)
        cv2.putText(frame, most_common, (left + 6, bottom + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        print(f"Detected RGB: {avg_rgb} -> Classified as: {skin_tone}")

    cv2.imshow("Skin Tone Detection", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break

    elif key == ord("r"):
        classification_buffer.clear()
        print("Classification buffer reset.")

    elif key == ord(" "):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_filename = f"{SAVE_PATH}/captured_{timestamp}.jpg"
        cv2.imwrite(image_filename, frame)
        print(f"Image saved to {image_filename}")

        if classification_buffer:
            final_tone = max(set(classification_buffer), key=classification_buffer.count)
            bucket = bucket_mapping.get(final_tone, "Bucket3")
            mqtt_client.publish(MQTT_TOPIC, f"PL={bucket}")
            print(f"Sent MQTT command: PL={bucket} to {MQTT_TOPIC}")

cv2.destroyAllWindows()
picam2.stop()
