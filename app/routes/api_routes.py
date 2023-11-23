from flask import Blueprint, jsonify,request, render_template
from app import db  
from app.models import Car, UserCarAssociation, CarImage, User
from app.utils.email_utils import send_simple_message
from app.config import MAILGUN_DOMAIN, MAILGUN_API_KEY, UPLOAD_FOLDER
import db_ops
from google.cloud import storage
import datetime 
import requests
#import json
#import os
#from werkzeug.utils import secure_filename
from werkzeug.security import check_password_hash, generate_password_hash
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
    years_and_trims = db.session.query(Car.model_year, Car.model_trim, Car.model_id, Car.is_generic_model).filter(Car.model_name == model_name).distinct(Car.model_year, Car.model_trim).all()
    return jsonify([{"year": year_and_trim[0], "trim": year_and_trim[1], "model_id": year_and_trim[2], "is_generic_model": year_and_trim[3]} for year_and_trim in years_and_trims])


@api.route('/add_car', methods=['GET'])
def add_car_page():
    return render_template('add_car.html')

suggestion_milestones = {
    7: "Why not contact some of the people you traveled around with in that car? It's good to talk.",
    8: "You can invite people to join; just enter their email here.",
    9: "Have you seen the chat forum for this model? Just click here."
    # Add more milestones as needed
}

def get_suggestions_for_user(user_id):
    user_cars_count = UserCarAssociation.query.filter_by(user_id=user_id).count()
    print(f"User has {user_cars_count} cars")
    for milestone, suggestion in sorted(suggestion_milestones.items()):
        if user_cars_count == milestone:
            return suggestion
    return None

@api.route('/add_car', methods=['POST'])
def add_car():
    # Your code to handle the form submission goes here
    data = request.form
    file = request.files.get('file', None)
    rating = int(data.get('rating'))
    memories = data['memories']
    year_purchased = data.get('year_purchased')
    user_id = data.get('user_id')
    print('user_id is:' + str(user_id))
    
    # Extract custom fields
    custom_make = data.get('custom_make', None)
    custom_model = data.get('custom_model', None)
    custom_variant = data.get('custom_variant', None)

    if 'model_id' in data and data['model_id']:
        model_id = int(data.get('model_id'))
    else:
        model_id = 1 # custom car
    
    # Check if an image was uploaded
    has_custom_image = file and file.filename.split('.')[-1] in ALLOWED_EXTENSIONS

    new_car_id = db_ops.add_car_to_db(
    model_id=model_id,
    rating=rating,
    memories=memories,
    user_id=user_id,
    year_purchased=year_purchased,
    custom_make=custom_make,
    custom_model=custom_model,
    custom_variant=custom_variant,
    has_custom_image=has_custom_image
    )

    # Check if a custom image has been uploaded
    if has_custom_image:
        # Now you can use new_car_id to upload the image to GCP
        folder_path = f"{UPLOAD_FOLDER}/{new_car_id}/"
        thumbnail_folder_path = f"{UPLOAD_FOLDER}/{new_car_id}/thumb/"

        # Upload main image
        blob = storage.Blob(folder_path + file.filename, bucket=storage_client.bucket(GCP_BUCKET_NAME))
        blob.upload_from_file(file)
        # Reset the file pointer to the beginning so that it can be read again
        file.seek(0)
        # Create a thumbnail
        create_thumbnail(file, thumbnail_folder_path + file.filename, GCP_BUCKET_NAME)
    
    # After adding a new car, check if there's a suggestion for the user
    suggestion = get_suggestions_for_user(user_id)

    # Include the suggestion in the response if there is one
    if suggestion:
        return jsonify({"message": "Car added successfully", "suggestion": suggestion})
    else:
        return jsonify({"message": "Car added successfully"})

@api.route('/edit_car/<int:car_id>', methods=['POST'])
def edit_car(car_id):
    data = request.form
    file = request.files.get('file', None)
    memories = data['memories']

    # Check if an image was uploaded
    if file and file.filename.split('.')[-1] in ALLOWED_EXTENSIONS:
        has_custom_image = True
        db_ops.update_car_in_db(
            car_id=car_id,
            memories=memories,
            has_custom_image=has_custom_image
        )
        # Add code to handle the new image upload
        # ...
    else:
        db_ops.update_car_in_db(
            car_id=car_id,
            memories=memories
            # Note: Not passing has_custom_image
        )

    return jsonify({"message": "Car updated successfully"})


