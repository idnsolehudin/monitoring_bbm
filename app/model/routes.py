from app import db
from app.model.users import Users
from datetime import datetime
from app.controller.SoftDeleteMixin import SoftDeleteMixin

class Routes(db.Model, SoftDeleteMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    code = db.Column(db.Integer, unique=True)
    description = db.Column(db.String(50), nullable=False)
    distance = db.Column(db.Integer, nullable=False)
    created_id = db.Column(db.Integer, db.ForeignKey(Users.id))
    created_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, nullable=True)
    
    reports = db.relationship('Reports', backref="route", lazy=True)
    

    def __repr__(self):
        return '<Routes {}>'.format(self.name)