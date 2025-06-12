from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app import db

class SoftDeleteMixin:
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        self.deleted_at = datetime.now()
        

    def restore(self):
        self.deleted_at = None
       