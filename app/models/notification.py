from app import db
from datetime import datetime

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    read = db.Column(db.Boolean, default=False)
    message = db.Column(db.Text, nullable=False)

    # Relationships
    user = db.relationship('User', back_populates='notifications')

    def __repr__(self):
        return f'<Notification {self.id} for User {self.user_id}>'