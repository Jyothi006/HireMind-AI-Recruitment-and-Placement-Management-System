from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.user import User
from models.recruiter import RecruiterProfile
from models.company import Company
from models.job import Job
from models.application import Application
from models.assessment import Assessment, AssessmentAssignment
from models.interview import Interview
from models.offer import Offer
from services.ai_matching import calculate_ai_match
from services.notification_service import notify_user
from services.report_service import get_recruiter_metrics

recruiter_bp = Blueprint('recruiter', __name__, url_prefix='/recruiter')

def check_recruiter():
    if current_user.role not in ['recruiter', 'company_rep']:
        flash('Unauthorized access: Recruiter area.', 'danger')
        return False
    return True

@recruiter_bp.route('/dashboard')
@login_required
def dashboard():
    if not check_recruiter():
        return redirect(url_for('index'))

    recruiter_profile = current_user.recruiter_profile
    company = recruiter_profile.company if recruiter_profile else None
    
    metrics = get_recruiter_metrics(recruiter_profile.id if recruiter_profile else None)
    jobs = Job.query.filter_by(recruiter_id=recruiter_profile.id).order_by(Job.created_at.desc()).all() if recruiter_profile else Job.query.all()
    
    recent_apps = Application.query.join(Job).filter(Job.recruiter_id == (recruiter_profile.id if recruiter_profile else Job.recruiter_id)).order_by(Application.applied_at.desc()).limit(10).all()

    return render_template('recruiter/dashboard.html', metrics=metrics, jobs=jobs, company=company, recent_apps=recent_apps)


@recruiter_bp.route('/company', methods=['GET', 'POST'])
@login_required
def company_profile():
    if not check_recruiter():
        return redirect(url_for('index'))

    recruiter_profile = current_user.recruiter_profile
    if not recruiter_profile:
        recruiter_profile = RecruiterProfile(user_id=current_user.id)
        db.session.add(recruiter_profile)
        db.session.commit()

    company = recruiter_profile.company

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        website = request.form.get('website', '').strip()
        industry = request.form.get('industry', '').strip()
        description = request.form.get('description', '').strip()
        location = request.form.get('location', '').strip()

        if not company:
            company = Company(name=name, website=website, industry=industry, description=description, location=location)
            db.session.add(company)
            db.session.flush()
            recruiter_profile.company_id = company.id
        else:
            company.name = name
            company.website = website
            company.industry = industry
            company.description = description
            company.location = location

        db.session.commit()
        flash('Company details updated!', 'success')
        return redirect(url_for('recruiter.company_profile'))

    return render_template('recruiter/company_profile.html', company=company)


@recruiter_bp.route('/jobs')
@login_required
def jobs():
    if not check_recruiter():
        return redirect(url_for('index'))

    recruiter_profile = current_user.recruiter_profile
    jobs_list = Job.query.filter_by(recruiter_id=recruiter_profile.id).order_by(Job.created_at.desc()).all() if recruiter_profile else Job.query.all()
    return render_template('recruiter/jobs.html', jobs=jobs_list)


