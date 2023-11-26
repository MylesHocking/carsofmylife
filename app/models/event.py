from app import db  
from datetime import datetime

class Event(db.Model):
    __tablename__ = 'events'

    event_id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))  # Assuming you have a User model
    car_id = db.Column(db.Integer, db.ForeignKey('car_data.model_id'))  # Assuming you have a Car model
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    additional_info = db.Column(db.Text)
    association_id = db.Column(db.Integer, db.ForeignKey('user_car_association.id'))

    association = db.relationship("UserCarAssociation", back_populates="events")
    user = db.relationship("User", back_populates="events")
    car = db.relationship("Car", back_populates="events")
    comments = db.relationship('Comment', back_populates='event')

    def __repr__(self):
        return f'<Event {self.event_type} - User {self.user_id}>'