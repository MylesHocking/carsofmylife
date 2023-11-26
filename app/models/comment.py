from app import db  
from datetime import datetime

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('events.event_id'), nullable=True)
    user_car_association_id = db.Column(db.Integer, db.ForeignKey('user_car_association.id'), nullable=True)
    parent_comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)
    
    # Relationships
    user = db.relationship('User', back_populates='comments')
    event = db.relationship('Event', back_populates='comments', post_update=True)
    user_car_association = db.relationship('UserCarAssociation', back_populates='comments', post_update=True)
    parent_comment = db.relationship('Comment', remote_side=[id], back_populates='child_comments', post_update=True)
    child_comments = db.relationship('Comment', back_populates='parent_comment', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id}>'
