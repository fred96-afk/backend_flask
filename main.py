from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app, resources={r"/*": {"origins": ["https://frontend-angular-fxx8.vercel.app", "http://localhost:4200"]}})
db = SQLAlchemy(app)
migrate = Migrate(app, db)

from app import models, routes