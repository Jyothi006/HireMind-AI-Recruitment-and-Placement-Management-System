from datetime import datetime
from models import db

class CandidateProfile(db.Model):
    __tablename__ = 'candidate_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    phone = db.Column(db.String(20))
    department = db.Column(db.String(100)) # e.g. Computer Science, Electronics, Mechanical
    cgpa = db.Column(db.Float, default=0.0)
    graduation_year = db.Column(db.Integer, default=2026)
    backlogs = db.Column(db.Integer, default=0)
    bio = db.Column(db.Text)
    location = db.Column(db.String(100))
    qualification = db.Column(db.String(100), default='B.Tech')
    experience_years = db.Column(db.Float, default=0.0)
    skills = db.Column(db.Text) # Comma-separated or JSON list
    certifications = db.Column(db.Text)
    placement_status = db.Column(db.String(50), default='Unplaced') # Unplaced, Placed, Placed – Application Restrictions Active
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    resume = db.relationship('Resume', backref='candidate', uselist=False, cascade='all, delete-orphan')
    applications = db.relationship('Application', backref='candidate', lazy=True, cascade='all, delete-orphan')
    assessment_assignments = db.relationship('AssessmentAssignment', backref='candidate', lazy=True)
    interviews = db.relationship('Interview', backref='candidate', lazy=True)
    offers = db.relationship('Offer', backref='candidate', lazy=True)
    placement_records = db.relationship('PlacementRecord', backref='candidate', lazy=True)

    def get_skills_list(self):
        if not self.skills:
            return []
        return [s.strip() for s in self.skills.split(',') if s.strip()]

    def calculate_profile_completion(self):
        fields = [self.phone, self.department, self.cgpa, self.bio, self.skills, self.resume]
        completed = sum(1 for f in fields if f)
        return int((completed / len(fields)) * 100)

    def __repr__(self):
        return f"<CandidateProfile user_id={self.user_id}>"
