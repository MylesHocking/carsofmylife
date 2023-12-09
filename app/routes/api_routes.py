from flask import Blueprint, jsonify, request, render_template, redirect
from app import db  
from app.models import Car, UserCarAssociation, CarImage, User, Event, Comment, UserFriends, Notification
from app.models.user import SharingPreferenceEnum
from app.utils.email_utils import send_simple_message, send_html_message
from app.utils.notification_utils import send_notification_email
from app.config import MAILGUN_DOMAIN, MAILGUN_API_KEY, UPLOAD_FOLDER, LINKEDIN_CLIENT_ID, LINKEDIN_CLIENT_SECRET, LINKEDIN_REDIRECT_URI, ALLOWED_ORIGINS
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
    # Check if this is the first car for the user
    user_cars_count = UserCarAssociation.query.filter_by(user_id=user_id).count()
    if user_cars_count == 1:  # This means the car just added is the first car
        # Create an event for the first car addition
        first_car_event = Event(
            event_type='first_car_added',
            user_id=user_id,
            timestamp=datetime.datetime.utcnow(),
            # Add additional info if needed
        )
        db.session.add(first_car_event)
        db.session.commit()

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

    # Create an event for new user signup
    new_event = Event(
        event_type='new_user',
        user_id=new_user.id,
        timestamp=datetime.datetime.utcnow(),  # Assuming you have from datetime import datetime
        # You can add more fields if needed
    )
    db.session.add(new_event)
    db.session.commit()
    #debug
    print('new_user is:' + str(new_user))
    print('new_event is:' + str(new_event))

    # Convert the user model to a dictionary
    user_info = new_user.to_dict()
    return jsonify({"status": "success", "message": "User added", "user_info": user_info}), 200

@api.route('/linkedin/callback')
def linkedin_callback():
    print('linkedin_callback triggered')
    code = request.args.get('code')
    print('code is:' + code)
    token_info = exchange_code_for_token(code)
    print('token_info is:' + str(token_info))
    access_token = token_info.get('access_token')
    print('access_token is:' + access_token)
    user_info = get_user_info(access_token)
    print('user_info is:' + str(user_info))
    # Handle user_info (e.g., create a user session, store details in the database)
    if user_info:
        new_user_data = linkedin_signup(user_info)
        return redirect(f'{ALLOWED_ORIGINS}/linkedin-callback?user_id={new_user_data["id"]}&email={new_user_data["email"]}&firstname={new_user_data["firstname"]}&lastname={new_user_data["lastname"]}&profile_picture={new_user_data["profile_picture"]}')
    else:
        return jsonify({"message": "Failed to retrieve user info"}), 500

def get_user_info(access_token):
    url = 'https://api.linkedin.com/v2/userinfo'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'cache-control': "no-cache"
    }
    response = requests.get(url, headers=headers)
    return response.json()  # This contains the user's LinkedIn profile information
def exchange_code_for_token(code):
    url = 'https://www.linkedin.com/oauth/v2/accessToken'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': LINKEDIN_REDIRECT_URI,
        'client_id': LINKEDIN_CLIENT_ID,
        'client_secret': LINKEDIN_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()  # This contains the access token

def linkedin_signup(user_data):
    print('linkedin_signup triggered with user_data:' + str(user_data))
    email = user_data['email']
    firstname = user_data['given_name']
    lastname = user_data['family_name']
    picture = user_data['picture']
    # Check if user already exists
    linkedin_sub = user_data['sub']  # Assuming 'sub' is in user_data
    existing_user = User.query.filter_by(linkedin_sub=linkedin_sub).first()
    if existing_user:
        return existing_user.to_dict()

    # Create new user with LinkedIn data
    new_user = User(email=email, username=email, firstname=firstname, lastname=lastname, linkedin_sub=linkedin_sub, profile_picture=picture)
    db.session.add(new_user)
    db.session.commit()

    # Create an event for new user signup
    new_event = Event(event_type='new_user', user_id=new_user.id, timestamp=datetime.datetime.utcnow())
    db.session.add(new_event)
    db.session.commit()

    # Convert the user model to a dictionary
    user_info = new_user.to_dict()
    return user_info

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

