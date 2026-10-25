from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.application import Application
from models.interview import Interview
from models.offer import Offer

hiring_bp = Blueprint('hiring', __name__, url_prefix='/hiring')

def check_hiring_manager():
    if current_user.role not in ['hiring_manager', 'recruiter', 'admin']:
        flash('Unauthorized access: Hiring Manager area.', 'danger')
        return False
    return True

@hiring_bp.route('/dashboard')
@login_required
def dashboard():
    if not check_hiring_manager():
        return redirect(url_for('index'))

    shortlisted_apps = Application.query.filter(Application.status.in_(['AI Shortlisted', 'Assessment', 'Interview', 'Selected'])).order_by(Application.ai_score.desc()).all()
    recent_offers = Offer.query.order_by(Offer.created_at.desc()).all()

    return render_template('hiring_manager/dashboard.html', applications=shortlisted_apps, offers=recent_offers)


@hiring_bp.route('/select/<int:app_id>', methods=['POST'])
@login_required
def select_candidate(app_id):
    if not check_hiring_manager():
        return redirect(url_for('index'))

    app_obj = Application.query.get_or_404(app_id)
    app_obj.status = 'Selected'
    db.session.commit()

    flash(f'Candidate {app_obj.candidate.user.full_name} selected for offer stage!', 'success')
    return redirect(url_for('hiring.dashboard'))
