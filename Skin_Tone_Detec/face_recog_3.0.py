import face_recognition
import cv2
import numpy as np
import csv
import time
import requests
from picamera2 import Picamera2
from libcamera import controls
from collections import Counter

# Configurations
TUNING_FILE = "/home/chroma/Arducam-477P-Pi4.json"
CSV_PATH = "/home/chroma/Desktop/Face Recognition/monk_skin_tones.csv"
SAMPLE_COUNT = 7

# Two ESP32 WLED targets
WLED_IPS = ["192.168.1.231", "192.168.1.233"]

# Mapping monk tones to buckets
bucket_mapping = {
    "monk_1": "Bucket1", "monk_2": "Bucket1",
    "monk_3": "Bucket2", "monk_4": "Bucket2",
    "monk_5": "Bucket3", "monk_6": "Bucket3",
    "monk_7": "Bucket4", "monk_8": "Bucket4",
    "monk_9": "Bucket5", "monk_10": "Bucket5",
}

# Preset mapping for both ESP32s (same)
bucket_to_preset_id = {
    "Bucket1": 1,
    "Bucket2": 2,
    "Bucket3": 3,
    "Bucket4": 4,
    "Bucket5": 5,
}

def send_preset(preset_id):
    for ip in WLED_IPS:
        try:
            response = requests.get(f"http://{ip}/win&PL={preset_id}", timeout=2)
            print(f"[HTTP] Sent preset {preset_id} to {ip} (Status {response.status_code})")
        except Exception as e:
            print(f"[HTTP] Error sending to {ip}: {e}")

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

def classify_skin_tone(face_rgb, reference_rgb):
    min_distance = float("inf")
    closest_tone = None
    for tone, samples in reference_rgb.items():
        for ref_rgb in samples:
            dist = np.linalg.norm(np.array(face_rgb) - np.array(ref_rgb))
            if dist < min_distance:
                min_distance = dist
                closest_tone = tone
    return closest_tone

def initialize_camera():
    picam2 = Picamera2(tuning=TUNING_FILE)
    config = picam2.create_preview_configuration(main={"size": (1280, 960)})
    picam2.configure(config)
    picam2.start()
    return picam2

def get_average_face_rgb(frame, face_location):
    (top, right, bottom, left) = face_location
    face_roi = frame[top:bottom, left:right]
    h, w, _ = face_roi.shape
    forehead_roi = face_roi[:int(h * 0.4), :]
    avg_r = int(np.mean(forehead_roi[:, :, 0]))
    avg_g = int(np.mean(forehead_roi[:, :, 1]))
    avg_b = int(np.mean(forehead_roi[:, :, 2]))
    return (avg_r, avg_g, avg_b)

MONK_SKIN_TONES = load_monk_skin_tones(CSV_PATH)
picam2 = initialize_camera()

classification_buffer = []
sampling_active = True
last_detected_tone = "monk_?"

print("Press 'R' to reset. Press 'Q' to quit.")

while True:
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    small_locations = face_recognition.face_locations(small_frame, model="hog")
    face_locations = [(top*2, right*2, bottom*2, left*2) for (top, right, bottom, left) in small_locations]

    for face_location in face_locations:
        (top, right, bottom, left) = face_location
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 3)

        if sampling_active:
            avg_rgb = get_average_face_rgb(frame, face_location)
            tone = classify_skin_tone(avg_rgb, MONK_SKIN_TONES)
            classification_buffer.append(tone)
            last_detected_tone = tone
            print(f"Sample {len(classification_buffer)}: {avg_rgb} -> {tone}")

            if len(classification_buffer) == SAMPLE_COUNT:
                most_common = Counter(classification_buffer).most_common(1)[0][0]
                bucket = bucket_mapping.get(most_common, "Unknown")
                preset_id = bucket_to_preset_id.get(bucket)

                if preset_id:
                    send_preset(preset_id)
                else:
                    print(f"[HTTP] Unknown bucket mapping for: {most_common}")

                sampling_active = False
        else:
            cv2.putText(frame, "WAITING FOR RESET", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)

        cv2.putText(frame, last_detected_tone, (left + 6, bottom + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow("Skin Tone Detection", frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord("q"):
        break
    elif key == ord("r"):
        classification_buffer.clear()
        sampling_active = True
        print("Sampling reset.")
        send_preset(6)  # Send Boot state to both ESP32s

cv2.destroyAllWindows()
picam2.stop()