@api.route('/delete_car/<int:car_id>', methods=['DELETE'])
def delete_car(car_id):
    print(f"Deleting car with ID: {car_id}")
    success = db_ops.delete_car_from_db(car_id)
    if success:
        return jsonify({"message": "Car deleted successfully"}), 200
    else:
        return jsonify({"error": "Car not found"}), 404


@api.route('/user_cars/<int:user_id>', methods=['GET'])
def get_user_cars(user_id):
    user_cars = db.session.query(UserCarAssociation, Car, CarImage).\
                join(Car, UserCarAssociation.model_id == Car.model_id, isouter=True).\
                outerjoin(CarImage, UserCarAssociation.id == CarImage.association_id).\
                filter(UserCarAssociation.user_id == user_id).\
                order_by(UserCarAssociation.year_purchased).all()

    cars_data = [
        {
            'id': car.UserCarAssociation.id,
            'model_id': car.UserCarAssociation.model_id,
            'make': car.UserCarAssociation.custom_make if car.UserCarAssociation.model_id == 1 else car.Car.model_make_id,
            'model': car.UserCarAssociation.custom_model if car.UserCarAssociation.model_id == 1 else car.Car.model_name,
            'model_trim': car.Car.model_trim if car.Car else None,
            'model_year': car.Car.model_year if car.Car else None,
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
    return get_first_image_type(f'{UPLOAD_FOLDER}/{user_car_association_id}/thumb')

@api.route('/get_first_photo/<model_id>', methods=['GET'])
def get_first_photo(model_id):
    return get_first_image_type('photos', model_id)

@api.route('/get_custom_photo/<user_car_association_id>', methods=['GET'])
def get_custom_photo(user_car_association_id):
    return get_first_image_type(f'{UPLOAD_FOLDER}/{user_car_association_id}')

def get_first_image_type(image_type, model_id=None):
    folder_name = f'{image_type}/{model_id}/' if model_id else f'{image_type}/'
    #print(f"Searching in folder: {folder_name}")  # Print the folder name you are searching in

    bucket = storage_client.get_bucket(GCP_BUCKET_NAME)
    blobs = list(bucket.list_blobs(prefix=folder_name))  # Convert iterator to list
    
    blob_names = [blob.name for blob in blobs]
    #print(f"Blobs found: {blob_names}")  # Print the names of blobs retrieved

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

from concurrent.futures import ThreadPoolExecutor
import random
def generate_url(blob):
    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=15),
        method="GET"
    )
    return url

def get_multiple_thumbs_for_generic_model(make, model):
    #print(f"[DEBUG {datetime.datetime.now()}] Starting get_multiple_thumbs_for_generic_model for {make} {model}")
    
    # Get DB connection
    conn = db_ops.get_db_conn()
    cur = conn.cursor()

    # Step 1: Get all model_ids with the same make and model
    print(f"[DEBUG {datetime.datetime.now()}] Fetching sibling model IDs.")
    query = "SELECT model_id FROM car_data WHERE model_make_id = %s AND model_name = %s"
    cur.execute(query, (make, model))
    sibling_model_ids = [row[0] for row in cur.fetchall()]
    print(f"[DEBUG {datetime.datetime.now()}] Found sibling model IDs: {sibling_model_ids}")

    cur.close()
    conn.close()
    # Randomly pick 6 siblings
    random_sample_ids = random.sample(sibling_model_ids, min(6, len(sibling_model_ids)))

    image_urls = []

    # Get the GCP bucket
    bucket = storage_client.get_bucket(GCP_BUCKET_NAME)

    # Fetch thumbnails in parallel
    with ThreadPoolExecutor() as executor:
        for model_id in random_sample_ids:
            folder_name = f'thumbs/{model_id}/'
            blobs = list(bucket.list_blobs(prefix=folder_name))
                
            # We only need the first thumbnail for each model
            if blobs:
                blob = blobs[0]
                future = executor.submit(generate_url, blob)
                url = future.result()
                image_urls.append(url)
                print(f"[DEBUG {datetime.datetime.now()}] Generated URL: {url}")
                
    # Step 3: Return the list of image URLs
    if not image_urls:
        print(f"[DEBUG {datetime.datetime.now()}] No images found.")
        return jsonify({"error": "No images found"}), 200
    
    print(f"[DEBUG {datetime.datetime.now()}] Finished fetching. Returning URLs.")
    return jsonify({"image_urls": image_urls})


