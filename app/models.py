from werkzeug.security import generate_password_hash, check_password_hash
from main import db
import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    orders = db.relationship('Order', backref='user', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    price = db.Column(db.Float)
    description = db.Column(db.String(500))
    offer_price = db.Column(db.Float, nullable=True)
    image_filename = db.Column(db.String(256), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))

    def __repr__(self):
        return '<Product {}>'.format(self.name)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(140))
    products = db.relationship('Product', backref='category', lazy='dynamic')

    def __repr__(self):
        return '<Category {}>'.format(self.name)

class Banner(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    link = db.Column(db.String(500))
    image_filename = db.Column(db.String(256), nullable=True)

    def __repr__(self):
        return '<Banner {}>'.format(self.title)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_price = db.Column(db.Float)
    status = db.Column(db.String(64), default='pending')
    timestamp = db.Column(db.DateTime, index=True, default=datetime.datetime.utcnow)
    items = db.relationship('OrderItem', backref='order', lazy='dynamic')

    def __repr__(self):
        return '<Order {}>'.format(self.id)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    def __repr__(self):
        return '<OrderItem {}>'.format(self.id)
