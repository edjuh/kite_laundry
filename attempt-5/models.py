from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Design(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    dimensions = db.Column(db.Text, nullable=False)
    colors = db.Column(db.Text, nullable=False)
    rod = db.Column(db.String(50))
    creation_date = db.Column(db.String(50), nullable=False)
    unit_label = db.Column(db.String(10), default='cm')
