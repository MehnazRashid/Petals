from app import app, db
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(300), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.String(50), nullable=False)
    category = db.Column(db.Text, nullable=True) 
    details = db.Column(db.Text, nullable=True)
    image_url = db.Column(db.String(200), nullable=True)
    stock = db.Column(db.Integer, nullable=False, default=10)
    ratings = db.relationship('Rating', backref='flower', lazy=True)

    def __init__(self, name, price, category, details, image_url):
        self.name = name
        self.price = price
        self.category = category
        self.details = details
        self.image_url = image_url

    @property
    def average_rating(self):
        if not self.ratings:
            return 0.0
        return round(sum(r.rating for r in self.ratings) / len(self.ratings), 1)

    @property
    def review_count(self):
        return len(self.ratings)

class Contact(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=True)

    def __init__(self, email, message):
        self.email = email 
        self.message = message

class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    blogtext = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(200), nullable=True)

    def __init__(self, title, blogtext, image_url):
        self.title = title
        self.blogtext = blogtext
        self.image_url = image_url

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flower_id = db.Column(db.Integer, db.ForeignKey('flower.id'), nullable=False)
    user = db.relationship('User', backref='wishlist_items')
    flower = db.relationship('Flower')

class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flower_id = db.Column(db.Integer, db.ForeignKey('flower.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    user = db.relationship('User', backref='cart_items')
    flower = db.relationship('Flower')

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='Processing')
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='orders')
    items = db.relationship('OrderItem', backref='order', cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    flower_id = db.Column(db.Integer, db.ForeignKey('flower.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.String(50), nullable=False)
    flower = db.relationship('Flower')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    flower_id = db.Column(db.Integer, db.ForeignKey('flower.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text, nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    user = db.relationship('User', backref='ratings', lazy=True)

with app.app_context():
    db.create_all()