from flask import g  # Import global context object, typically used for request-specific data like current user

@api.route('/users', methods=['GET'])
def get_users():
    try:
        current_user_id = request.args.get('userId')
        users = User.query.filter(User.sharing_preference == SharingPreferenceEnum.Global).all()

        user_list = []
        for user in users:
            # Check if the current user is friends with this user
            is_friend = UserFriends.query.filter(
                ((UserFriends.user_id == current_user_id) & (UserFriends.friend_id == user.id)) |
                ((UserFriends.friend_id == current_user_id) & (UserFriends.user_id == user.id))
            ).first() is not None

            # Exclude the current user from the list
            if user.id != current_user_id:
                user_list.append({
                    'user_id': user.id,
                    'firstname': user.firstname,
                    'lastname': user.lastname,
                    'is_friend': is_friend
                })

        return jsonify(user_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@api.route('/events', methods=['GET'])
def get_events():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    events_pagination = Event.query.order_by(Event.timestamp.desc()).paginate(page=page, per_page=per_page, error_out=False)
    events = events_pagination.items

    events_data = []
    for event in events:
        # Fetch user details
        user = User.query.get(event.user_id)
        if not user:
            continue  # or handle the missing user scenario
        event_info = {
            'event_id': event.event_id,
            'event_type': event.event_type,
            'timestamp': event.timestamp.isoformat(),
            'user_id': event.user_id,
            'firstname': user.firstname, 
            'lastname': user.lastname, 
            'profile_picture': user.profile_picture
            # You can add more general fields here
        }

        # Add specific data for 'first_car_added' event type
        if event.event_type == 'first_car_added':
            car_association = UserCarAssociation.query.filter_by(user_id=event.user_id).first()
            if car_association:
                # Basic car information
                event_info.update({
                    'rating': car_association.rating,
                    'memories': car_association.memories,
                    'year_purchased': car_association.year_purchased,
                    'user_car_association_id': car_association.id,
                    'model_id': car_association.model_id,
                    'has_custom_image': car_association.has_custom_image,
                    'is_custom': car_association.is_custom
                })

                # Custom or standard car details
                if car_association.is_custom:
                    event_info.update({
                        'car_make': car_association.custom_make,
                        'car_model': car_association.custom_model,
                        'car_variant': car_association.custom_variant
                    })
                else:
                    car = Car.query.get(car_association.model_id)
                    if car:
                        event_info.update({
                            'model_make_id': car.model_make_id,  # Assuming this is how you get the make
                            'model_name': car.model_name,    # Assuming this is how you get the model
                            'model_trim': car.model_trim,  # Assuming this is how you get the variant
                        })
                            

        events_data.append(event_info)

    return jsonify({
        'events': events_data,
        'total_pages': events_pagination.pages,
        'current_page': events_pagination.page
    })

@api.route('/add_comment', methods=['POST'])
def add_comment():
    user_id = request.json.get('user_id')
    event_id = request.json.get('event_id', None)
    uca_id = request.json.get('user_car_association_id', None)  # UserCarAssociation ID
    text = request.json.get('text')
    parent_comment_id = request.json.get('parent_comment_id', None)

    if not text:
        return jsonify({'message': 'Comment text is required'}), 400
    
    event = None
    car_info = None
    if event_id:
        event = Event.query.get(event_id)

    if uca_id:
        uca = UserCarAssociation.query.get(uca_id)
        if not uca:
            return jsonify({'message': 'Invalid user car association ID'}), 400

        car = Car.query.get(uca.model_id)  # Fetch the car based on the association
        if car:
            car_info = f"{car.model_make_id} {car.model_name}"  # TODO: Sort for custom cars 
        user_id_of_car = uca.user_id
        
    comment = Comment(
        user_id=user_id, 
        event_id=event_id,
        user_car_association_id=uca_id,
        text=text,
        parent_comment_id=parent_comment_id
    )

    db.session.add(comment)
    
    #get the user who created the comment
    commenting_user = User.query.get(user_id)
    print(f"Commenting user: {commenting_user}")
    link_to_commenters_chart = f"{ALLOWED_ORIGINS}/chart/{user_id}"
    link_to_chart = f"{ALLOWED_ORIGINS}/chart/"
    notification_message = ""
    if event:      
        notification_user_id = event.user_id 
        link_to_chart = link_to_chart + str(notification_user_id)
        notification_message = f"New comment on your <a href='{link_to_chart}'>{event.event_type}</a> by <a href='{link_to_commenters_chart}'>{commenting_user.firstname} {commenting_user.lastname}</a>"
    elif uca_id and car_info:
        notification_user_id = user_id_of_car
        link_to_chart = link_to_chart + str(notification_user_id)
        notification_message = f"New comment on your <a href='{link_to_chart}'>{car_info}</a> by <a href='{link_to_commenters_chart}'>{commenting_user.firstname} {commenting_user.lastname}</a>"        
    else:
        return jsonify({'message': 'Either event_id or user_car_association_id must be provided'}), 400


    # Create a new notification for the user of the event or car
    notification = Notification(
        user_id=notification_user_id,
        message=notification_message
    )
    print(f"Notification: {notification}")
    db.session.add(notification)
    db.session.commit()

    #get email of user who created the event
    user = User.query.get(notification_user_id)
    #send notification email
    send_notification_email(user.email, "New comment on CarsOfMy.Life ", notification_message, notification_user_id)

    return jsonify({'message': 'Comment added successfully', 'comment_id': comment.id}), 201

@api.route('/get_comments', methods=['GET'])
def get_comments():
    event_id = request.args.get('event_id', None)
    uca_id = request.args.get('user_car_association_id', None)

    query = Comment.query
    if event_id:
        query = query.filter_by(event_id=event_id)
    if uca_id:
        query = query.filter_by(user_car_association_id=uca_id)

    comments = query.order_by(Comment.timestamp.asc()).all()

    comments = query.join(User).add_columns(
        Comment.id, Comment.text, Comment.timestamp, 
        User.id.label("user_id"), 
        User.firstname, User.lastname
    ).all()

    comments_data = [{
        'id': c.id, 'text': c.text, 
        'timestamp': c.timestamp.isoformat() if c.timestamp else None, 
        'user_id': c.user_id,
        'firstname': c.firstname, 'lastname': c.lastname
    } for c in comments]

    return jsonify(comments_data)


@api.route('/get_user_profile/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    
    user_data = {
        "firstname": user.firstname,
        "lastname": user.lastname,
        "sharingPreference": user.sharing_preference.name  # Assuming Enum value
    }
    return jsonify(user_data)

@api.route('/update_user_profile/<int:user_id>', methods=['PUT'])
def update_user_profile(user_id):
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    print(f"User profile before update: {user.to_dict()}")
    data = request.json
    try:
        print(f"Data received: {data}")
        if 'firstname' in data:
            user.firstname = data['firstname']
            print(f"User firstname updated: {user.firstname}")
        if 'lastname' in data:
            user.lastname = data['lastname']
            print(f"User lastname updated: {user.lastname}")
        if 'sharingPreference' in data:
            # Convert the string to an enum value
            preference = SharingPreferenceEnum[data['sharingPreference']]
            user.sharing_preference = preference
            print(f"User sharing preference updated: {user.sharing_preference}")
        if 'emailNotifications' in data:
            user.email_notifications = data['emailNotifications'].lower() == 'true'
            print(f"User email notifications updated: {user.email_notifications}")
        print(f"User profile updated: {user.to_dict()}")
        db.session.commit()
        return jsonify({"message": "User profile updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500