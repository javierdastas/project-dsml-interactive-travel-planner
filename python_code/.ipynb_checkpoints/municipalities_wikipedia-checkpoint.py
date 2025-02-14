import requests
from bs4 import BeautifulSoup
import csv
import os  # Para extraer el nombre de archivo

def get_puerto_rico_municipalities_data():
    url = "https://en.wikipedia.org/wiki/List_of_municipalities_of_Puerto_Rico"

    # Make an HTTP GET request to the Wikipedia page
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error accessing the page, status code: {response.status_code}"

    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.content, "html.parser")

    # Find the table containing the municipalities
    table = soup.find("table", class_="wikitable")
    if not table:
        return "Error: Could not find the table of municipalities."

    # List to store data about each municipality
    municipalities_data = []

    # Extract data row by row (skip the header row)
    rows = table.find_all("tr")[1:]
    for row in rows:
        columns = row.find_all("td")
        if columns:
            # Municipality name
            municipality_name = columns[0].get_text(strip=True)

            # Location (map URL name)
            map_link = columns[1].find("a")["href"] if columns[2].find("a") else None
            location_name = os.path.basename(map_link) if map_link else "N/A"

            # Flag (extract image filename)
            flag_img = columns[2].find("img")
            flag_filename = os.path.basename(flag_img["src"]) if flag_img else "N/A"

            # Coat of arms (extract image filename)
            coat_of_arms_img = columns[3].find("img")
            coat_of_arms_filename = os.path.basename(coat_of_arms_img["src"]) if coat_of_arms_img else "N/A"

            # Append the extracted data
            municipalities_data.append({
                "Name": municipality_name,
                "Location": location_name,
                "Flag": flag_filename,
                "Coat of Arms": coat_of_arms_filename
            })

    return municipalities_data

def save_to_csv(data, filename="../datasets/municipalities_of_puerto_rico.csv"):
    # Column names for the CSV
    headers = ["Name", "Location", "Flag", "Coat of Arms"]

    # Write data to CSV
    with open(filename, mode="w", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)

    print(f"Data successfully saved to {filename}")

if __name__ == "__main__":
    municipalities_data = get_puerto_rico_municipalities_data()
    if isinstance(municipalities_data, list):
        save_to_csv(municipalities_data)
    else:
        print(municipalities_data)  # Print the error message if any
