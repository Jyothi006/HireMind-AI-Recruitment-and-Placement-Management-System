from datetime import datetime
from models import db

class Job(db.Model):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    recruiter_id = db.Column(db.Integer, db.ForeignKey('recruiter_profiles.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False) # Comma-separated
    min_qualification = db.Column(db.String(100), default='B.Tech')
    min_experience = db.Column(db.Float, default=0.0)
    salary_package = db.Column(db.String(100)) # e.g. "8-12 LPA" or "$80,000/yr"
    location = db.Column(db.String(100))
    deadline = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(20), default='Open') # Open, Closed, Draft
    job_type = db.Column(db.String(50), default='Full-Time') # Full-Time, Placement Drive, Internship
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='job', lazy=True, cascade='all, delete-orphan')
    placement_drives = db.relationship('PlacementDrive', backref='job', lazy=True)

    def get_required_skills_list(self):
        if not self.required_skills:
            return []
        return [s.strip() for s in self.required_skills.split(',') if s.strip()]

    def is_expired(self):
        if self.deadline and datetime.utcnow() > self.deadline:
            return True
        return False

    def __repr__(self):
        return f"<Job {self.title} at Company #{self.company_id}>"
