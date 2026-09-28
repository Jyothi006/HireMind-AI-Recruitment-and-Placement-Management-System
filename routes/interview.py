from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.interview import Interview, InterviewFeedback
from models.application import Application
from services.notification_service import notify_user

interview_bp = Blueprint('interview', __name__, url_prefix='/interview')

@interview_bp.route('/dashboard')
@login_required
def dashboard():
    if current_user.role not in ['interviewer', 'recruiter', 'hiring_manager', 'tpo', 'admin']:
        flash('Unauthorized access: Interviewer area.', 'danger')
        return redirect(url_for('index'))

    assigned_interviews = Interview.query.filter_by(interviewer_id=current_user.id).order_by(Interview.scheduled_time.asc()).all() if current_user.role == 'interviewer' else Interview.query.order_by(Interview.scheduled_time.asc()).all()

    return render_template('interviewer/dashboard.html', interviews=assigned_interviews)


@interview_bp.route('/evaluate/<int:interview_id>', methods=['GET', 'POST'])
@login_required
def evaluate(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    candidate = interview.candidate
    application = interview.application
    resume = candidate.resume

    if request.method == 'POST':
        rating = int(request.form.get('rating', 3))
        technical_score = int(request.form.get('technical_score', 70))
        communication_score = int(request.form.get('communication_score', 70))
        summary = request.form.get('summary', '').strip()
        recommendation = request.form.get('recommendation', 'Select')

        feedback = interview.feedback
        if not feedback:
            feedback = InterviewFeedback(interview_id=interview.id)
            db.session.add(feedback)

        feedback.rating = rating
        feedback.technical_score = technical_score
        feedback.communication_score = communication_score
        feedback.summary = summary
        feedback.recommendation = recommendation
        feedback.submitted_at = datetime.utcnow()

        interview.status = 'Completed'

        # Update application status based on recommendation
        if recommendation == 'Select':
            application.status = 'Selected'
        elif recommendation == 'Reject':
            application.status = 'Rejected'

        db.session.commit()

        notify_user(candidate.user_id, "Interview Feedback Submitted", f"Evaluation for your interview '{interview.title}' has been processed.")
        flash('Interview feedback and evaluation submitted successfully!', 'success')
        return redirect(url_for('interview.dashboard'))

    return render_template('interviewer/evaluate.html', interview=interview, candidate=candidate, application=application, resume=resume)
