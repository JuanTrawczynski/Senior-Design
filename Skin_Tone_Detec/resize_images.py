import cv2
import os

# Path to the dataset folder
DATASET_PATH = "/home/chroma/Desktop/Face Recognition/dataset"

# Desired image size
IMG_SIZE = (400, 400)

def resize_images():
    # Iterate through monk_1 to monk_10
    for monk_folder in sorted(os.listdir(DATASET_PATH)):
        monk_path = os.path.join(DATASET_PATH, monk_folder)

        # Ensure it's a directory
        if os.path.isdir(monk_path):
            print(f"Resizing images in {monk_folder}...")

            # Iterate through subject folders
            for subject_folder in os.listdir(monk_path):
                subject_path = os.path.join(monk_path, subject_folder)

                if os.path.isdir(subject_path):
                    # Iterate through all images in subject folder
                    for img_name in os.listdir(subject_path):
                        img_path = os.path.join(subject_path, img_name)

                        # Check if the file is an image
                        if img_name.lower().endswith((".jpg", ".jpeg", ".png")):
                            try:
                                # Read the image
                                img = cv2.imread(img_path)

                                # Resize the image to 400x400
                                resized_img = cv2.resize(img, IMG_SIZE)

                                # Overwrite the original image
                                cv2.imwrite(img_path, resized_img)

                            except Exception as e:
                                print(f"Error processing {img_name}: {e}")

    print("All images have been resized to 400x400 pixels.")

if __name__ == "__main__":
    resize_images()
