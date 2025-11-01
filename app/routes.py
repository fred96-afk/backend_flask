from flask import jsonify, request
from main import app, db
from app.models import User, Product, Category

@app.route('/auth/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    if 'username' not in data or 'email' not in data or 'password' not in data:
        return jsonify({'message': 'must include username, email and password fields'}), 400
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'message': 'username already taken'}), 400
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'email already taken'}), 400
    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'user created successfully'}), 201

@app.route('/auth/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    if 'username' not in data or 'password' not in data:
        return jsonify({'message': 'must include username and password fields'}), 400
    user = User.query.filter_by(username=data['username']).first()
    if user is None or not user.check_password(data['password']):
        return jsonify({'message': 'invalid username or password'}), 401
    # In a real app, you would return a JWT token here
    return jsonify({'message': 'login successful'})

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'category': p.category.name} for p in products])

@app.route('/products', methods=['POST'])
def create_product():
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
def create_category():
    data = request.get_json() or {}
    if 'name' not in data:
        return jsonify({'message': 'must include name field'}), 400
    category = Category(name=data['name'])
    db.session.add(category)
    db.session.commit()
    return jsonify({'message': 'category created successfully'}), 201
