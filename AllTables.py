import os
import json

def read_pos_json_files(folder_path):
    main_list = []
    
    # Iterate through all files in the specified folder
    for file_name in os.listdir(folder_path):
        # Check if the file ends with '_pos.json'
        if file_name.endswith('_pos.json'):
            file_path = os.path.join(folder_path, file_name)
            
            # Open and read the json file
            with open(file_path, 'r') as json_file:
                data = json.load(json_file)
                
                # Check if the json structure has the 'content' key and it's a list
                if 'content' in data and isinstance(data['content'], list):
                    main_list.extend([data['content']])
    
    return main_list

def extract_rows(ocr_data):
    # Thresholds to consider items as part of the same row and to merge columns
    row_threshold = 20  # Adjust based on the height of the text boxes
    merge_x_threshold = 5# Threshold to merge columns horizontally if they are close

    # Step 1: Sort the OCR data by the Y-coordinate (top of bounding box)
    sorted_ocr = sorted(ocr_data, key=lambda x: x[1][0][1])  # Sort by the top Y coordinate of each item
    
    rows = []
    current_row = []
    previous_y = None

    # Step 2: Group elements into rows based on Y-coordinate proximity
    for item in sorted_ocr:
        item_name, ((x1, y1), (x2, y2)) = item

        if previous_y is None:
            # Initialize the first row
            previous_y = y1
            current_row.append(item)
        else:
            # Check if this item belongs to the same row based on Y-coordinate difference
            if abs(y1 - previous_y) <= row_threshold:
                current_row.append(item)
            else:
                # Start a new row
                rows.append(sorted(current_row, key=lambda x: x[1][0][0]))  # Sort current row by X-coordinate
                current_row = [item]
                previous_y = y1

    # Append the last row
    if current_row:
        rows.append(sorted(current_row, key=lambda x: x[1][0][0]))

    # Step 3: Merge adjacent columns in each row that are close on X but don't overlap vertically
    final_result = []
    for row in rows:
        merged_row = []
        i = 0
        while i < len(row):
            item_name, ((x1, y1), (x2, y2)) = row[i]
            j = i + 1
            
            # Check if the next box is close on the x-axis and doesn't overlap vertically
            while j < len(row):
                next_item_name, ((next_x1, next_y1), (next_x2, next_y2)) = row[j]
                
                # If they are close horizontally (small gap) and don't overlap vertically
                if next_x1 - x2 <= merge_x_threshold and abs(y1 - next_y1) <= row_threshold:
                    # Merge the two items (concatenate their names)
                    item_name += " " + next_item_name
                    x2 = next_x2  # Extend the bounding box to include the next item
                    j += 1
                else:
                    break
            
            # Add the merged (or single) item to the merged row
            merged_row.append(item_name)
            i = j

        final_result.append(merged_row)

    return final_result

'''
# Sample OCR input
ocr_data = [['ItemName', [[245, 15], [325, 32]]], ['Price', [[689, 11], [732, 28]]], ['CGST', [[793, 9], [842, 29]]], ['SGST', [[871, 7], [921, 25]]], ['IGST', [[942, 5], [986, 23]]], ['Total', [[1069, 2], [1116, 19]]], ['S. No', [[19, 15], [65, 36]]], ['HSN', [[519, 13], [555, 32]]], ['Qty', [[601, 13], [635, 33]]], ['0%', [[948, 42], [977, 59]]], ['12,203.40', [[1094, 37], [1176, 58]]], ['1', [[35, 54], [49, 72]]], ['ATOMBERG FAN 48 STUDIO PLUS EARTH BROWN', [[84, 51], [403, 68]]], ['84145120', [[498, 49], [579, 68]]], ['3', [[614, 45], [628, 64]]], ['4,067.80', [[705, 49], [775, 65]]], ['9%', [[806, 46], [834, 64]]], ['9%', [[880, 43], [909, 61]]]]

# Apply the algorithm to extract and merge rows
structured_data = extract_rows(ocr_data)
print()
'''



# The function checks the position of every section and rearrange it to correct row and column :
def GiveTheTable():
    folder_path = r'D:\OCR Models\Own model\Spacy Model\simpleTransformer\lm Connection\Tables\T'
    result = read_pos_json_files(folder_path)
    structured_lists=[]
    for i in result:
        structured_data = extract_rows(i)
        structured_lists.append(structured_data)
    return structured_lists