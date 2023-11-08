from app import db

class UserCarAssociation(db.Model):
    __tablename__ = 'user_car_association'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    model_id = db.Column(db.BigInteger, db.ForeignKey('car_data.model_id'))
    rating = db.Column(db.Integer)
    memories = db.Column(db.Text)
    year_purchased = db.Column(db.Integer)
    has_custom_image = db.Column(db.Boolean, default=False)
    is_custom = db.Column(db.Boolean, default=False)  # Flag to indicate custom car data
    custom_make = db.Column(db.String(100), nullable=True)
    custom_model = db.Column(db.String(100), nullable=True)
    custom_variant = db.Column(db.String(100), nullable=True)

    user = db.relationship("User", back_populates="cars")
    car = db.relationship("Car", back_populates="users")
    images = db.relationship("CarImage", back_populates="association")
    
