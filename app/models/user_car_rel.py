from app import db

class UserCarAssociation(db.Model):
    __tablename__ = 'user_car_association'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    model_id = db.Column(db.BigInteger, db.ForeignKey('car_data.model_id'))
    rating = db.Column(db.Integer)
    memories = db.Column(db.Text)
    year_purchased = db.Column(db.Integer)

    user = db.relationship("User", back_populates="cars")
    car = db.relationship("Car", back_populates="users")
    images = db.relationship("CarImage", back_populates="association")
    
