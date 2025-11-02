from flask import jsonify, request, url_for, send_from_directory
from main import app, db
from app.models import User, Product, Category
import jwt
import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename


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
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'category': p.category.name, 'image_url': url_for('uploaded_file', filename=p.image_filename, _external=True) if p.image_filename else None} for p in products])

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    if 'name' not in request.form or 'price' not in request.form or 'category_id' not in request.form:
        return jsonify({'message': 'must include name, price and category_id fields'}), 400
    category = Category.query.get(request.form['category_id'])
    if not category:
        return jsonify({'message': 'category not found'}), 404
    image_filename = None
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            image_filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))
    product = Product(name=request.form['name'], price=request.form['price'], category=category, image_filename=image_filename)
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
