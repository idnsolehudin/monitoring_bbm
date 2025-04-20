from app import db
from datetime import datetime
from app.model.users import Users

class VehicleTypes(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merk = db.Column(db.String(100), nullable=False)
    tipe = db.Column(db.String(50), nullable=False)
    cc = db.Column(db.Integer, nullable=False)
    ratio = db.Column(db.Integer, nullable=False)
    type_encode = db.Column(db.Integer, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey(Users.id))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicles = db.relationship('Vehicles', backref='vehicle_type', lazy=True)

    def __repr__(self):
        return '<VehicleTypes {}>'. format(self.name)
