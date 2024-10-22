from flask import Flask

app = Flask(__name__)

from app import routes

app.config['SECRET_KEY'] = 'vous-ne-trouverez-jamais'
