from datetime import datetime
from models import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    target = db.Column(db.String(150), nullable=True)
    details = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f"<AuditLog action='{self.action}' by user_id={self.user_id}>"
