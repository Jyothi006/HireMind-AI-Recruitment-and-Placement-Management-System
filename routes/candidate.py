import os
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import db
from models.candidate import CandidateProfile
from models.job import Job
from models.resume import Resume
from models.application import Application
from models.placement import PlacementDrive, PlacementRecord
from models.assessment import AssessmentAssignment
from models.interview import Interview
from models.offer import Offer
from models.notification import Notification
from services.resume_parser import parse_resume
from services.ai_matching import calculate_ai_match
from services.notification_service import notify_user

candidate_bp = Blueprint('candidate', __name__, url_prefix='/candidate')

def check_candidate():
    if current_user.role != 'candidate':
        flash('Unauthorized access: Candidate area.', 'danger')
        return False
    return True

@candidate_bp.route('/dashboard')
@login_required
def dashboard():
    if not check_candidate():
        return redirect(url_for('index'))

    profile = current_user.candidate_profile
    if not profile:
        profile = CandidateProfile(user_id=current_user.id)
        db.session.add(profile)
        db.session.commit()

    applications = Application.query.filter_by(candidate_id=profile.id).order_by(Application.applied_at.desc()).all()
    assessments = AssessmentAssignment.query.filter_by(candidate_id=profile.id).all()
    interviews = Interview.query.filter_by(candidate_id=profile.id).order_by(Interview.scheduled_time.asc()).all()
    offers = Offer.query.filter_by(candidate_id=profile.id).all()
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).limit(5).all()

    # Eligible Drives
    drives = PlacementDrive.query.filter_by(status='Active').all()
    eligible_drives = [d for d in drives if d.is_candidate_eligible(profile)[0]]

    return render_template(
        'candidate/dashboard.html',
        profile=profile,
        applications=applications,
        assessments=assessments,
        interviews=interviews,
        offers=offers,
        notifications=notifications,
        eligible_drives=eligible_drives
    )


@candidate_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if not check_candidate():
        return redirect(url_for('index'))

    profile = current_user.candidate_profile
    if request.method == 'POST':
        profile.phone = request.form.get('phone', '').strip()
        profile.department = request.form.get('department', '').strip()
        profile.cgpa = float(request.form.get('cgpa', 0.0) or 0.0)
        profile.graduation_year = int(request.form.get('graduation_year', 2026) or 2026)
        profile.backlogs = int(request.form.get('backlogs', 0) or 0)
        profile.bio = request.form.get('bio', '').strip()
        profile.location = request.form.get('location', '').strip()
        profile.qualification = request.form.get('qualification', 'B.Tech').strip()
        profile.experience_years = float(request.form.get('experience_years', 0.0) or 0.0)
        profile.skills = request.form.get('skills', '').strip()
        profile.certifications = request.form.get('certifications', '').strip()

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('candidate.profile'))

    return render_template('candidate/profile.html', profile=profile)


@candidate_bp.route('/resume', methods=['GET', 'POST'])
@login_required
def resume():
    if not check_candidate():
        return redirect(url_for('index'))

    profile = current_user.candidate_profile
    resume_obj = profile.resume

    if request.method == 'POST':
        if 'resume_file' not in request.files:
            flash('No file part selected.', 'danger')
            return redirect(request.url)
        
        file = request.files['resume_file']
        if file.filename == '':
            flash('No selected file.', 'danger')
            return redirect(request.url)

        if file:
            filename = secure_filename(file.filename)
            ext = os.path.splitext(filename)[1].lower().replace('.', '')
            if ext not in current_app.config['ALLOWED_EXTENSIONS']:
                flash('Invalid file extension. Only PDF, DOCX, and TXT allowed.', 'danger')
                return redirect(request.url)

            os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
            save_path = os.path.join(current_app.config['UPLOAD_FOLDER'], f"resume_cand_{profile.id}_{filename}")
            file.save(save_path)

            # AI Resume Parsing
            parsed_data = parse_resume(save_path)

            if not resume_obj:
                resume_obj = Resume(candidate_id=profile.id, filename=filename, filepath=save_path)
                db.session.add(resume_obj)
            else:
                resume_obj.filename = filename
                resume_obj.filepath = save_path

            resume_obj.extracted_text = parsed_data['text']
            resume_obj.set_parsed_skills(parsed_data['skills'])
            resume_obj.extracted_education = parsed_data['education']
            resume_obj.extracted_experience = f"{parsed_data['experience_years']} years"

            # Auto sync extracted skills into candidate profile if profile skills empty
            if parsed_data['skills'] and not profile.skills:
                profile.skills = ", ".join(parsed_data['skills'])

            db.session.commit()
            notify_user(current_user.id, "Resume AI Parsed", f"Your resume '{filename}' was successfully uploaded and parsed by AI Engine.")
            flash('Resume uploaded and parsed successfully by AI Engine!', 'success')
            return redirect(url_for('candidate.resume'))

    return render_template('candidate/resume.html', profile=profile, resume=resume_obj)


@candidate_bp.route('/resume/delete', methods=['POST'])
@login_required
def delete_resume():
    if not check_candidate():
        return redirect(url_for('index'))
    profile = current_user.candidate_profile
    if profile and profile.resume:
        try:
            if os.path.exists(profile.resume.filepath):
                os.remove(profile.resume.filepath)
        except Exception:
            pass
        db.session.delete(profile.resume)
        db.session.commit()
        flash('Resume deleted.', 'info')
    return redirect(url_for('candidate.resume'))


