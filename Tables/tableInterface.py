from flask import Flask, request, jsonify
import os
import tableM as t
import json 
import LLMTableInter

app = Flask(__name__)

def combine_json_files(folder_path):
    combined_data = []

    # Loop through all files in the folder
    for filename in os.listdir(folder_path):
        # Check if the file is a JSON file
        if filename.endswith('.json'):
            file_path = os.path.join(folder_path, filename)
            
            # Open and load the JSON file
            with open(file_path, 'r') as file:
                data = json.load(file)
                
                # Check if data is a list and extend it
                if isinstance(data, list):
                    combined_data.extend(data)
                else:
                    combined_data.append(data)

    return combined_data
# Define the function to instantiate the table module with the image path
def Instance(path):
    print("Before Table")
    t.Table(path)
    print("After Table")

# Define the TableOcr function that processes the image path
def TableOcr(pathT):
    Instance(pathT)
    print("Before Response")
    response="done"
    return response

# Define the Flask route for POST request
@app.route('/table-ocr', methods=['POST'])
def process_image():
    try:
        # Extract the file path from the POST request
        data = request.json
        image_path = data.get('path')
        
        # Check if the file exists
        if not os.path.exists(image_path):
            return jsonify({'error': 'File does not exist'}), 400

        #TableM.py which -> find tables in the image(yolo) saves it , saved images are made ocr and saved as csv and json(Group of words made into one box and box position is saved in json with the group of word)
        res=TableOcr(image_path)
        print(res)
        # Return a success message
        return jsonify({'FolderPath': r"D:\OCR Models\Own model\Spacy Model\simpleTransformer\lm Connection\Tables\T"}), 200 #Replace it with Tables\T for your server

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, port=3000)


