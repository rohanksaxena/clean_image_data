import cv2
import re
import argparse
from pathlib import Path
from imaging_interview import preprocess_image_change_detection, compare_frames_change_detection

MIN_CONTOUR_AREA = 1000
TOTAL_SCORE_THRESHOLD = 30000
RESOLUTION = (480, 640)


def get_image_data(data_root):
    """
    Get image data from the specified data root.

    Parameters:
        data_root (str): Path to the dataset.

    Returns:
        dict: A dictionary containing image data grouped by their camera IDs.
    """

    p = Path(data_root)
    img_list = list(p.glob("*.png"))

    image_data = {}
    for img in img_list:
        c_id = re.split("[-_]", str(img.stem))[0]
        if c_id not in image_data:
            image_data[c_id] = []
        image_data[c_id].append(img)

    return image_data


def remove_similar_images(image_data):
    """
    Remove similar images from the given dataset.

    Parameters:
        image_data (dict): A dictionary containing image data grouped by their camera IDs.

    Returns:
        list: A list of paths to the images that were removed during the process.
    """
    # Set to keep track of images to be removed
    removed_images = set()

    # Loop through individual image lists per camera
    for key, val in image_data.items():

        # First Pass
        i, j = 0, 1
        while j < len(val):
            if val[i] not in removed_images:
                try:
                    img1 = preprocess_image_change_detection(cv2.resize(cv2.imread(str(val[i])), RESOLUTION))
                    img2 = preprocess_image_change_detection(cv2.resize(cv2.imread(str(val[j])), RESOLUTION))
                except cv2.error:
                    i, j = j, j + 1
                    continue
                score, res_cnts, thresh = compare_frames_change_detection(img1, img2, MIN_CONTOUR_AREA)

                if score < TOTAL_SCORE_THRESHOLD:
                    removed_images.add(val[j])
                    j += 1
                else:
                    i, j = j, j + 1

        # Second pass
        for i in range(len(val)):
            if val[i] not in removed_images:
                try:
                    img1 = preprocess_image_change_detection(cv2.resize(cv2.imread(str(val[i])), RESOLUTION))
                except cv2.error:
                    continue
            else:
                continue
            for j in range(i + 1, len(val)):
                if val[j] not in removed_images:
                    try:
                        img2 = preprocess_image_change_detection(cv2.resize(cv2.imread(str(val[j])), RESOLUTION))
                    except cv2.error:
                        continue
                    score, res_cnts, thresh = compare_frames_change_detection(img1, img2, MIN_CONTOUR_AREA)
                    if score < TOTAL_SCORE_THRESHOLD:
                        removed_images.add(val[j])
                else:
                    continue
    return removed_images


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_root", type=str, help="Path to the dataset")
    args = parser.parse_args()

    if not args.data_root:
        raise ValueError("Please provide the path to the dataset using '--data_root' argument.")

    image_data = get_image_data(args.data_root)
    removed_images = remove_similar_images(image_data)

    # Delete the retrieved images
    for img_path in removed_images:
        img_path.unlink()