@candidate_bp.route('/jobs')
@login_required
def jobs():
    if not check_candidate():
        return redirect(url_for('index'))

    search = request.args.get('search', '').strip()
    job_type = request.args.get('type', '').strip()

    query = Job.query.filter_by(status='Open')
    if search:
        query = query.filter(Job.title.ilike(f'%{search}%') | Job.required_skills.ilike(f'%{search}%') | Job.description.ilike(f'%{search}%'))
    if job_type:
        query = query.filter_by(job_type=job_type)

    all_jobs = query.order_by(Job.created_at.desc()).all()
    profile = current_user.candidate_profile

    applied_job_ids = [app.job_id for app in Application.query.filter_by(candidate_id=profile.id).all()]

    return render_template('candidate/jobs.html', jobs=all_jobs, profile=profile, applied_job_ids=applied_job_ids, search=search)


@candidate_bp.route('/job/<int:job_id>')
@login_required
def job_detail(job_id):
    if not check_candidate():
        return redirect(url_for('index'))

    job = Job.query.get_or_404(job_id)
    profile = current_user.candidate_profile
    application = Application.query.filter_by(candidate_id=profile.id, job_id=job.id).first()

    # Instant preview of AI match
    ai_match = calculate_ai_match(profile, job, profile.resume)

    return render_template('candidate/job_detail.html', job=job, profile=profile, application=application, ai_match=ai_match)


@candidate_bp.route('/job/<int:job_id>/apply', methods=['POST'])
@login_required
def apply_job(job_id):
    if not check_candidate():
        return redirect(url_for('index'))

    job = Job.query.get_or_404(job_id)
    profile = current_user.candidate_profile

    # One-Student-One-Job Policy Check
    if current_app.config['ONE_STUDENT_ONE_JOB_POLICY'] and 'Placed' in (profile.placement_status or ''):
        flash('Application Restriction Active: You are already placed under the One-Student-One-Job policy.', 'warning')
        return redirect(url_for('candidate.job_detail', job_id=job.id))

    existing_app = Application.query.filter_by(candidate_id=profile.id, job_id=job.id).first()
    if existing_app:
        flash('You have already applied for this position.', 'info')
        return redirect(url_for('candidate.job_detail', job_id=job.id))

    # Calculate real AI match
    match_result = calculate_ai_match(profile, job, profile.resume)

    app_obj = Application(
        candidate_id=profile.id,
        job_id=job.id,
        status='Applied',
        ai_score=match_result['overall_score']
    )
    app_obj.set_ai_details_dict(match_result)

    db.session.add(app_obj)
    db.session.commit()

    notify_user(current_user.id, "Application Submitted", f"Your application for '{job.title}' at {job.company.name} has been submitted with an AI Match score of {match_result['overall_score']}%.", link=url_for('candidate.applications'))
    flash('Application submitted successfully!', 'success')
    return redirect(url_for('candidate.applications'))


@candidate_bp.route('/applications')
@login_required
def applications():
    if not check_candidate():
        return redirect(url_for('index'))

    profile = current_user.candidate_profile
    apps = Application.query.filter_by(candidate_id=profile.id).order_by(Application.applied_at.desc()).all()
    return render_template('candidate/applications.html', applications=apps)


@candidate_bp.route('/offers')
@login_required
def offers():
    if not check_candidate():
        return redirect(url_for('index'))

    profile = current_user.candidate_profile
    offers_list = Offer.query.filter_by(candidate_id=profile.id).order_by(Offer.created_at.desc()).all()
    return render_template('candidate/offers.html', offers=offers_list, profile=profile)


@candidate_bp.route('/offer/<int:offer_id>/respond', methods=['POST'])
@login_required
def respond_offer(offer_id):
    if not check_candidate():
        return redirect(url_for('index'))

    profile = current_user.candidate_profile
    offer = Offer.query.get_or_404(offer_id)
    if offer.candidate_id != profile.id:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('candidate.offers'))

    action = request.form.get('action') # 'accept' or 'reject'

    if action == 'accept':
        offer.status = 'Accepted'
        offer.application.status = 'Offer Accepted'
        profile.placement_status = 'Placed – Application Restrictions Active'

        # Create Placement Record
        precord = PlacementRecord(
            candidate_id=profile.id,
            company_id=offer.company_id,
            job_id=offer.application.job_id,
            offer_id=offer.id,
            package=offer.salary_package
        )
        db.session.add(precord)

        # Notify candidate & recruiters
        notify_user(current_user.id, "Offer Accepted!", f"Congratulations! You accepted the offer from {offer.company.name}. One-Student-One-Job policy active.")
        flash(f'Congratulations! Offer from {offer.company.name} accepted. Placement status updated to Placed.', 'success')

    elif action == 'reject':
        offer.status = 'Rejected'
        offer.application.status = 'Rejected'
        notify_user(current_user.id, "Offer Rejected", f"You rejected the offer from {offer.company.name}.")
        flash('Offer rejected.', 'info')

    db.session.commit()
    return redirect(url_for('candidate.offers'))


@candidate_bp.route('/notifications')
@login_required
def notifications():
    notifs = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.created_at.desc()).all()
    # Mark all read
    for n in notifs:
        n.is_read = True
    db.session.commit()
    return render_template('candidate/notifications.html', notifications=notifs)
