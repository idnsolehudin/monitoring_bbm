from app import db
from app.model.users import Users
from datetime import datetime
from app.controller.SoftDeleteMixin import SoftDeleteMixin

class Vehicles(db.Model, SoftDeleteMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    nopol = db.Column(db.String(50), unique=True, nullable=False)
    images = db.Column(db.String(255))
    type_id = db.Column(db.Integer, db.ForeignKey('vehicle_types.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)

    reports = db.relationship('Reports', backref='vehicle', lazy=True)
    
    def __repr__(self):
        return '<Vehicles {}>'.format(self.name)