import cv2
import os
import numpy as np
import csv

# Dataset directory
DATASET_DIR = "dataset"
OUTPUT_CSV = "monk_skin_tones.csv"

def extract_rgb_samples(image_path):
    """ Extract multiple RGB values from different regions of the face. """
    img = cv2.imread(image_path)
    img = cv2.resize(img, (400, 400))  # Ensure consistency in size
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

    # Define ROI regions for sampling (forehead, cheeks, chin)
    h, w, _ = img.shape
    sample_regions = [
        (int(h * 0.2), int(w * 0.4)),  # Forehead center
        (int(h * 0.3), int(w * 0.2)),  # Left cheek
        (int(h * 0.3), int(w * 0.8)),  # Right cheek
        (int(h * 0.6), int(w * 0.4)),  # Chin center
    ]

    rgb_samples = []
    for y, x in sample_regions:
        sample_rgb = img_rgb[y, x]  # Extract RGB at sample point
        rgb_samples.append(sample_rgb)

    return rgb_samples

def process_dataset():
    """ Process dataset, extract multiple RGB values per Monk Skin Tone, and save to CSV. """
    monk_tone_data = []

    for monk_tone in sorted(os.listdir(DATASET_DIR)):  # Iterate over monk_1, monk_2, ..., monk_10
        monk_tone_dir = os.path.join(DATASET_DIR, monk_tone)

        if not os.path.isdir(monk_tone_dir):
            continue  # Skip if not a directory

        for subject in os.listdir(monk_tone_dir):  # Iterate over subject folders
            subject_dir = os.path.join(monk_tone_dir, subject)

            if not os.path.isdir(subject_dir):
                continue  # Skip non-folder files

            for img_file in os.listdir(subject_dir):  # Iterate over images
                img_path = os.path.join(subject_dir, img_file)

                try:
                    rgb_samples = extract_rgb_samples(img_path)

                    for rgb in rgb_samples:
                        monk_tone_data.append([monk_tone, rgb[0], rgb[1], rgb[2]])  # Save multiple samples

                except Exception as e:
                    print(f"Error processing {img_path}: {e}")

    # Save data to CSV
    with open(OUTPUT_CSV, "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["Monk_Tone", "R", "G", "B"])  # Header
        writer.writerows(monk_tone_data)

    print(f"Processing complete. Extracted RGB samples saved to {OUTPUT_CSV}.")

if __name__ == "__main__":
    process_dataset()
