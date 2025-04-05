import face_recognition
import cv2
import numpy as np
import csv
import os
import time
from picamera2 import Picamera2
from libcamera import controls
import paho.mqtt.client as mqtt

# Configurations
TUNING_FILE = "/home/chroma/Arducam-477P-Pi4.json"
CSV_PATH = "/home/chroma/Desktop/Face Recognition/monk_skin_tones.csv"
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "wled/main/api"
SAMPLE_COUNT = 7

# Mapping Monk tones to WLED bucket presets
bucket_mapping = {
    "monk_1": "Bucket1", "monk_2": "Bucket1",
    "monk_3": "Bucket2", "monk_4": "Bucket2",
    "monk_5": "Bucket3", "monk_6": "Bucket3",
    "monk_7": "Bucket4", "monk_8": "Bucket4",
    "monk_9": "Bucket5", "monk_10": "Bucket5",
}

# Load Monk RGB values from CSV
def load_skin_tone_dataset(csv_path):
    dataset = {}
    with open(csv_path, "r") as file:
        reader = csv.reader(file)
        next(reader)
        for row in reader:
            tone = row[0]
            rgb = tuple(map(int, row[1:4]))
            dataset.setdefault(tone, []).append(rgb)
    return dataset

# Find the closest tone via Euclidean distance
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

# Get average RGB from forehead
def get_forehead_rgb(frame, face_location):
    top, right, bottom, left = face_location
    face_height = bottom - top
    forehead_top = top + int(face_height * 0.15)
    forehead_bottom = top + int(face_height * 0.30)
    forehead = frame[forehead_top:forehead_bottom, left:right]
    forehead_rgb = cv2.cvtColor(forehead, cv2.COLOR_BGR2RGB)
    avg_r = int(np.mean(forehead_rgb[:, :, 0]))
    avg_g = int(np.mean(forehead_rgb[:, :, 1]))
    avg_b = int(np.mean(forehead_rgb[:, :, 2]))
    return (avg_r, avg_g, avg_b)

# Setup MQTT
mqtt_client = mqtt.Client()
mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Setup Camera
picam2 = Picamera2(tuning=TUNING_FILE)
picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
picam2.set_controls({"AwbEnable": True, "ExposureTime": 5000, "AnalogueGain": 1.0})
picam2.start()
time.sleep(2)

# Load Reference Data
reference_rgb = load_skin_tone_dataset(CSV_PATH)

# Skin tone sampling buffer
skin_tone_samples = []
print("Press 'R' to reset, 'Q' to quit.")

while True:
    frame = picam2.capture_array()
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(rgb_frame)

    for face_location in face_locations:
        forehead_rgb = get_forehead_rgb(frame, face_location)
        detected_tone = classify_skin_tone(forehead_rgb, reference_rgb)
        print(f"Detected RGB: {forehead_rgb} -> Classified as: {detected_tone}")

        # Draw face box and label
        top, right, bottom, left = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, detected_tone, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        if len(skin_tone_samples) < SAMPLE_COUNT:
            skin_tone_samples.append(detected_tone)

    # Display count status
    cv2.putText(frame, f"Samples: {len(skin_tone_samples)}/{SAMPLE_COUNT}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    cv2.imshow("Skin Tone Detection", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    elif key == ord("r"):
        skin_tone_samples = []
        print("Sampling buffer reset.")

    # Once enough samples are collected
    if len(skin_tone_samples) == SAMPLE_COUNT:
        final_tone = max(set(skin_tone_samples), key=skin_tone_samples.count)
        wled_bucket = bucket_mapping.get(final_tone, "Bucket3")
        mqtt_message = f"PL={wled_bucket}"
        mqtt_client.publish(MQTT_TOPIC, mqtt_message)
        print(f"Sent MQTT command: {mqtt_message} to topic {MQTT_TOPIC}")
        skin_tone_samples = []  # Reset for next person

cv2.destroyAllWindows()
picam2.stop()
