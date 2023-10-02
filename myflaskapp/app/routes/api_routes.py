from flask import Blueprint, jsonify
from app import db  
from app.models import Car, UserCarAssociation, CarImage
import random
import db_ops
from flask import Blueprint, render_template, request, jsonify


api = Blueprint('api', __name__)
'''
#test route fetches 10 randoms cars from db
@api.route('/random_cars', methods=['GET'])
def get_random_cars():
    rows = db_ops.get_random_cars_from_db()
    cars = [{"id": row[0], "make": row[1], "model": row[2], "rating": random.randint(1, 10)} for row in rows] 
    return jsonify(cars)
'''
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
    user_id = 1  # For now, let's assume the user ID is 1
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
            'rating': car.UserCarAssociation.rating,
            'memories': car.UserCarAssociation.memories,
            'year_purchased': car.UserCarAssociation.year_purchased,
            'image_url': car.CarImage.image_url if car.CarImage else None
        } for car in user_cars
    ]
    return jsonify(cars_data)

