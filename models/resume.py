from datetime import datetime
import json
from models import db

class Resume(db.Model):
    __tablename__ = 'resumes'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id'), nullable=False, unique=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text)
    extracted_skills = db.Column(db.Text) # JSON string list
    extracted_education = db.Column(db.String(255))
    extracted_experience = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_parsed_skills(self):
        if not self.extracted_skills:
            return []
        try:
            return json.loads(self.extracted_skills)
        except Exception:
            return [s.strip() for s in self.extracted_skills.split(',') if s.strip()]

    def set_parsed_skills(self, skills_list):
        self.extracted_skills = json.dumps(skills_list)

    def __repr__(self):
        return f"<Resume candidate_id={self.candidate_id} filename={self.filename}>"
