import psycopg2
from flask_sqlalchemy import SQLAlchemy
from app import db
from app.models import Car, UserCarAssociation
from config import SQLALCHEMY_DATABASE_URI

def get_db_conn():
    return psycopg2.connect(SQLALCHEMY_DATABASE_URI)

def get_random_cars_from_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM car_data ORDER BY RANDOM() LIMIT 10;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def add_car_to_db(model_id, rating, memories, user_id, year_purchased):
    new_association = UserCarAssociation(
        user_id=user_id,
        model_id=model_id,
        rating=rating,
        memories=memories,
        year_purchased=year_purchased
    )

    db.session.add(new_association)
    db.session.commit()
