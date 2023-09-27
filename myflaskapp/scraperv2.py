from sqlalchemy import create_engine, insert
from sqlalchemy.orm import sessionmaker
from app.models import Car, GeneralCarImage  # Add GeneralCarImage to the imports
import requests
from bs4 import BeautifulSoup
import time

# Database setup
DATABASE_URI = "postgresql://postgres:J4sp3rw00@localhost/carsofmylife"
engine = create_engine(DATABASE_URI)
Session = sessionmaker(bind=engine)
session = Session()

def fetch_image_details(make, model, trim, year, body, engine_cc):
    search_terms = [make, model, trim, year, body, engine_cc]
    search_string = "+".join([str(term) for term in search_terms if term])
    search_url = f"https://commons.wikimedia.org/w/index.php?search={search_string}&title=Special:MediaSearch&go=Go&type=image"
    
    print(f"Searching...  {search_url} ...")

    response = requests.get(search_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find the image and attribution (replace 'some_class' and 'attribution_class' with actual classes)
    image = soup.find('img', {'class': 'some_class'})  # The class will likely be different
    attribution = soup.find('div', {'class': 'attribution_class'})  # Ditto
    
    image_url = image['src'] if image else None
    attribution_text = attribution.text if attribution else None
    
    return image_url, attribution_text

# Fetch the first 20 cars from the database
all_cars = session.query(Car.model_id, Car.model_make_id, Car.model_name, Car.model_trim, Car.model_year, Car.model_body, Car.model_engine_cc).limit(20).all()

for car in all_cars:
    make = car.model_make_id
    model = car.model_name
    trim = car.model_trim
    year = car.model_year
    body = car.model_body
    engine_cc = car.model_engine_cc
    
    image_url, attribution_text = fetch_image_details(make, model, trim, year, body, engine_cc)
    
    print(f"Searching for images for {make} {model} ...")
    print(f"Image URL: {image_url}")
    print(f"Attribution Text: {attribution_text}")

    if image_url and attribution_text:
        # Insert a new record into general_car_images
        new_image = GeneralCarImage(
            model_id=car.model_id,
            image_url=image_url,
            web_image_url=None,  # For now, we'll leave this as None
            attribution_text=attribution_text
        )
        session.add(new_image)
        session.commit()
        
    time.sleep(3)
