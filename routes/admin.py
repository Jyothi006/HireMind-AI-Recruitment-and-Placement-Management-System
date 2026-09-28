from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.candidate import CandidateProfile
from models.recruiter import RecruiterProfile
from models.company import Company
from models.job import Job
from models.placement import PlacementDrive
from models.audit import AuditLog
from services.report_service import get_admin_metrics

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def check_admin():
    if current_user.role != 'admin':
        flash('Unauthorized access: Administrator rights required.', 'danger')
        return False
    return True

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    if not check_admin():
        return redirect(url_for('index'))

    metrics = get_admin_metrics()
    recent_users = User.query.order_by(User.created_at.desc()).limit(8).all()
    audit_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()

    return render_template('admin/dashboard.html', metrics=metrics, recent_users=recent_users, audit_logs=audit_logs)


@admin_bp.route('/users')
@login_required
def users():
    if not check_admin():
        return redirect(url_for('index'))

    users_list = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', users=users_list)


@admin_bp.route('/user/create', methods=['GET', 'POST'])
@login_required
def create_user():
    if not check_admin():
        return redirect(url_for('index'))

    companies = Company.query.all()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'candidate').strip()

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return render_template('admin/create_user.html', companies=companies)

        user = User(email=email, full_name=full_name, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        if role == 'candidate':
            profile = CandidateProfile(user_id=user.id)
            db.session.add(profile)
        elif role in ['recruiter', 'company_rep']:
            company_id = request.form.get('company_id')
            profile = RecruiterProfile(user_id=user.id, company_id=company_id if company_id else None)
            db.session.add(profile)

        # Audit
        audit = AuditLog(user_id=current_user.id, action='Create User', target=email, details=f"Admin created user {email} with role {role}.")
        db.session.add(audit)

        db.session.commit()
        flash(f'User {email} created successfully!', 'success')
        return redirect(url_for('admin.users'))

    return render_template('admin/create_user.html', companies=companies)


@admin_bp.route('/user/<int:user_id>/toggle', methods=['POST'])
@login_required
def toggle_user(user_id):
    if not check_admin():
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot deactivate your own admin account.', 'danger')
        return redirect(url_for('admin.users'))

    user.is_active = not user.is_active
    audit = AuditLog(user_id=current_user.id, action='Toggle User Status', target=user.email, details=f"Status changed to active={user.is_active}")
    db.session.add(audit)
    db.session.commit()

    flash(f"User {user.email} status updated to {'Active' if user.is_active else 'Deactivated'}.", 'info')
    return redirect(url_for('admin.users'))


@admin_bp.route('/logs')
@login_required
def logs():
    if not check_admin():
        return redirect(url_for('index'))

    logs_list = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('admin/logs.html', logs=logs_list)
