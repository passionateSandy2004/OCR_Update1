import cv2
import numpy as np
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

# Function to calculate the distance between two bounding boxes
def box_distance(box1, box2):
    x1_min, y1_min = box1[0]
    x1_max, y1_max = box1[1]
    
    x2_min, y2_min = box2[0]
    x2_max, y2_max = box2[1]
    
    # Horizontal and vertical distance between boxes
    horizontal_dist = max(x2_min - x1_max, x1_min - x2_max, 0)
    vertical_dist = max(y2_min - y1_max, y1_min - y2_max, 0)
    
    return horizontal_dist, vertical_dist

# Main function to process image and return merged text and bounding boxes
def process_image_for_ocr(image_path):
    # Load the image
    image = cv2.imread(image_path)
    
    # OCR model (Doctr)
    ocr_model = ocr_predictor(pretrained=True)

    # Load the image and extract text using Doctr
    doc = DocumentFile.from_images(image_path)
    result = ocr_model(doc)

    # Extract the first page (assuming single page)
    page = result.pages[0]

    # Parse the words and their bounding boxes
    words = [word.value for block in page.blocks for line in block.lines for word in line.words]
    boxes = [word.geometry for block in page.blocks for line in block.lines for word in line.words]

    # Convert boxes to (x_min, y_min, x_max, y_max) in relative coordinates
    boxes = np.array([[(box[0][0], box[0][1]), (box[1][0], box[1][1])] for box in boxes])

    # Thresholds for proximity (relative to image size)
    horizontal_threshold = 0.004  # 0.4% of the image width
    vertical_threshold = 0.02     # 2% of the image height

    # A boolean array to track which boxes are already merged
    merged = [False] * len(boxes)

    # List to store merged fields and their bounding boxes
    merged_fields = []

    # Function to merge nearby boxes
    def merge_boxes(index):
        current_field = [words[index]]
        current_box = boxes[index]
        merged[index] = True
        
        for i in range(len(boxes)):
            if merged[i]:
                continue
            
            h_dist, v_dist = box_distance(current_box, boxes[i])
            
            if h_dist < horizontal_threshold and v_dist < vertical_threshold:
                current_field.append(words[i])
                # Extend the current box to include the new word's box
                current_box = (
                    (min(current_box[0][0], boxes[i][0][0]), min(current_box[0][1], boxes[i][0][1])),
                    (max(current_box[1][0], boxes[i][1][0]), max(current_box[1][1], boxes[i][1][1]))
                )
                merged[i] = True
        
        return ' '.join(current_field), current_box

    # Iterate over all words and boxes, merging nearby ones
    for i in range(len(boxes)):
        if not merged[i]:
            merged_field, merged_box = merge_boxes(i)
            merged_fields.append((merged_field, merged_box))

    # Convert boxes to absolute pixel values and return the result
    image_height, image_width = image.shape[:2]
    result_fields = []
    for field, box in merged_fields:
        # Convert relative coordinates to absolute pixel values
        top_left = (int(box[0][0] * image_width), int(box[0][1] * image_height))
        bottom_right = (int(box[1][0] * image_width), int(box[1][1] * image_height))

        # Draw bounding box on the image (optional)
        cv2.rectangle(image, top_left, bottom_right, (0, 255, 0), 2)  # Green box for each field
        
        # Append the field and absolute bounding box to result list
        result_fields.append((field, (top_left, bottom_right)))

    '''# Optionally display the image
    cv2.imshow("Merged Text Fields", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()'''

    return result_fields

# Example usa