@recruiter_bp.route('/job/create', methods=['GET', 'POST'])
@login_required
def create_job():
    if not check_recruiter():
        return redirect(url_for('index'))

    recruiter_profile = current_user.recruiter_profile
    if not recruiter_profile or not recruiter_profile.company_id:
        flash('Please complete your company profile before posting jobs.', 'warning')
        return redirect(url_for('recruiter.company_profile'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        required_skills = request.form.get('required_skills', '').strip()
        min_qualification = request.form.get('min_qualification', 'B.Tech').strip()
        min_experience = float(request.form.get('min_experience', 0.0) or 0.0)
        salary_package = request.form.get('salary_package', '').strip()
        location = request.form.get('location', '').strip()
        deadline_str = request.form.get('deadline')
        job_type = request.form.get('job_type', 'Full-Time')

        deadline = datetime.strptime(deadline_str, '%Y-%m-%d') if deadline_str else None

        job = Job(
            company_id=recruiter_profile.company_id,
            recruiter_id=recruiter_profile.id,
            title=title,
            description=description,
            required_skills=required_skills,
            min_qualification=min_qualification,
            min_experience=min_experience,
            salary_package=salary_package,
            location=location,
            deadline=deadline,
            job_type=job_type,
            status='Open'
        )
        db.session.add(job)
        db.session.commit()
        flash(f'Job posting "{title}" created successfully!', 'success')
        return redirect(url_for('recruiter.jobs'))

    return render_template('recruiter/create_job.html')


@recruiter_bp.route('/job/<int:job_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_job(job_id):
    if not check_recruiter():
        return redirect(url_for('index'))

    job = Job.query.get_or_404(job_id)
    if request.method == 'POST':
        job.title = request.form.get('title', '').strip()
        job.description = request.form.get('description', '').strip()
        job.required_skills = request.form.get('required_skills', '').strip()
        job.min_qualification = request.form.get('min_qualification', 'B.Tech').strip()
        job.min_experience = float(request.form.get('min_experience', 0.0) or 0.0)
        job.salary_package = request.form.get('salary_package', '').strip()
        job.location = request.form.get('location', '').strip()
        job.status = request.form.get('status', 'Open')
        job.job_type = request.form.get('job_type', 'Full-Time')

        deadline_str = request.form.get('deadline')
        if deadline_str:
            job.deadline = datetime.strptime(deadline_str, '%Y-%m-%d')

        db.session.commit()
        flash('Job details updated!', 'success')
        return redirect(url_for('recruiter.jobs'))

    return render_template('recruiter/edit_job.html', job=job)


@recruiter_bp.route('/job/<int:job_id>/applicants')
@login_required
def job_applicants(job_id):
    if not check_recruiter():
        return redirect(url_for('index'))

    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job.id).order_by(Application.ai_score.desc()).all()

    return render_template('recruiter/job_applicants.html', job=job, applications=applications)


@recruiter_bp.route('/job/<int:job_id>/ai-rank')
@login_required
def ai_rank_candidates(job_id):
    if not check_recruiter():
        return redirect(url_for('index'))

    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job.id).all()

    # Run AI engine for each candidate
    ranked_results = []
    for app_obj in applications:
        match_result = calculate_ai_match(app_obj.candidate, job, app_obj.candidate.resume)
        app_obj.ai_score = match_result['overall_score']
        app_obj.set_ai_details_dict(match_result)
        ranked_results.append({
            'application': app_obj,
            'match': match_result
        })

    db.session.commit()

    # Sort descending by score
    ranked_results.sort(key=lambda x: x['match']['overall_score'], reverse=True)

    return render_template('recruiter/ai_ranking.html', job=job, ranked_results=ranked_results)


@recruiter_bp.route('/application/<int:app_id>/status', methods=['POST'])
@login_required
def update_app_status(app_id):
    if not check_recruiter():
        return redirect(url_for('index'))

    app_obj = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')
    
    if new_status:
        app_obj.status = new_status
        db.session.commit()
        notify_user(app_obj.candidate.user_id, "Application Status Update", f"Your application status for '{app_obj.job.title}' has been updated to '{new_status}'.", link=url_for('candidate.applications'))
        flash(f'Candidate status updated to {new_status}.', 'success')

    return redirect(request.referrer or url_for('recruiter.jobs'))


@recruiter_bp.route('/schedule-interview/<int:app_id>', methods=['GET', 'POST'])
@login_required
def schedule_interview(app_id):
    if not check_recruiter():
        return redirect(url_for('index'))

    app_obj = Application.query.get_or_404(app_id)
    interviewers = User.query.filter(User.role.in_(['interviewer', 'recruiter', 'hiring_manager'])).all()

    if request.method == 'POST':
        interviewer_id = int(request.form.get('interviewer_id'))
        title = request.form.get('title', f"Interview for {app_obj.job.title}").strip()
        interview_type = request.form.get('interview_type', 'Technical')
        scheduled_time_str = request.form.get('scheduled_time')
        duration = int(request.form.get('duration_minutes', 45))
        location_or_link = request.form.get('location_or_link', 'Online Meeting')
        instructions = request.form.get('instructions', '')

        scheduled_time = datetime.strptime(scheduled_time_str, '%Y-%m-%dT%H:%M') if scheduled_time_str else datetime.utcnow()

        interview = Interview(
            application_id=app_obj.id,
            candidate_id=app_obj.candidate_id,
            interviewer_id=interviewer_id,
            title=title,
            interview_type=interview_type,
            scheduled_time=scheduled_time,
            duration_minutes=duration,
            location_or_link=location_or_link,
            instructions=instructions,
            status='Scheduled'
        )
        app_obj.status = 'Interview'
        db.session.add(interview)
        db.session.commit()

        # Notify Candidate & Interviewer
        notify_user(app_obj.candidate.user_id, "Interview Scheduled", f"An interview '{title}' ({interview_type}) has been scheduled for {scheduled_time.strftime('%b %d, %Y %I:%M %p')}.", link=url_for('candidate.dashboard'))
        notify_user(interviewer_id, "New Interview Assigned", f"You have been assigned to conduct an interview '{title}' for candidate {app_obj.candidate.user.full_name}.", link=url_for('interview.dashboard'))

        flash('Interview scheduled successfully!', 'success')
        return redirect(url_for('recruiter.job_applicants', job_id=app_obj.job_id))

    return render_template('recruiter/schedule_interview.html', application=app_obj, interviewers=interviewers)


@recruiter_bp.route('/generate-offer/<int:app_id>', methods=['GET', 'POST'])
@login_required
def generate_offer(app_id):
    if not check_recruiter():
        return redirect(url_for('index'))

    app_obj = Application.query.get_or_404(app_id)

    if request.method == 'POST':
        salary_package = request.form.get('salary_package', '').strip()
        joining_date_str = request.form.get('joining_date')
        deadline_str = request.form.get('deadline')
        offer_letter_text = request.form.get('offer_letter_text', '')

        joining_date = datetime.strptime(joining_date_str, '%Y-%m-%d')
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')

        offer = Offer(
            application_id=app_obj.id,
            candidate_id=app_obj.candidate_id,
            company_id=app_obj.job.company_id,
            job_title=app_obj.job.title,
            salary_package=salary_package,
            joining_date=joining_date,
            deadline=deadline,
            offer_letter_text=offer_letter_text,
            status='Sent'
        )
        app_obj.status = 'Offer Received'
        db.session.add(offer)
        db.session.commit()

        notify_user(app_obj.candidate.user_id, "Official Offer Received!", f"You have received an official offer for '{app_obj.job.title}' with package {salary_package}!", link=url_for('candidate.offers'))
        flash('Digital offer letter generated and sent to candidate!', 'success')
        return redirect(url_for('recruiter.job_applicants', job_id=app_obj.job_id))

    return render_template('recruiter/generate_offer.html', application=app_obj)
