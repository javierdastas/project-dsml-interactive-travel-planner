# Data Pre-Processing 
#   1. Extracting ZIP files.
#   2. Reading and cleaning HTML.
#   3. Structuring data into a readable and organized format.
#   4. Exporting to JSON or CSV for use in further steps.

import os
import zipfile
import json
import pandas as pd
from bs4 import BeautifulSoup

# Function to extract ZIP files
def extract_zip(zip_path, extract_path):
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

# Function to clean HTML and extract useful information
def clean_html_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')
        
        # Extract title
        title = soup.title.string if soup.title else "No Title"
        
        # Extract significant paragraphs
        paragraphs = [p.get_text() for p in soup.find_all('p')]
        main_content = "\n".join(paragraphs[:5])  # Limit to the first 5 relevant paragraphs
        
        return {"title": title, "content": main_content}

# Function to process all files in a folder
def process_files_in_folder(folder_path):
    processed_data = []
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith('.txt'):
            data = clean_html_content(file_path)
            data["file_name"] = file_name  # Add the file name for reference
            processed_data.append(data)
    return processed_data

# Function to save processed data in JSON or CSV format
def save_data(processed_data, output_path, output_format="json"):
    if output_format == "json":
        with open(output_path, 'w', encoding='utf-8') as json_file:
            json.dump(processed_data, json_file, ensure_ascii=False, indent=4)
    elif output_format == "csv":
        df = pd.DataFrame(processed_data)
        df.to_csv(output_path, index=False, encoding='utf-8')
        
# File Path
dir_path = '../data/'

# Input and output paths
landmarks_zip_path = f'{dir_path}landmarks.zip'
municipalities_zip_path = f'{dir_path}municipalities.zip'
landmarks_extracted_path = f'{dir_path}landmarks/'
municipalities_extracted_path = f'{dir_path}municipalities/'
landmarks_output_path = f'{dir_path}processed_landmarks.json'
municipalities_output_path = f'{dir_path}processed_municipalities.json'

# Main process
if __name__ == "__main__":
    # Extract datasets
    extract_zip(landmarks_zip_path, landmarks_extracted_path)
    extract_zip(municipalities_zip_path, municipalities_extracted_path)

    # Process landmarks
    landmarks_folder = os.path.join(landmarks_extracted_path, 'landmarks')
    landmarks_data = process_files_in_folder(landmarks_folder)
    save_data(landmarks_data, landmarks_output_path, output_format="json")

    # Process municipalities
    municipalities_folder = os.path.join(municipalities_extracted_path, 'municipalities')
    municipalities_data = process_files_in_folder(municipalities_folder)
    save_data(municipalities_data, municipalities_output_path, output_format="json")

    print(f"Processing completed. Data saved at:\n- {landmarks_output_path}\n- {municipalities_output_path}")
