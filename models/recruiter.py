from models import db

class RecruiterProfile(db.Model):
    __tablename__ = 'recruiter_profiles'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True)
    designation = db.Column(db.String(100))
    department = db.Column(db.String(100))
    phone = db.Column(db.String(20))

    # Relationships
    jobs = db.relationship('Job', backref='recruiter', lazy=True)

    def __repr__(self):
        return f"<RecruiterProfile user_id={self.user_id}>"
