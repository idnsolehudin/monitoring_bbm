from app import db
from app.model.users import Users
from app.model.routes import Routes
from app.model.vehicles import Vehicles
from datetime import datetime
from enum import Enum
from app.controller.SoftDeleteMixin import SoftDeleteMixin

class Reports(db.Model, SoftDeleteMixin):
    id =  db.Column(db.Integer, primary_key=True, autoincrement=True)
    shipment = db.Column(db.BigInteger, nullable=False)
    route_id = db.Column(db.Integer,db.ForeignKey(Routes.id), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey(Vehicles.id), nullable=False)
    spbu_code = db.Column(db.BigInteger, nullable=False)
    first_km = db.Column(db.Integer, nullable=False)
    last_km = db.Column(db.Integer, nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    ratio = db.Column(db.Integer, nullable=False)
    volume = db.Column(db.Integer, nullable=False)
    receipt = db.Column(db.String(255), nullable=False)
    odometer = db.Column(db.String(255), nullable=False)
    dispenser = db.Column(db.String(255), nullable=False)
    fulfillment = db.Column(db.String(255), nullable=False)
    similarity = db.Column(db.Float, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey(Users.id), nullable=False)
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return '<Reports {}>'.format(self.name)