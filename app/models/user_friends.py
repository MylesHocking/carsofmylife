from app import db

class UserFriends(db.Model):
    __tablename__ = 'user_friends'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    # Relationship back to User
    user = db.relationship("User", back_populates="friends", foreign_keys=[user_id])
    friend = db.relationship("User", foreign_keys=[friend_id])

    # Additional fields like status, etc., can be added if necessary
