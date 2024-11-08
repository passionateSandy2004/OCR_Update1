import requests
import re 

# Define the base URL of your LM Studio server
BASE_URL = "http://localhost:1234/v1"

def get_models():
    url = f"{BASE_URL}/models"
    try:
        response = requests.get(url)
        response.raise_for_status()
        models = response.json()
        return models
    except requests.exceptions.RequestException as e:
        print(f"Error fetching models: {e}")
        return None

def ask_question(model_id, question):
    url = f"{BASE_URL}/chat/completions"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": question}
        ],
        "max_tokens": 900,  # Adjust as needed
        "temperature": 1  # Adjust creativity as needed
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        completion = response.json()
        # Extract the assistant's reply
        answer = completion['choices'][0]['message']['content']
        plain_text = re.sub(r'[\n\t]', '', answer)
        start = plain_text[plain_text.find("```") + 3:]
        target = start[:start.find("```")]
        plain_text = target

        # Clean the plain text if necessary
        plain_text = re.sub(r'[\n\t]', '', plain_text)
        return target
    except requests.exceptions.RequestException as e:
        print(f"Error during completion: {e}")
        return None

def main(Tcontent):
    # Step 1: Get available models
    models = get_models()
    if models and "data" in models and len(models["data"]) > 0:
        # Choose the first model from the list or specify a model ID
        selected_model = models["data"][0]["id"]

        # Step 2: Ask a question
        user_question = f'''
            Here is a very messy and uncleaned OCR-generated JSON table. The data contains many inconsistencies, redundant, irrelevant, and repeated fields, as well as errors in formatting. The table is supposed to represent an invoice with item details, taxes, and amounts, but unrelated data may have been included.
            I need you to clean, improve, and transform the JSON by doing the following:
            Identify and remove irrelevant fields: Discard all fields and values that are unrelated to the invoice or item details (e.g., any random strings, extra information unrelated to the transaction).
            Fix key names and ensure consistency:
            Use clear and consistent key names that describe the item, its quantity, price, taxes, and amount. The relevant fields should include:
            "Item Name","Quantity","Unit","Price per Unit","Taxable Amount","CGST","SGST","Total Amount"
            Correct any misspelled or repeated keys, and ensure that similar fields are merged into one consistent key.
            Correct the values:
            Ensure that numerical fields (e.g., prices, quantities, amounts) are formatted correctly as numbers.
            Remove any extra characters, such as percentage signs or parentheses, that are not necessary unless part of the value (e.g., tax percentages).
            Ignore unrelated or unrelated table contents: Ensure the output only contains information about invoice items, taxes, and amounts. Discard everything else.
            Clean the structure:
            Organize the data logically, ensuring each entry contains the relevant item details (such as name, quantity, unit, price, taxes, and total amount).
            Remove duplicated information or unnecessary repetition in any fields.
            Format cleanly: Ensure the final output is in a well-structured, easy-to-read, and correct JSON format.
            Output format:
            The final cleaned JSON should follow this structure [
            {"Item Name": "value", "Quantity": "value", "Unit": "value", "Price per Unit": "value", "Taxable Amount": "value", "CGST": "value", "SGST": "value", "Total Amount": "value"},
            ...
            ]
            the ocr result:
            {Tcontent}
        '''
        res=ask_question(selected_model, user_question)
        print("Table Response:\n",res)
        return res
    else:
        print("No models available to use.")
