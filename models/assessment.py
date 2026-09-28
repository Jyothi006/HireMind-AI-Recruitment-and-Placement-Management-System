from datetime import datetime
from models import db

class Assessment(db.Model):
    __tablename__ = 'assessments'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50), default='Technical') # Aptitude, Technical, Programming, General Skill
    duration_minutes = db.Column(db.Integer, default=30)
    pass_marks = db.Column(db.Integer, default=60) # percentage or score
    total_marks = db.Column(db.Integer, default=100)
    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    questions = db.relationship('Question', backref='assessment', lazy=True, cascade='all, delete-orphan')
    assignments = db.relationship('AssessmentAssignment', backref='assessment', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Assessment {self.title}>"


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    option_a = db.Column(db.String(255), nullable=False)
    option_b = db.Column(db.String(255), nullable=False)
    option_c = db.Column(db.String(255), nullable=False)
    option_d = db.Column(db.String(255), nullable=False)
    correct_option = db.Column(db.String(1), nullable=False) # 'A', 'B', 'C', 'D'
    marks = db.Column(db.Integer, default=10)

    def __repr__(self):
        return f"<Question #{self.id} for Assessment #{self.assessment_id}>"


class AssessmentAssignment(db.Model):
    __tablename__ = 'assessment_assignments'

    id = db.Column(db.Integer, primary_key=True)
    assessment_id = db.Column(db.Integer, db.ForeignKey('assessments.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate_profiles.id'), nullable=False)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=True)
    status = db.Column(db.String(20), default='Assigned') # Assigned, Started, Completed
    score = db.Column(db.Integer, default=0)
    passed = db.Column(db.Boolean, default=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<AssessmentAssignment Assessment #{self.assessment_id} Candidate #{self.candidate_id} Score: {self.score}>"
