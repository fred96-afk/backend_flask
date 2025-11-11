import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    # mssql+pyodbc://user:password@host\instance_name/database?driver=...
    SQLALCHEMY_DATABASE_URI = 'mssql+pyodbc://Freddy_SQLLogin_1:52vgexnsdj@test_api.mssql.somee.com/test_api?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=True'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'your-jwt-secret-key'
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance/uploads')
    CLOUDINARY_CLOUD_NAME = 'dcvnwpwnu'
    CLOUDINARY_API_KEY = '312535877423432'
    CLOUDINARY_API_SECRET = '3P1aZsINAFGBnNsIoyH2zJDreRo'