from flask import jsonify, request
from main import app, db
from app.models import User, Product, Category
import jwt
import datetime
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message' : 'Token is missing!'}), 401
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.filter_by(id=data['id']).first()
        except:
            return jsonify({'message' : 'Token is invalid!'}), 401
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'must include username, email and password fields'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'el nombre de usuario ya esta en uso'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'el correo electronico ya esta en uso'}), 400
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'usuario creado exitosamente'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if 'username' not in data or 'password' not in data:
        return jsonify({'message': 'must include username and password fields'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'nombre de usuario o contraseña incorrectos'}), 401
    token = jwt.encode({'id': user.id, 'exp' : datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['JWT_SECRET_KEY'], algorithm='HS256')
    return jsonify({'token' : token})

@app.route('/protected')
@token_required
def protected(current_user):
    return jsonify({'message' : f'Hello {current_user.username}!'})

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'category': p.category.name} for p in products])

@app.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    data = request.get_json() or {}
    if 'name' not in data or 'price' not in data or 'category_id' not in data:
        return jsonify({'message': 'must include name, price and category_id fields'}), 400
    category = Category.query.get(data['category_id'])
    if not category:
        return jsonify({'message': 'category not found'}), 404
    product = Product(name=data['name'], price=data['price'], category=category)
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'product created successfully'}), 201

@app.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.all()
    return jsonify([{'id': c.id, 'name': c.name} for c in categories])

@app.route('/categories', methods=['POST'])
@token_required
def create_category(current_user):
    data = request.get_json() or {}
    if 'name' not in data:
        return jsonify({'message': 'must include name field'}), 400
    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'category created successfully'}), 201
