import TableHeader as TH 
import TableContent as TC 

import csv
import cv2
import numpy as np

# Function to check if two boxes overlap or touch
def boxes_overlap(box1, box2):
    (x1_min, y1_min), (x1_max, y1_max) = box1
    (x2_min, y2_min), (x2_max, y2_max) = box2

    # Check if one rectangle is on the left side of the other
    if x1_max < x2_min or x2_max < x1_min:
        return False
    # Check if one rectangle is above the other
    if y1_max < y2_min or y2_max < y1_min:
        return False

    return True

# Function to extend the header box downwards to the bottom of the image
def extend_box_downwards(box, image_height):
    (x_min, y_min), (x_max, y_max) = box
    return ((x_min, y_min), (x_max, image_height))

# Main code to process and create the CSV
def create_csv_from_boxes(header, content, image_path, csv_filename="output.csv"):
    # Load the image using OpenCV to get its dimensions
    image = cv2.imread(image_path)
    image_height, image_width, _ = image.shape

    # Create a dictionary to store the values for each column (header)
    csv_data = {}
    
    # Loop through each header and extend its box downwards
    for header_field in header:
        # Extract header name and box geometry
        header_name = header_field[0][0]
        header_box = header_field[0][1]

        # Convert numpy array (header box) to pixel coordinates
        if isinstance(header_box, np.ndarray):
            header_box = header_box.tolist()

        # Convert normalized header box coordinates (0 to 1 range) to actual pixel values
        header_box_px = (
            (header_box[0][0] * image_width, header_box[0][1] * image_height),
            (header_box[1][0] * image_width, header_box[1][1] * image_height)
        )

        extended_box = extend_box_downwards(header_box_px, image_height)

        # Initialize an empty list for each header column
        csv_data[header_name] = []

        # Loop through each content box and check if it overlaps with the extended header box
        for content_name, content_box in content:
            if boxes_overlap(extended_box, content_box):
                csv_data[header_name].append(content_name)

    # Write the results to a CSV file
    with open(csv_filename, mode='w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        # Write the header
        writer.writerow(csv_data.keys())

        # Find the maximum number of rows any column has (for consistent CSV rows)
        max_rows = max(len(values) for values in csv_data.values())

        # Write the rows
        for i in range(max_rows):
            row = []
            for column in csv_data.keys():
                if i < len(csv_data[column]):
                    row.append(csv_data[column][i])
                else:
                    row.append("")  # Empty cell if no value
            writer.writerow(row)

# Example usage with the provided output data
def values(image_path, output_path):
    header = TH.extract_header_fields(image_path)
    content = TC.process_image_for_ocr(image_path)
    print("Content: ",content)
    # Create CSV from header and content boxes
    create_csv_from_boxes(header, content, image_path, csv_filename=output_path)
    return content
