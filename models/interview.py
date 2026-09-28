from datetime import datetime
from models import db

class Interview(db.Model):
    __tablename__ = 'interviews'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id'), nullable=False)
    interviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    interview_type = db.Column(db.String(50), default='Technical') # Technical, HR, Managerial, Campus Interview
    scheduled_time = db.Column(db.DateTime, nullable=False)
    duration_minutes = db.Column(db.Integer, default=45)
    location_or_link = db.Column(db.String(255), default='Online Meeting Room')
    instructions = db.Column(db.Text)
    status = db.Column(db.String(20), default='Scheduled') # Scheduled, Completed, Cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    interviewer = db.relationship('User', foreign_keys=[interviewer_id])
    feedback = db.relationship('InterviewFeedback', backref='interview', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Interview {self.title} Candidate #{self.candidate_id}>"


class InterviewFeedback(db.Model):
    __tablename__ = 'interview_feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    interview_id = db.Column(db.Integer, db.ForeignKey('interviews.id'), nullable=False, unique=True)
    rating = db.Column(db.Integer, default=3) # 1-5
    technical_score = db.Column(db.Integer, default=70) # 0-100
    communication_score = db.Column(db.Integer, default=70) # 0-100
    summary = db.Column(db.Text)
    recommendation = db.Column(db.String(30), default='Select') # Select, Reject, Further Review
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<InterviewFeedback Interview #{self.interview_id} Rec: {self.recommendation}>"
