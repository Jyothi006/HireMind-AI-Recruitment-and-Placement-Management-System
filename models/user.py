from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from models import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(30), nullable=False) # candidate, recruiter, interviewer, hiring_manager, tpo, company_rep, admin
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    candidate_profile = db.relationship('CandidateProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    recruiter_profile = db.relationship('RecruiterProfile', backref='user', uselist=False, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_role_display(self):
        role_names = {
            'candidate': 'Candidate / Student',
            'recruiter': 'Recruiter / HR',
            'interviewer': 'Interviewer',
            'hiring_manager': 'Hiring Manager',
            'tpo': 'Placement Officer / TPO',
            'company_rep': 'Company Representative',
            'admin': 'System Administrator'
        }
        return role_names.get(self.role, self.role.title())

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
