import os

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'postgresql://postgres:J4sp3rw00@localhost/carsofmylife')

ALLOWED_ORIGINS = "http://localhost:3000"