import requests
import json

def fetch_image_details_via_api(make, model):
    search_query = f"{make} {model}"
    url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch={search_query}&utf8=1&formatversion=2"
    print('searching...'+url)
    response = requests.get(url)
    data = json.loads(response.text)
    
    image_details = []
    for item in data.get('query', {}).get('search', []):
        title = item.get('title', '')
        image_details.append({
            'title': title,
            'page_url': f"https://commons.wikimedia.org/wiki/{title}"
        })
    
    return image_details

# Replace with your actual make and model
make = 'Ford'
model = 'Granada'
image_details = fetch_image_details_via_api(make, model)

print(image_details)
