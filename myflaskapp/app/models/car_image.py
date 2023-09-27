from app import db

class CarImage(db.Model):
    __tablename__ = 'car_images'

    id = db.Column(db.Integer, primary_key=True)
    association_id = db.Column(db.Integer, db.ForeignKey('user_car_association.id'), nullable=False)
    image_url = db.Column(db.Text, nullable=True)

    # Add a backref to establish a bi-directional relationship if needed
    association = db.relationship("UserCarAssociation", back_populates="images")
