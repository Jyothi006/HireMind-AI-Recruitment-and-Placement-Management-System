from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.candidate import CandidateProfile
from models.company import Company
from models.job import Job
from models.placement import PlacementDrive, PlacementRecord
from models.application import Application
from services.report_service import get_tpo_metrics
from services.notification_service import notify_user

placement_bp = Blueprint('placement', __name__, url_prefix='/placement')

def check_tpo():
    if current_user.role != 'tpo':
        flash('Unauthorized access: Placement Officer (TPO) area.', 'danger')
        return False
    return True

@placement_bp.route('/dashboard')
@login_required
def dashboard():
    if not check_tpo():
        return redirect(url_for('index'))

    metrics = get_tpo_metrics()
    drives = PlacementDrive.query.order_by(PlacementDrive.drive_date.desc()).all()
    recent_placements = PlacementRecord.query.order_by(PlacementRecord.placement_date.desc()).limit(10).all()

    return render_template('placement/dashboard.html', metrics=metrics, drives=drives, recent_placements=recent_placements)


@placement_bp.route('/students')
@login_required
def students():
    if not check_tpo():
        return redirect(url_for('index'))

    search = request.args.get('search', '').strip()
    dept = request.args.get('department', '').strip()
    status = request.args.get('status', '').strip()

    query = CandidateProfile.query.join(User)
    if search:
        query = query.filter(User.full_name.ilike(f'%{search}%') | User.email.ilike(f'%{search}%') | CandidateProfile.skills.ilike(f'%{search}%'))
    if dept:
        query = query.filter(CandidateProfile.department == dept)
    if status:
        query = query.filter(CandidateProfile.placement_status.like(f'%{status}%'))

    students_list = query.all()
    departments = [d[0] for d in db.session.query(CandidateProfile.department).distinct().all() if d[0]]

    return render_template('placement/students.html', students=students_list, departments=departments, search=search)


@placement_bp.route('/companies', methods=['GET', 'POST'])
@login_required
def companies():
    if not check_tpo():
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        website = request.form.get('website', '').strip()
        industry = request.form.get('industry', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()

        if Company.query.filter_by(name=name).first():
            flash('A company with this name already exists.', 'warning')
        else:
            comp = Company(name=name, website=website, industry=industry, description=description, location=location)
            db.session.add(comp)
            db.session.commit()
            flash(f'Company "{name}" added to placement network!', 'success')
            return redirect(url_for('placement.companies'))

    companies_list = Company.query.order_by(Company.name.asc()).all()
    return render_template('placement/companies.html', companies=companies_list)


@placement_bp.route('/drives')
@login_required
def drives():
    if not check_tpo():
        return redirect(url_for('index'))

    drives_list = PlacementDrive.query.order_by(PlacementDrive.drive_date.desc()).all()
    return render_template('placement/drives.html', drives=drives_list)


@placement_bp.route('/drive/create', methods=['GET', 'POST'])
@login_required
def create_drive():
    if not check_tpo():
        return redirect(url_for('index'))

    companies_list = Company.query.all()
    jobs_list = Job.query.filter_by(status='Open').all()

    if request.method == 'POST':
        company_id = int(request.form.get('company_id'))
        job_id = request.form.get('job_id')
        title = request.form.get('title', '').strip()
        drive_date_str = request.form.get('drive_date')
        venue = request.form.get('venue', 'Campus Auditorium')
        min_cgpa = float(request.form.get('min_cgpa', 6.0) or 6.0)
        eligible_branches = request.form.get('eligible_branches', 'Computer Science, Electronics')
        max_backlogs = int(request.form.get('max_backlogs', 0) or 0)
        graduation_year = int(request.form.get('graduation_year', 2026) or 2026)

        drive_date = datetime.strptime(drive_date_str, '%Y-%m-%d') if drive_date_str else datetime.utcnow()

        drive = PlacementDrive(
            company_id=company_id,
            job_id=int(job_id) if job_id else None,
            title=title,
            drive_date=drive_date,
            venue=venue,
            min_cgpa=min_cgpa,
            eligible_branches=eligible_branches,
            max_backlogs=max_backlogs,
            graduation_year=graduation_year,
            status='Active'
        )
        db.session.add(drive)
        db.session.commit()

        # Notify all students
        candidates = CandidateProfile.query.all()
        for c in candidates:
            is_elig, reason = drive.is_candidate_eligible(c)
            if is_elig:
                notify_user(c.user_id, "New Placement Drive Scheduled", f"You are eligible for '{title}' on {drive_date.strftime('%b %d, %Y')}.", link=url_for('candidate.dashboard'))

        flash(f'Placement Drive "{title}" created!', 'success')
        return redirect(url_for('placement.drives'))

    return render_template('placement/create_drive.html', companies=companies_list, jobs=jobs_list)


@placement_bp.route('/drive/<int:drive_id>')
@login_required
def drive_detail(drive_id):
    if not check_tpo():
        return redirect(url_for('index'))

    drive = PlacementDrive.query.get_or_404(drive_id)
    all_candidates = CandidateProfile.query.all()

    eligible_candidates = []
    ineligible_candidates = []

    for c in all_candidates:
        is_elig, reason = drive.is_candidate_eligible(c)
        if is_elig:
            eligible_candidates.append((c, reason))
        else:
            ineligible_candidates.append((c, reason))

    return render_template('placement/drive_detail.html', drive=drive, eligible=eligible_candidates, ineligible=ineligible_candidates)


@placement_bp.route('/drive/<int:drive_id>/hall-tickets')
@login_required
def hall_tickets(drive_id):
    if not check_tpo():
        return redirect(url_for('index'))

    drive = PlacementDrive.query.get_or_404(drive_id)
    all_candidates = CandidateProfile.query.all()
    eligible_students = [c for c in all_candidates if drive.is_candidate_eligible(c)[0]]

    return render_template('placement/hall_tickets.html', drive=drive, students=eligible_students)


@placement_bp.route('/reports')
@login_required
def reports():
    if not check_tpo():
        return redirect(url_for('index'))

    metrics = get_tpo_metrics()
    placements = PlacementRecord.query.order_by(PlacementRecord.placement_date.desc()).all()

    return render_template('placement/reports.html', metrics=metrics, placements=placements)
