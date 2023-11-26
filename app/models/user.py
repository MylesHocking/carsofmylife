from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    google_id = db.Column(db.String(50), unique=True, nullable=True) 
    is_google_account = db.Column(db.Boolean, default=False) 
    username = db.Column(db.String(50), nullable=True, default='default_username')
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), unique=False, nullable=False)    
    email = db.Column(db.String(100), unique=False, nullable=False)
    password_hash = db.Column(db.String(128), nullable=True)
    happy2show = db.Column(db.Boolean, nullable=False, default=True)
    cars = db.relationship("UserCarAssociation", back_populates="user")
    events = db.relationship("Event", back_populates="user")
    comments = db.relationship("Comment", back_populates="user")
    
    def to_dict(self):
        return {
            'id': self.id,
            'google_id': self.google_id,
            'is_google_account': self.is_google_account,
            'username': self.username,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'email': self.email
        }