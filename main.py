from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
import cloudinary

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Configure Cloudinary
cloudinary.config(
    cloud_name=app.config['CLOUDINARY_CLOUD_NAME'],
    api_key=app.config['CLOUDINARY_API_KEY'],
    api_secret=app.config['CLOUDINARY_API_SECRET']
)

CORS(app, resources={r"/*": {"origins": ["https://frontend-angular-fxx8.vercel.app", "http://localhost:4200"]}})
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models, routes