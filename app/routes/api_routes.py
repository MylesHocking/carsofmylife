from flask import Blueprint, jsonify, render_template, request
from app import db  
from app.models import Car, UserCarAssociation, CarImage, User
import db_ops
from google.cloud import storage
import datetime 
import requests
import json
import os
from werkzeug.utils import secure_filename
from app.utils.image_utils import create_thumbnail
from app.utils.gcp_utils import storage_client

api = Blueprint('api', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
GCP_BUCKET_NAME = 'cars-of-my-life-images'

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
    data = request.form
    file = request.files.get('file', None)
    model_id = int(data.get('model_id'))  # Convert to integer
    rating = int(data.get('rating'))
    memories = data['memories']
    year_purchased = data.get('year_purchased')
    user_id = data.get('user_id')
    print('user_id is:' + str(user_id))

    # Check if an image was uploaded
    has_custom_image = file and file.filename.split('.')[-1] in ALLOWED_EXTENSIONS

    new_car_id = db_ops.add_car_to_db(model_id, rating, memories, user_id, year_purchased, has_custom_image)
    # Check if a custom image has been uploaded
    if has_custom_image:
        # Now you can use new_car_id to upload the image to GCP
        folder_path = f"user_images/{new_car_id}/"
        thumbnail_folder_path = f"user_images/{new_car_id}/thumb/"

        # Upload main image
        blob = storage.Blob(folder_path + file.filename, bucket=storage_client.bucket(GCP_BUCKET_NAME))
        blob.upload_from_file(file)
        # Reset the file pointer to the beginning so that it can be read again
        file.seek(0)
        # Create a thumbnail
        create_thumbnail(file, thumbnail_folder_path + file.filename, GCP_BUCKET_NAME)
    
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
            'image_url': car.CarImage.image_url if car.CarImage else None,
            'has_custom_image': car.UserCarAssociation.has_custom_image,  
            'user_car_association_id': car.UserCarAssociation.id 
        } for car in user_cars
    ]
    return jsonify(cars_data)



@api.route('/get_first_thumb/<model_id>', methods=['GET'])
def get_first_thumb(model_id):
    return get_first_image_type('thumbs', model_id)

@api.route('/get_custom_thumb/<user_car_association_id>', methods=['GET'])
def get_custom_thumb(user_car_association_id):
    return get_first_image_type(f'user_images/{user_car_association_id}/thumb')

@api.route('/get_first_photo/<model_id>', methods=['GET'])
def get_first_photo(model_id):
    return get_first_image_type('photos', model_id)

@api.route('/get_custom_photo/<user_car_association_id>', methods=['GET'])
def get_custom_photo(user_car_association_id):
    return get_first_image_type(f'user_images/{user_car_association_id}')

def get_first_image_type(image_type, model_id=None):
    folder_name = f'{image_type}/{model_id}/' if model_id else f'{image_type}/'
    print(f"Searching in folder: {folder_name}")  # Print the folder name you are searching in

    bucket = storage_client.get_bucket(GCP_BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=folder_name))  # Convert iterator to list
    
    blob_names = [blob.name for blob in blobs]
    print(f"Blobs found: {blob_names}")  # Print the names of blobs retrieved

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