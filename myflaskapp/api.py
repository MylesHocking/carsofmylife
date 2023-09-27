from flask import Blueprint, jsonify
import db_ops
import random

api = Blueprint('api', __name__)

@api.route('/random_cars', methods=['GET'])
def get_random_cars():
    rows = db_ops.get_random_cars_from_db()
    cars = [{"id": row[0], "make": row[1], "model": row[2], "rating": random.randint(1, 10)} for row in rows] 
    return jsonify(cars)
