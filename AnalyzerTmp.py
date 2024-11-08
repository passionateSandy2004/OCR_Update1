'''
before running this module , make sure to host the api given in file Tables/TableInterface.py, just by running the file TableInterface.py
'''


import AllTables
import requests 
def call_table_ocr_api(image_path):

    '''
        In the file Tables/TableInterface host the api for the process, the process is explained:
            1.tableInterface(input: invoice image path) module pass the image to the tableM module.
            2.tableM makes 3 processes 1.find table in image 2.find every sections of the table(ocr and algorithm) with there positions 3.the group of section values with positions are stored in a json file(ends with _pos.json)
                example:
                    s.no|| Item Name|| Qty ||Price and Gst||
                    1.  || Shirt    ||  1  || 2000+250    ||
                if this is the table the algorithm finds the section and position of the value and stores in json file like below
                    s.no :[200,400],
                    Item Name:[500,400]
                    Qty:[800,395]
                    Price and Gst:[900, 410]
            3.returns the folder where all the json file of the every table with poitions are stored 
    '''
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

TableFolder=call_table_ocr_api(r"D:\OCR Models\Own model\Spacy Model\simpleTransformer\lm Connection\temp_image1.jpg")
l=AllTables.GiveTheTable()#The function takes all files in Table/T get the json file(where group of words are stored with positions) and with the positions the values are made into rows (which is the digital table)
table=[]
for i in l:
    rowValue=[]
    for row in i:    
        rowValue.append(", ".join(row))
    table.append([rowValue])
print(table)#this table is sent to any llm that we discussed 
'''
The output may look like this :
    [
        ['Bill To :, AKA INFRA PROJECTS, Ship To :, AKA INFRA PROJECTS, Invoice No:, M264-24/ 408302413', 'DESK NO 265, 4/608VOC STREET, OMR ROAD,, DESK NO 265, 4/608VOC STREET, OMR ROAD, NEHRU NAGAR, KOTTIVAKKAMACHENNAL CHENNAI-600041, Invoice Date :, 8-Jun-2024', 'NEHRU NAGAR, ROTTIVAKAM.CHENNA, Date : Delivery, 08-Jun-2024', 'CHENNAI600041', 'State Code:, 33, State Code :, 33, Payment Type:, Credit', 'State :, Tamil Nadu, State : 33AAFP27408/1ZB Tamil Nadu, Sales Executive : PANDI STAFF MURUGAN.M s Nimber: 408103261', 'GSTIN3SAAFP274081Z8, GSTIN :', '9845888804, 9845888804'],
        ['S. No, ItemName, HSN, Qty, Price, CGST, SGST, IGST, Total', '1, ATOMBERG FAN 48 STUDIO PLUS EARTH BROWN, 84145120, 3, 4,067.80, 9%, 9%, 0%, 12,203.40'],
        ['Invoice, No., Dated', 'SHB/456/20, 20-Dec-20', 'Delivery, Note, Mode/lerms, of, Payment', 'Reference, No. &, Date., Other, References', "Buyer's, Order No., Dated", 'Dispatch, Doc, No., Delivery, Note, Date', 'Dispatched, through, Destination']
    ]
    for all the table found in the image has made into digital tables our required table is 
        'S. No, ItemName, HSN, Qty, Price, CGST, SGST, IGST, Total'
        '1, ATOMBERG FAN 48 STUDIO PLUS EARTH BROWN, 84145120, 3, 4,067.80, 9%, 9%, 0%, 12,203.40'
    which is found in the 2nd position of the output 
'''