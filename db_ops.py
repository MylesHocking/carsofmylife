import psycopg2
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models import Car, UserCarAssociation
from app.config import SQLALCHEMY_DATABASE_URI

def get_db_conn():
    return psycopg2.connect(SQLALCHEMY_DATABASE_URI)

def add_car_to_db(model_id, rating, memories, user_id, year_purchased, custom_make=None, custom_model=None, custom_variant=None, has_custom_image=False):
    # Determine if the car is custom based on the presence of custom fields
    is_custom = bool(custom_make or custom_model or custom_variant)

    # Create a new UserCarAssociation instance with the provided data
    new_association = UserCarAssociation(
        user_id=user_id,
        model_id=model_id,  # This could be None for custom cars
        rating=rating,
        memories=memories,
        year_purchased=year_purchased,
        custom_make=custom_make,
        custom_model=custom_model,
        custom_variant=custom_variant,
        is_custom=is_custom,  # This will be True for custom cars
        has_custom_image=has_custom_image
    )

    # Save the new association to the database
    db.session.add(new_association)
    db.session.commit()

    # Return the ID of the newly created association
    return new_association.id

def update_car_in_db(car_id, memories, has_custom_image=None):
    # Find the existing car entry by ID
    car_to_edit = UserCarAssociation.query.get(car_id)

    # Check if the car exists
    if not car_to_edit:
        raise ValueError("Car not found")

    # Update the fields
    car_to_edit.memories = memories
    if has_custom_image is not None:
        car_to_edit.has_custom_image = has_custom_image

    # Commit the changes to the database
    db.session.commit()

    # You might want to return something, like a success message or the updated car data
    return {"message": "Car updated successfully", "car_id": car_id}

def delete_car_from_db(car_id):
    car_to_delete = UserCarAssociation.query.get(car_id)
    if car_to_delete:
        db.session.delete(car_to_delete)
        db.session.commit()
        return True
    else:
        return False