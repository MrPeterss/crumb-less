from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Define Business model
class Business(db.Model):
    __tablename__ = 'businesses'
    id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(256), nullable=False)
    address = db.Column(db.String(512))
    city = db.Column(db.String(128))
    state = db.Column(db.String(64))
    postal_code = db.Column(db.String(16))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    stars = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    categories = db.Column(db.Text)
    hours = db.Column(db.Text)
    
    # Relationship to reviews
    reviews = db.relationship('Review', backref='business', lazy=True)
    
    def __repr__(self):
        return f'<Business {self.id}: {self.name}>'

# Define Review model
class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.String(64), primary_key=True)
    user_id = db.Column(db.String(64))
    business_id = db.Column(db.String(64), db.ForeignKey('businesses.id'), nullable=False)
    stars = db.Column(db.Float)
    date = db.Column(db.String(64))
    text = db.Column(db.Text)
    
    def __repr__(self):
        return f'<Review {self.id} for Business {self.business_id}>'
