from datetime import datetime
from models import db

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    website = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    logo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    recruiters = db.relationship('RecruiterProfile', backref='company', lazy=True)
    jobs = db.relationship('Job', backref='company', lazy=True)
    placement_drives = db.relationship('PlacementDrive', backref='company', lazy=True)

    def __repr__(self):
        return f"<Company {self.name}>"
