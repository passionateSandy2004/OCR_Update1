import cv2
import numpy as np
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

def extract_header_fields(image_path):
    # Load the image
    image = cv2.imread(image_path)

    # Doctr OCR model
    ocr_model = ocr_predictor(pretrained=True)

    # Load the image and extract text using Doctr
    doc = DocumentFile.from_images(image_path)
    result = ocr_model(doc)

    # Extract the first page (assuming single page table)
    page = result.pages[0]

    # Parse the words and their bounding boxes
    words = [word.value for block in page.blocks for line in block.lines for word in line.words]
    boxes = [word.geometry for block in page.blocks for line in block.lines for word in line.words]

    # Convert boxes to a more usable format (x_min, y_min, x_max, y_max) in relative coordinates
    boxes = np.array([[(box[0][0], box[0][1]), (box[1][0], box[1][1])] for box in boxes])

    # Focus on top 15% of the image to find header
    image_height, image_width = image.shape[:2]
    header_cutoff = 0.15  # Adjust as needed
    header_indices = [i for i, box in enumerate(boxes) if box[0][1] < header_cutoff]

    # Extract words and boxes from the header area
    header_words = [words[i] for i in header_indices]
    header_boxes = [boxes[i] for i in header_indices]

    # Define thresholds for merging words
    horizontal_threshold = 0.05  # Adjust based on relative image width
    vertical_threshold = 0.05  # Adjust based on relative image height

    # Function to calculate the horizontal distance between two word boxes
    def horizontal_distance(box1, box2):
        x1 = (box1[1][0] + box1[0][0]) / 2
        x2 = (box2[1][0] + box2[0][0]) / 2
        return abs(x2 - x1)

    # Function to calculate the vertical distance between two word boxes
    def vertical_distance(box1, box2):
        y1 = (box1[1][1] + box1[0][1]) / 2
        y2 = (box2[1][1] + box2[0][1]) / 2
        return abs(y2 - y1)

    # Create an empty list for merged fields
    merged_fields = []

    # A boolean array to track which boxes are already merged
    merged = [False] * len(header_boxes)

    # Function to merge neighboring words recursively
    # Function to merge neighboring words recursively with a check for repeated words
    def merge_nearby_words(current_index):
        # Start a new field with the current word and box
        current_field = [header_words[current_index]]
        current_box = header_boxes[current_index]
        merged[current_index] = True

        # Continue searching for nearby words
        for j in range(len(header_boxes)):
            if merged[j]:
                continue
            
            # Calculate horizontal and vertical distances
            h_dist = horizontal_distance(current_box, header_boxes[j])
            v_dist = vertical_distance(current_box, header_boxes[j])
            
            # If the word is within both the horizontal and vertical thresholds, merge it
            if h_dist < horizontal_threshold and v_dist < vertical_threshold:
                # Check for repeating last word before merging
                if current_field[-1] == header_words[j]:
                    continue  # Skip if the last word is the same as the new word

                current_field.append(header_words[j])
                # Extend the current box to include the new word's box
                current_box = (
                    (min(current_box[0][0], header_boxes[j][0][0]), min(current_box[0][1], header_boxes[j][0][1])),
                    (max(current_box[1][0], header_boxes[j][1][0]), max(current_box[1][1], header_boxes[j][1][1]))
                )
                merged[j] = True
                # Recursively merge the nearby words of this word
                more_field, more_box = merge_nearby_words(j)
                current_field.extend(more_field)
                # Extend the current box further if more fields are merged
                current_box = (
                    (min(current_box[0][0], more_box[0][0]), min(current_box[0][1], more_box[0][1])),
                    (max(current_box[1][0], more_box[1][0]), max(current_box[1][1], more_box[1][1]))
                )

        return current_field, current_box

    # Iterate through all words and boxes in the header
    for i in range(len(header_boxes)):
        if merged[i]:
            continue  # Skip if the box is already merged

        # Merge nearby words recursively and get the final field and its box
        field_words, field_box = merge_nearby_words(i)
        merged_fields.append([(' '.join(field_words), field_box)])
    
    return merged_fields

# E