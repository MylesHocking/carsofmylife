import requests

def fetch_wikimedia_images(search_query):
    print(f"Fetching images for {search_query} from Wikimedia API...")
    """
    Fetch images from Wikimedia API based on the search query.
    """
    # Wikimedia API endpoint for image search
    api_url = "https://commons.wikimedia.org/w/api.php"

    # Parameters for the API request
    params = {
        "action": "query",
        "format": "json",
        "prop": "imageinfo",
        "generator": "search",
        "gsrnamespace": 6,  # Namespace for files
        "gsrsearch": search_query,
        "gsrlimit": 10,  # Limit the number of results
        "iiprop": "url|extmetadata"  # Fetch URL and metadata
    }

    # Sending a GET request to the API
    response = requests.get(api_url, params=params)

    # Check if the response is successful
    if response.status_code == 200:
        return response.json()
    else:
        return f"Error: Unable to fetch data. Status Code: {response.status_code}"

# Test the function with the search query 'ford granada'
search_query = "ford granada"
wikimedia_images = fetch_wikimedia_images(search_query)

# Display a part of the fetched data for inspection
wikimedia_images.keys()  # Displaying the keys to understand the structure of the response

