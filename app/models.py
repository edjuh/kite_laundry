from . import db
from datetime import datetime

class Design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    dimensions = db.Column(db.String(200), nullable=False)
    colors = db.Column(db.String(100))
    rod = db.Column(db.String(50))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    unit_label = db.Column(db.String(10), default='cm')
