import os

class Config:
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/westingen')
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
