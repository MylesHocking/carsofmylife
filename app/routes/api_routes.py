from flask import Blueprint, jsonify
from app.app import db  
from app.models import Car, UserCarAssociation, CarImage, User
import db_ops
from flask import Blueprint, render_template, request, jsonify
from google.cloud import storage
import datetime 
import requests
import json
import os

api = Blueprint('api', __name__)

# Fetch all unique car makes
@api.route('/car_makes')
def get_car_makes():
    makes = db.session.query(Car.model_make_id).distinct().all()
    #sort alphabetically case agnostic
    makes.sort(key=lambda x: x[0].lower())
    
    return jsonify([make[0] for make in makes])

# Fetch car models based on make
@api.route('/car_models/<make>')
def get_car_models(make):
    models = db.session.query(Car.model_id, Car.model_name).filter(Car.model_make_id == make).distinct(Car.model_name).all()
    return jsonify([{"id": model[0], "name": model[1]} for model in models])

# Fetch compound of year and car trims based on model name
@api.route('/car_years_and_trims/<model_name>')
def get_car_years_and_trims(model_name):
    years_and_trims = db.session.query(Car.model_year, Car.model_trim, Car.model_id).filter(Car.model_name == model_name).distinct(Car.model_year, Car.model_trim).all()
    return jsonify([{"year": year_and_trim[0], "trim": year_and_trim[1], "model_id": year_and_trim[2]} for year_and_trim in years_and_trims])


@api.route('/add_car', methods=['GET'])
def add_car_page():
    return render_template('add_car.html')

@api.route('/add_car', methods=['POST'])
def add_car():
    # Your code to handle the form submission goes here
    data = request.json
    model_id = int(data.get('model_id'))  # Convert to integer
    rating = int(data.get('rating'))
    memories = data['memories']
    year_purchased = data.get('year_purchased')
    user_id = data.get('user_id')
    print('user_id is:' + str(user_id))
    db_ops.add_car_to_db(model_id, rating, memories, user_id, year_purchased)

    return jsonify({"message": "Car added successfully"})

@api.route('/user_cars/<int:user_id>', methods=['GET'])
def get_user_cars(user_id):
    user_cars = db.session.query(UserCarAssociation, Car, CarImage).\
                join(Car, UserCarAssociation.model_id == Car.model_id).\
                outerjoin(CarImage, UserCarAssociation.id == CarImage.association_id).\
                filter(UserCarAssociation.user_id == user_id).\
                order_by(UserCarAssociation.year_purchased).all()

    cars_data = [
        {
            'model_id': car.UserCarAssociation.model_id,
            'make': car.Car.model_make_id,
            'model': car.Car.model_name,
            'model_trim': car.Car.model_trim,  
            'model_year': car.Car.model_year,  
            'rating': car.UserCarAssociation.rating,
            'memories': car.UserCarAssociation.memories,
            'year_purchased': car.UserCarAssociation.year_purchased,
            'image_url': car.CarImage.image_url if car.CarImage else None
        } for car in user_cars
    ]
    return jsonify(cars_data)


GCP_CREDENTIALS_JSON_STRING = os.environ.get("GCP_CREDENTIALS_JSON_STRING")
if GCP_CREDENTIALS_JSON_STRING:
    creds_json = json.loads(GCP_CREDENTIALS_JSON_STRING)
    storage_client = storage.Client.from_service_account_info(creds_json)
else:
    storage_client = storage.Client()
@api.route('/get_first_image/<model_id>', methods=['GET'])
def get_first_image(model_id):
    bucket_name = 'cars-of-my-life-images'
    folder_name = f'photos/{model_id}/'

    bucket = storage_client.get_bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=folder_name)

    for blob in blobs:
        if blob.name != folder_name:  # Skip the folder itself
            # Generate a signed URL for the blob
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.timedelta(minutes=15),  # URL valid for 15 minutes
                method="GET"
            )
            return jsonify({"image_url": url})

    return jsonify({"error": "No images found"}), 200

@api.route('/verify_google_token', methods=['POST'])
def verify_google_token():
    received_data = request.json
    token = received_data.get('token', '')

    GOOGLE_TOKEN_INFO_URL = f"https://oauth2.googleapis.com/tokeninfo?id_token={token}"

    response = requests.get(GOOGLE_TOKEN_INFO_URL)
    token_info = response.json()

    if "error_description" in token_info:
        return jsonify({"status": "failure", "message": "Invalid token"}), 401
    
    google_id = token_info.get('sub', '')
    #debug print
    print('google_id is:' + google_id)
    if not google_id:
        return jsonify({"status": "failure", "message": "Google ID not found"}), 401

    # Check if user exists in DB
    try:
        user = User.query.filter_by(google_id=google_id).first()      
        #debug print
        print('user is:' + str(user))
        if user is None:
            # Create new user
            user = User(
                google_id=google_id, 
                is_google_account=True,
                email=token_info.get('email', ''),
                # ... populate more fields if needed
            )
            db.session.add(user)
            db.session.commit()
        # Convert the user model to a dictionary
        user_info = user.to_dict()
    except Exception as e:
        print(f"An error occurred: {e}")


    return jsonify({"status": "success", "message": "Valid token", "token_info": token_info, "user_info": user_info}), 200