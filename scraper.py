from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Car, GeneralCarImage  # Add GeneralCarImage to the imports
import requests
from bs4 import BeautifulSoup
import time

# Database setup
DATABASE_URI = "postgresql://postgres:J4sp3rw00@localhost/carsofmylife"  # Replace with your actual database URI
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def fetch_image_details(make, model):
    # Build the URL for Wikimedia Commons search
    search_url = f"https://commons.wikimedia.org/w/index.php?search={make}+{model}&title=Special:MediaSearch&go=Go&type=image"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    print(f"Searching...  {search_url} ...")
    # Find the image and attribution (replace 'some_class' and 'attribution_class' with actual classes)
    image = soup.find('img', {'class': 'some_class'})  # The class will likely be different
    attribution = soup.find('div', {'class': 'attribution_class'})  # Ditto
    
    image_url = image['src'] if image else None
    attribution_text = attribution.text if attribution else None
    return image_url, attribution_text

# Fetch unique make and model combinations from your database
unique_cars = session.query(Car.model_make_id, Car.model_name).distinct().all()

# Iterate through each unique make and model to fetch the image
for car in unique_cars:
    make = car.model_make_id
    model = car.model_name
    
    image_url, attribution_text = fetch_image_details(make, model)
    print(f"Searching for images for {make} {model} ...")
    print(f"Image URL: {image_url}")
    print(f"Attribution Text: {attribution_text}")
    if image_url:
        # Add new record to the GeneralCarImage table
        general_image = GeneralCarImage(model_id=car.model_id, web_image_url=image_url)
        session.add(general_image)
    
        # Commit the changes
        session.commit()
    
    # Wait a few seconds to respect rate limiting
    time.sleep(3)
