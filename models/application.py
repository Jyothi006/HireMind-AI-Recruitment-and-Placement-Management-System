from datetime import datetime
import json
from models import db

class Application(db.Model):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    placement_drive_id = db.Column(db.Integer, db.ForeignKey('placement_drives.id'), nullable=True)
    status = db.Column(db.String(50), default='Applied') 
    # Statuses: Applied, Under Review, AI Shortlisted, Assessment, Interview, Selected, Rejected, Offer Received, Offer Accepted
    ai_score = db.Column(db.Float, default=0.0)
    ai_details = db.Column(db.Text) # JSON breakdown of matched skills, missing skills, etc.
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    assessment_assignments = db.relationship('AssessmentAssignment', backref='application', lazy=True, cascade='all, delete-orphan')
    interviews = db.relationship('Interview', backref='application', lazy=True, cascade='all, delete-orphan')
    offers = db.relationship('Offer', backref='application', lazy=True, cascade='all, delete-orphan')

    def get_ai_details_dict(self):
        if not self.ai_details:
            return {}
        try:
            return json.loads(self.ai_details)
        except Exception:
            return {}

    def set_ai_details_dict(self, data_dict):
        self.ai_details = json.dumps(data_dict)

    def get_status_badge_class(self):
        badge_map = {
            'Applied': 'bg-secondary',
            'Under Review': 'bg-info text-dark',
            'AI Shortlisted': 'bg-primary',
            'Assessment': 'bg-warning text-dark',
            'Interview': 'bg-purple text-white',
            'Selected': 'bg-success',
            'Rejected': 'bg-danger',
            'Offer Received': 'bg-warning text-dark',
            'Offer Accepted': 'bg-success fw-bold'
        }
        return badge_map.get(self.status, 'bg-secondary')

    def __repr__(self):
        return f"<Application Candidate #{self.candidate_id} -> Job #{self.job_id} Status: {self.status}>"
