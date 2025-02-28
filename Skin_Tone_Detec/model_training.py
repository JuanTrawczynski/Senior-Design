import os
import cv2
import numpy as np
from imutils import paths
import face_recognition
import csv

# Path to dataset
DATASET_PATH = "dataset"
CSV_OUTPUT = "monk_skin_tones.csv"

def get_average_rgb(image, face_box):
    """
    Extracts the Region of Interest (ROI) and calculates the average RGB values.
    """
    (top, right, bottom, left) = face_box

    # Extract the face ROI
    face_roi = image[top:bottom, left:right]

    # Convert to RGB (OpenCV loads images in BGR format)
    face_roi = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)

    # Compute the mean RGB values
    avg_r = int(np.mean(face_roi[:, :, 0]))
    avg_g = int(np.mean(face_roi[:, :, 1]))
    avg_b = int(np.mean(face_roi[:, :, 2]))

    return avg_r, avg_g, avg_b

def process_dataset():
    """
    Processes all images in the dataset, extracts RGB values, and calculates the average per Monk Skin Tone.
    """
    skin_tone_data = {}

    # Loop through each Monk Skin Tone folder (monk_1, monk_2, ..., monk_10)
    for monk_tone in sorted(os.listdir(DATASET_PATH)):
        monk_path = os.path.join(DATASET_PATH, monk_tone)
        
        if not os.path.isdir(monk_path):
            continue

        image_paths = list(paths.list_images(monk_path))
        rgb_values = []

        for image_path in image_paths:
            print(f"[INFO] Processing {image_path}")

            # Load image
            image = cv2.imread(image_path)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Detect faces
            face_boxes = face_recognition.face_locations(rgb, model="hog")

            if len(face_boxes) > 0:
                avg_rgb = get_average_rgb(image, face_boxes[0])  # Process first detected face
                rgb_values.append(avg_rgb)

        # Compute average RGB values for this Monk Skin Tone category
        if rgb_values:
            avg_r = int(np.mean([rgb[0] for rgb in rgb_values]))
            avg_g = int(np.mean([rgb[1] for rgb in rgb_values]))
            avg_b = int(np.mean([rgb[2] for rgb in rgb_values]))

            skin_tone_data[monk_tone] = (avg_r, avg_g, avg_b)

    # Save to CSV file
    with open(CSV_OUTPUT, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Monk_Tone", "Avg_R", "Avg_G", "Avg_B"])
        for tone, rgb in skin_tone_data.items():
            writer.writerow([tone, rgb[0], rgb[1], rgb[2]])

    print(f"[INFO] Processing complete. Real RGB values saved to {CSV_OUTPUT}")

if __name__ == "__main__":
    process_dataset()
