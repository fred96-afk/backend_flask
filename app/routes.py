from flask import jsonify, request, url_for
from main import app, db
from app.models import User, Product, Category, Banner, Order, OrderItem
import jwt
import datetime
from functools import wraps
import os
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader



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

@app.route('/products', methods=['POST'])
@token_required
def create_product(current_user):
    if 'name' not in request.form or 'price' not in request.form or 'category_id' not in request.form:
        return jsonify({'message': 'must include name, price and category_id fields'}), 400
    category = Category.query.get(request.form['category_id'])
    image_filename = None
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            upload_result = cloudinary.uploader.upload(image)
            image_filename = upload_result['secure_url']
    product = Product(
        name=request.form['name'], 
        price=request.form['price'], 
        category=category, 
        image_filename=image_filename,
        description=request.form.get('description'),
        offer_price=request.form.get('offer_price')
    )
    db.session.add(product)
    db.session.commit()
    return jsonify({'message': 'product created successfully'}), 201

@app.route('/products', methods=['GET'])
def get_products():
    products = Product.query.all()
    return jsonify([{'id': p.id, 'name': p.name, 'price': p.price, 'description': p.description, 'offer_price': p.offer_price, 'category': p.category.name if p.category else None, 'image_url': p.image_filename if p.image_filename else None} for p in products])

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

@app.route('/banners', methods=['POST'])
@token_required
def create_banner(current_user):
    if 'title' not in request.form or 'link' not in request.form:
        return jsonify({'message': 'must include title and link fields'}), 400
    image_filename = None
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            upload_result = cloudinary.uploader.upload(image)
            image_filename = upload_result['secure_url']
    banner = Banner(
        title=request.form['title'], 
        link=request.form['link'], 
        image_filename=image_filename
    )
    db.session.add(banner)
    db.session.commit()
    return jsonify({'message': 'banner created successfully'}), 201

@app.route('/banners', methods=['GET'])
def get_banners():
    banners = Banner.query.all()
    return jsonify([{'id': b.id, 'title': b.title, 'link': b.link, 'image_url': b.image_filename if b.image_filename else None} for b in banners])

@app.route('/orders', methods=['POST'])
@token_required
def create_order(current_user):
    data = request.get_json() or {}
    if 'items' not in data:
        return jsonify({'message': 'must include items field'}), 400
    
    total_price = 0
    order_items = []
    for item_data in data['items']:
        product = Product.query.get(item_data['product_id'])
        if not product:
            return jsonify({'message': f'Product with id {item_data["product_id"]} not found'}), 404
        
        price = product.offer_price if product.offer_price else product.price
        total_price += price * item_data['quantity']
        order_items.append(OrderItem(product_id=product.id, quantity=item_data['quantity'], price=price))

    order = Order(user_id=current_user.id, total_price=total_price)
    db.session.add(order)
    db.session.flush() # flush to get the order id

    for item in order_items:
        item.order_id = order.id
        db.session.add(item)

    db.session.commit()
    return jsonify({'message': 'order created successfully'}), 201


@app.route('/orders', methods=['GET'])
@token_required
def get_orders(current_user):
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': o.id,
        'total_price': o.total_price,
        'status': o.status,
        'timestamp': o.timestamp,
        'items': [{
            'id': i.id,
            'product_id': i.product_id,
            'quantity': i.quantity,
            'price': i.price
        } for i in o.items]
    } for o in orders])
