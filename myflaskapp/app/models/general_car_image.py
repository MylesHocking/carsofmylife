from app import db

class GeneralCarImage(db.Model):
    __tablename__ = 'general_car_images'

    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.BigInteger, db.ForeignKey('car_data.model_id'), nullable=False)
    web_image_url = db.Column(db.Text, nullable=True)
    attribution_text = db.Column(db.Text, nullable=True)

    # Add a backref to establish a bi-directional relationship if needed
    car_data = db.relationship("Car", back_populates="general_images")
