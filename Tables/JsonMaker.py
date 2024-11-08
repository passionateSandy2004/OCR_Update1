import pandas as pd
def mJson(inpath,outpath):
    # Load the CSV file
    csv_file_path = inpath
    df = pd.read_csv(csv_file_path)

    # Convert the DataFrame to JSON format
    json_data = df.to_json(orient='records', indent=4)

    # Optionally, you can save it to a file:
    with open(outpath, 'w') as json_file:
        json_file.write(json_data)
