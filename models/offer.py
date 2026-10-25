from datetime import datetime
from models import db

class Offer(db.Model):
    __tablename__ = 'offers'

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_title = db.Column(db.String(150), nullable=False)
    salary_package = db.Column(db.String(100), nullable=False)
    joining_date = db.Column(db.DateTime, nullable=False)
    offer_letter_text = db.Column(db.Text)
    deadline = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='Sent') # Generated, Sent, Accepted, Rejected, Expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    company = db.relationship('Company', backref='offers')

    def __repr__(self):
        return f"<Offer Candidate #{self.candidate_id} Company #{self.company_id} Status: {self.status}>"
