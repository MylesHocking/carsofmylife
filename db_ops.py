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

