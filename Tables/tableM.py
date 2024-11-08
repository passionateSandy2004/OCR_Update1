import os
import cv2
from ultralyticsplus import YOLO, render_result
import TableValues as tv
import JsonMaker
import json 

# Load model
model = YOLO('foduucom/table-detection-and-extraction')

# Set model parameters
model.overrides['conf'] = 0.1  # NMS confidence threshold
model.overrides['iou'] = 0.3  # NMS IoU threshold
model.overrides['agnostic_nms'] = True  # NMS class-agnostic
model.overrides['max_det'] = 1000  # maximum number of detections per image

def Table(image_path):
    # Set image
    image = cv2.imread(image_path)

    # Perform inference
    results = model.predict(image_path)

    # Create the output folder if not exists
    output_folder = r'T'
    os.makedirs(output_folder, exist_ok=True)

    # Process each detected table
    for i, result in enumerate(results[0].boxes):
        # Get bounding box coordinates (x1, y1, x2, y2)
        x1, y1, x2, y2 = map(int, result.xyxy[0])  # Ensures coordinates are integers
        
        # Crop the table from the image
        cropped_table = image[y1:y2, x1:x2]
        
        # Save the cropped table
        output_path = os.path.join(output_folder, f'Table_{i+1}.jpg')
        print("In loop")
        # Write the cropped image
        cv2.imwrite(output_path, cropped_table)
        
        # Save the table values to CSV and JSON
        csv_path = os.path.join(output_folder, f'Table_{i+1}.csv')
        json_path = os.path.join(output_folder, f'Table_{i+1}.json')
        json_path_pos = os.path.join(output_folder, f'Table_{i+1}_pos.json')
        
        word_pos=tv.values(output_path, csv_path)#Groups the words into one box 
        JsonMaker.mJson(csv_path, json_path)#Made for Future Recontruction , but not used in current version
        pos={
            "content":word_pos
        }
        with open(json_path_pos, 'w') as json_file:
            json.dump(pos, json_file, indent=4)#Here the positions of each sections of the table is stored with the positions 

    print(f"{len(results[0].boxes)} tables saved to {output_folder} folder.")

'''# Set image path
image = 'invoice 2.jpeg'

# Perform inference
results = Table(image)'''


