from app import db

class Images(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50),  nullable=False)
    pathname = db.Column(db.String(50),  nullable=False)
    
    def __repr__(self):
        return '<Images {}>'.format(self.name)