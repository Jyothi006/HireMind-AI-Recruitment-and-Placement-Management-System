from datetime import datetime
from models import db

class PlacementDrive(db.Model):
    __tablename__ = 'placement_drives'

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    drive_date = db.Column(db.DateTime, nullable=False)
    venue = db.Column(db.String(150), default='Campus Auditorium & Online')
    min_cgpa = db.Column(db.Float, default=6.0)
    eligible_branches = db.Column(db.Text, default='Computer Science, Electronics, Information Technology')
    max_backlogs = db.Column(db.Integer, default=0)
    graduation_year = db.Column(db.Integer, default=2026)
    status = db.Column(db.String(20), default='Upcoming') # Upcoming, Active, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship('Application', backref='placement_drive', lazy=True)

    def get_eligible_branches_list(self):
        if not self.eligible_branches:
            return []
        return [b.strip() for b in self.eligible_branches.split(',') if b.strip()]

    def is_candidate_eligible(self, candidate_profile):
        if not candidate_profile:
            return False, "Candidate profile incomplete."
        if candidate_profile.cgpa < self.min_cgpa:
            return False, f"CGPA requirement not met ({candidate_profile.cgpa} < {self.min_cgpa})."
        if candidate_profile.backlogs > self.max_backlogs:
            return False, f"Backlogs limit exceeded ({candidate_profile.backlogs} > {self.max_backlogs})."
        if candidate_profile.graduation_year != self.graduation_year:
            return False, f"Graduation year mismatch ({candidate_profile.graduation_year} != {self.graduation_year})."
        
        branches = [b.lower() for b in self.get_eligible_branches_list()]
        if branches and candidate_profile.department and candidate_profile.department.lower() not in branches:
            return False, f"Department '{candidate_profile.department}' is not eligible."

        return True, "Eligible"

    def __repr__(self):
        return f"<PlacementDrive {self.title}>"


class PlacementRecord(db.Model):
    __tablename__ = 'placement_records'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=True)
    offer_id = db.Column(db.Integer, db.ForeignKey('offers.id'), nullable=True)
    package = db.Column(db.String(100))
    placement_date = db.Column(db.DateTime, default=datetime.utcnow)

    company = db.relationship('Company', backref='placement_records')
    job = db.relationship('Job', backref='placement_records')

    def __repr__(self):
        return f"<PlacementRecord Candidate #{self.candidate_id} -> Company #{self.company_id}>"
