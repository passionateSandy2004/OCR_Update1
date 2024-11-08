import streamlit as st 
import main 
import streamlit as st 
from doctr.io import DocumentFile
from doctr.models import ocr_predictor
import re
import json
import requests
import AllTables
#TableInterface.py 
def call_table_ocr_api(image_path):
    url = 'http://127.0.0.1:3000/table-ocr'  # URL of the Flask API

    # Prepare the JSON payload
    payload = {
        'path': image_path
    }

    try:
        # Send a POST request to the API
        response = requests.post(url, json=payload)

        # Check if the request was successful
        if response.status_code == 200:
            print("Success:", response.json())
            return response.json()
        else:
            print("Error:", response.status_code, response.json())
    
    except requests.exceptions.RequestException as e:
        print("Request failed:", str(e))

def BestTable(path):
    # Define the URL of the Flask API
    url = 'http://127.0.0.1:2000/invoice-table'

    # Data to be sent in the POST request
    data = {
        'path': path  # Replace this with the actual file path
    }

    # Send the POST request
    response = requests.post(url, json=data)

    # Check the response
    if response.status_code == 200:
        # Success, print the returned list of dictionaries
        print("Response Data:", response.json())
        return response.json()
    else:
        # Error, print the error message
        print("Error:", response.status_code, response.text)

def clean_text(text):
    cleaned_text = re.sub(r'[^\x00-\x7F]+', ' ', text)  # Removing non-ASCII characters
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text)  # Remove excess whitespace
    return cleaned_text
pic=st.file_uploader("Image:")
if pic:
    # Save the uploaded file temporarily
    temp_file_path = "temp_image1.jpg"  # You can give it any name with the correct extension
    
    # Write the uploaded image to a temporary file
    with open(temp_file_path, "wb") as f:
        f.write(pic.getbuffer())
    
    #Find Tables and Made into Json and return the main folder contains all the table jsons 
    TableFolder=call_table_ocr_api(r"D:\OCR Models\Own model\Spacy Model\simpleTransformer\lm Connection\temp_image1.jpg")
    InvTable=BestTable(TableFolder)
    l=AllTables.GiveTheTable()#The function takes all files in Table/T get the json file(where group of words are stored with positions) and with the positions made into rows 
    for i in l:
        st.write("---")
        st.write("Found Table\n")
        for row in i:    
            st.write(", ".join(row))
        st.write("---")
    doc = DocumentFile.from_images("temp_image1.jpg")

    #Normal OCR with LM Studio Connection from main.main()
    # Initialize OCR model
    model = ocr_predictor(pretrained=True)

    # Perform OCR
    result = model(doc)

    # Get the extracted text
    extracted_text = result.render() 
    cleanData=clean_text(extracted_text)
    print(cleanData)
    jsond=main.main(cleanData)
    st.write(jsond)
    if "json" in jsond:
        jsond=jsond.replace("json","")
    parsed_json = json.loads(jsond)
    pretty_json = json.dumps(parsed_json, indent=4)
    
    st.write(f"```json\n{pretty_json}\n```")
    file_path = "output.json"
    with open(file_path, "w") as json_file:
        json_file.write(pretty_json)