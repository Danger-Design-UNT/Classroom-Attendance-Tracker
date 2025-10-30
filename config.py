import os

class Config:
    SECRET_KEY = 'replace-this-with-a-secure-random-key'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
