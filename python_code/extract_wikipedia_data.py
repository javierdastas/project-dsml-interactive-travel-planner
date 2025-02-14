import requests
from bs4 import BeautifulSoup
import re
import os

from .convert_coordinates import convert_coordinates

def extract_wikipedia_data(municipality, paragraphs_count=2):
    
    url = (f"https://en.wikipedia.org/wiki/{municipality},_Puerto_Rico")
    
    # Make the HTTP request to the given URL
    response = requests.get(url)
    if response.status_code != 200:
        return f"Error accessing the page, status code: {response.status_code}"

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.content, "html.parser")

    # 1. Extract the title of the page
    def get_title():
        title_span = soup.find("span", class_="mw-page-title-main")
        return title_span.text.strip() if title_span else "Title not found"

    # 2. Extract all general paragraphs in the main content
    def get_general_paragraphs():
        content_div = soup.select_one("#mw-content-text > div.mw-parser-output")
        if content_div:
            paragraphs = content_div.find_all("p")
            return [clean_content(p.get_text(separator=' ', strip=True)) for p in paragraphs if p.get_text(strip=True)]
        return []

    # Extract paragraphs and lists between sections
    def get_paragraphs_and_lists_between_sections(start_id):
        content_div = soup.select_one("#mw-content-text > div.mw-parser-output")
        if not content_div:
            return []

        paragraphs_and_lists = []
        capture = False
        
        for element in content_div.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'div']):
            if start_id in element.get_text():
                capture = True
                continue

            if element.name == 'h2' and capture:
                break

            if capture and element.name == 'p':
                text = clean_content(element.get_text(separator=' ', strip=True))
                if text:
                    paragraphs_and_lists.append(text)

            if capture and element.name in ['ul', 'ol']:
                list_items = [clean_content(li.get_text(separator=' ', strip=True)) for li in element.find_all('li')]
                list_items = list(filter(bool, list_items))
                if list_items:
                    formatted_list = "\n  - " + "\n  - ".join(list_items)
                    paragraphs_and_lists.append(formatted_list)

        return paragraphs_and_lists[:paragraphs_count]

    # Clean the text by removing unwanted references, tags, and extra spaces
    def clean_content(text):
        # Replace accented characters and special cases
        replacements = {
            'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
            'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
            'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U'
        }
        
        # Replace each character in the dictionary
        for accented_char, replacement_char in replacements.items():
            text = text.replace(accented_char, replacement_char)
        
        # Remove references like [1], [ 99 ], etc.
        text = re.sub(r'\[\s*[a-z0-9]*\s*\]', '', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text)
        
        # Return cleaned text
        return text.strip()

    # 3. Extract paragraphs and lists in the "Tourism" section
    def get_tourism_content():
        return get_paragraphs_and_lists_between_sections("Tourism")

    # 4. Extract paragraphs and lists in the "Culture" section
    def get_culture_content():
        return get_paragraphs_and_lists_between_sections("Culture")

    # 5. Extract latitude and longitude
    def get_coordinates():
        latitude = soup.select_one(".latitude")
        longitude = soup.select_one(".longitude")
        return (latitude.text.strip() if latitude else "Latitude not found",
                longitude.text.strip() if longitude else "Longitude not found")

    # Generate output content
    output = []

    title = get_title()

    json_ouput = {
                "content": '',
                "metadata": {
                    "type": 'city',
                    "city": municipality,
                    "name": municipality,
                    "categories": [],
                    "url": url,
                    "image_url": ''
                }
            }

    # Town title
    output.append(f"1. Town:\n{title}")

    # General Information
    general_info = get_general_paragraphs()
    if general_info:
        output.append("\n2. General Information:")
        output.extend(general_info)

        paragraphs_str = ' '.join(general_info[:paragraphs_count]) 

        json_ouput['content'] = paragraphs_str

    # Tourism Section
    tourism_content = get_tourism_content()
    if tourism_content:
        output.append("\n3. Tourism:")
        output.extend(tourism_content)

        tourism_content_str = ' '.join(tourism_content) 
        json_ouput['content'] += (f' Tourism in {municipality}: {tourism_content_str}')

    # Culture Section
    culture_content = get_culture_content()
    if culture_content:
        output.append("\n4. Culture:")
        output.extend(culture_content)

        culture_content_str = ' '.join(culture_content)
        json_ouput['content'] += (f' Culture in {municipality}: {culture_content_str}')

    # Geographic Coordinates
    latitude_dms, longitude_dms = get_coordinates()

    # Convert to decimal coordinates using CoordinatesConverter
    latitude, longitude = convert_coordinates(latitude_dms, longitude_dms)
    
    output.append("\n5. Geographic coordinates:")
    output.append(f"Latitude: {latitude}")
    output.append(f"Longitude: {longitude}")

    json_ouput['metadata']['latitude'] = latitude
    json_ouput['metadata']['longitude'] = longitude

    # Return the result as a single string
    # return "\n".join(output)
    return json_ouput

