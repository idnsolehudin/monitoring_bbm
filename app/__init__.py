from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import  JWTManager

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app,db)

jwt = JWTManager(app)


from app.model import images, users, vehicletypes,routes,vehicles, reports
from app import routes