def get_multiple_thumbs_for_generic_model2(make, model):
    print(f"[DEBUG {datetime.datetime.now()}] Starting get_multiple_thumbs_for_generic_model for {make} {model}")
    
    # Get DB connection
    conn = db_ops.get_db_conn()
    cur = conn.cursor()

    # Step 1: Get all model_ids with the same make and model
    print(f"[DEBUG {datetime.datetime.now()}] Fetching sibling model IDs.")
    query = "SELECT model_id FROM car_data WHERE model_make_id = %s AND model_name = %s"
    cur.execute(query, (make, model))
    sibling_model_ids = [row[0] for row in cur.fetchall()]
    print(f"[DEBUG {datetime.datetime.now()}] Found sibling model IDs: {sibling_model_ids}")

    cur.close()
    conn.close()

    image_urls = []

    # Step 2: For each model_id, get the first thumbnail
    print(f"[DEBUG {datetime.datetime.now()}] Fetching thumbnails.")
    for model_id in sibling_model_ids:
        folder_name = f'thumbs/{model_id}/'
        bucket = storage_client.get_bucket(GCP_BUCKET_NAME)
        blobs = list(bucket.list_blobs(prefix=folder_name))

        for blob in blobs[:1]:  # Only need the first thumbnail
            if blob.name != folder_name:  # Skip the folder itself
                url = blob.generate_signed_url(
                    version="v4",
                    expiration=datetime.timedelta(minutes=15),  # URL valid for 15 minutes
                    method="GET"
                )
                image_urls.append(url)
                print(f"[DEBUG {datetime.datetime.now()}] Generated URL: {url}")
                break  # Found one thumbnail for this model_id, move to the next one

    # Step 3: Return the list of image URLs
    if not image_urls:
        print(f"[DEBUG {datetime.datetime.now()}] No images found.")
        return jsonify({"error": "No images found"}), 200
    
    print(f"[DEBUG {datetime.datetime.now()}] Finished fetching. Returning URLs.")
    return jsonify({"image_urls": image_urls})


@api.route('/get_multiple_thumbs', methods=['GET'])
def get_multiple_thumbs_route():
    make = request.args.get('make')
    model = request.args.get('model')

    if not make or not model:
        return jsonify({"error": "Make and model parameters are required"}), 400

    return get_multiple_thumbs_for_generic_model(make, model)

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
                username=token_info.get('email', ''),
                # get first name and last name
                firstname=token_info.get('given_name', ''),
                lastname=token_info.get('family_name', ''),                                
            )
            db.session.add(user)
            db.session.commit()
        # Convert the user model to a dictionary
        user_info = user.to_dict()
    except Exception as e:
        print(f"An error occurred: {e}")

    return jsonify({"status": "success", "message": "Valid token", "token_info": token_info, "user_info": user_info}), 200

@api.route('/signup', methods=['POST'])
def signup():
    email = request.json['email']
    password = request.json['password']
    firstname = request.json['firstname']
    lastname = request.json['lastname']
    #debug
    print('email is:' + email)

    # Check if user already exists
    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({"message": "User already exists"}), 409

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create new user
    new_user = User(email=email, password_hash=hashed_password, username=email, firstname=firstname, lastname=lastname)
    db.session.add(new_user)
    db.session.commit()
    # Convert the user model to a dictionary
    user_info = new_user.to_dict()
    return jsonify({"status": "success", "message": "User added", "user_info": user_info}), 200

@api.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    #debug
    print('email is:' + email)
    print('password is:' + password)
    
    user = User.query.filter_by(email=email).first()
    #debug
    print('user is:' + str(user))
    user_info = user.to_dict()
    if user and check_password_hash(user.password_hash, password):
        # Generate and return token/session info
        return jsonify({"message": "Login successful", "user_info": user_info}), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


@api.route('/share_chart', methods=['POST'])
def share_chart():
    data = request.json
    recipient_emails = data['recipients']  # Assuming this is a list of emails
    subject = "Check out my car-chart on Cars of My Life"
    text = data['message']  # The message to send

    # Call the email utility function for each recipient
    for email in recipient_emails:
        response = send_simple_message(MAILGUN_DOMAIN, MAILGUN_API_KEY, email, subject, text)
        if not response.ok:
            # If any email fails to send, return an error response
            return jsonify({"message": "Failed to send email to one or more recipients."}), 500

    # If all emails are sent successfully
    return jsonify({"message": "Emails sent successfully!"}), 200

@api.route('/users', methods=['GET'])
def get_users():
    try:
        users = User.query.all()  # Fetch all users from the database
        user_list = [{'user_id': user.id, 'firstname': user.firstname, 'lastname': user.lastname} for user in users]
        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

