from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement = True)
    nik = db.Column(db.Integer, index=True, unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    created_at =db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    image = db.Column(db.String(50))

    routes = db.relationship('Routes', backref='creator', lazy=True)
    vehicle_types = db.relationship('VehicleTypes', backref='creator', lazy=True)
    vehicles = db.relationship('Vehicles', backref='creator', lazy=True)
    reports = db.relationship('Reports', backref='creator', lazy=True)
    

    def __repr__(self): 
        return '<Users {}>'.format(self.name)
    
    def setPassword(self, password):
        self.password = generate_password_hash(password)

    def checkPassword(self, password):
        return check_password_hash(self.password, password)