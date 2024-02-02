import requests
from xml.etree import ElementTree as ET
import re
import os
from dotenv import load_dotenv

load_dotenv()


# Replace 'url_to_scrape' with the URL of the webpage you want to scrape
url_to_scrape = os.getenv('SITEMAP_URL')

# Extract the title from the URL ending and clean it
def get_title_from_url_ending(url_ending):

    # Check if ends with slash
    if url_ending.endswith('/'):
        title = url_ending.split('/')[-2].replace('-', ' ').title()
    else:
        title = url_ending.split('/')[-1].replace('-', ' ').title()
    
    return title

# Send an HTTP GET request to the sitemap URL
response = requests.get(url_to_scrape)

# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse the XML content of the sitemap
    root = ET.fromstring(response.text)

    # Extract URLs from the sitemap along with their image URLs and titles (if available)
    urls_with_images = []
    for url_elem in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url'):
        loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        image_elem = url_elem.find('.//{http://www.google.com/schemas/sitemap-image/1.1}image')
        
        url = loc_elem.text
        image_url = image_elem.find('{http://www.google.com/schemas/sitemap-image/1.1}loc').text if image_elem is not None else None
        image_title_elem = image_elem.find('{http://www.google.com/schemas/sitemap-image/1.1}title')
        image_title = image_title_elem.text if image_title_elem is not None else get_title_from_url_ending(url)

        if not re.search(r'test[\d]*|testing', image_title, flags=re.IGNORECASE):
            urls_with_images.append({'url': url, 'image_url': image_url, 'image_title': image_title})

    # Write the extracted data to a CSV file
    data = 'url,image_url,title\n' + ''.join([f"{url_with_image['url']},{url_with_image['image_url']},{url_with_image['image_title']}\n" for url_with_image in urls_with_images])
    with open('sitemap_data.csv', 'w') as file:
        file.write(data)
    
else:
    print(f"Failed to retrieve the sitemap. Status code: {response.status_code}")
    
