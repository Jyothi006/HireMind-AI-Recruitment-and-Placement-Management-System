from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from models.candidate import CandidateProfile
from models.recruiter import RecruiterProfile
from models.company import Company
from models.audit import AuditLog

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_to_role_dashboard(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', '').strip()

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return render_template('auth/login.html')

        if not user.is_active:
            flash('Your account has been deactivated by administration.', 'warning')
            return render_template('auth/login.html')

        if role and user.role != role:
            flash(f'Account exists, but your registered role is {user.get_role_display()}.', 'warning')
            return render_template('auth/login.html')

        login_user(user)

        # Audit Log
        audit = AuditLog(user_id=user.id, action='Login', target='System', details=f"User {user.email} logged in successfully.")
        db.session.add(audit)
        db.session.commit()

        flash(f'Welcome back, {user.full_name}!', 'success')
        return redirect_to_role_dashboard(user.role)

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect_to_role_dashboard(current_user.role)

    companies = Company.query.all()

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', '').strip()

        # Prevent direct admin registration
        if role == 'admin':
            flash('Administrator accounts cannot be registered publicly.', 'danger')
            return render_template('auth/register.html', companies=companies)

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash('An account with this email already exists.', 'danger')
            return render_template('auth/register.html', companies=companies)

        new_user = User(email=email, full_name=full_name, role=role)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Create Role Specific Profiles
        if role == 'candidate':
            department = request.form.get('department', 'Computer Science')
            cgpa = float(request.form.get('cgpa', 0.0) or 0.0)
            grad_year = int(request.form.get('graduation_year', 2026) or 2026)
            profile = CandidateProfile(
                user_id=new_user.id,
                department=department,
                cgpa=cgpa,
                graduation_year=grad_year
            )
            db.session.add(profile)
        elif role == 'recruiter':
            company_id = request.form.get('company_id')
            designation = request.form.get('designation', 'HR Recruiter')
            profile = RecruiterProfile(
                user_id=new_user.id,
                company_id=company_id if company_id else None,
                designation=designation
            )
            db.session.add(profile)

        # Audit Log
        audit = AuditLog(user_id=new_user.id, action='Register', target='System', details=f"New user {email} registered as {role}.")
        db.session.add(audit)

        db.session.commit()
        flash('Registration successful! Please login with your credentials.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', companies=companies)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


def redirect_to_role_dashboard(role):
    if role == 'candidate':
        return redirect(url_for('candidate.dashboard'))
    elif role == 'recruiter':
        return redirect(url_for('recruiter.dashboard'))
    elif role == 'tpo':
        return redirect(url_for('placement.dashboard'))
    elif role == 'interviewer':
        return redirect(url_for('interview.dashboard'))
    elif role == 'hiring_manager':
        return redirect(url_for('hiring.dashboard'))
    elif role == 'company_rep':
        return redirect(url_for('recruiter.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('index'))
