from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db
from models.assessment import Assessment, Question, AssessmentAssignment
from models.application import Application
from models.candidate import CandidateProfile
from services.notification_service import notify_user

assessment_bp = Blueprint('assessment', __name__, url_prefix='/assessment')

@assessment_bp.route('/list')
@login_required
def list_assessments():
    assessments = Assessment.query.order_by(Assessment.created_at.desc()).all()
    return render_template('assessment/list.html', assessments=assessments)


@assessment_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_assessment():
    if current_user.role not in ['recruiter', 'tpo', 'admin']:
        flash('Unauthorized to create assessments.', 'danger')
        return redirect(url_for('assessment.list_assessments'))

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        category = request.form.get('category', 'Technical')
        duration = int(request.form.get('duration_minutes', 30))
        pass_marks = int(request.form.get('pass_marks', 60))

        assessment = Assessment(
            title=title,
            description=description,
            category=category,
            duration_minutes=duration,
            pass_marks=pass_marks,
            created_by_id=current_user.id
        )
        db.session.add(assessment)
        db.session.commit()
        flash('Assessment created! Now add multiple-choice questions.', 'success')
        return redirect(url_for('assessment.manage_questions', assessment_id=assessment.id))

    return render_template('assessment/create.html')


@assessment_bp.route('/<int:assessment_id>/questions', methods=['GET', 'POST'])
@login_required
def manage_questions(assessment_id):
    assessment = Assessment.query.get_or_404(assessment_id)

    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        option_a = request.form.get('option_a', '').strip()
        option_b = request.form.get('option_b', '').strip()
        option_c = request.form.get('option_c', '').strip()
        option_d = request.form.get('option_d', '').strip()
        correct_option = request.form.get('correct_option', 'A').strip().upper()
        marks = int(request.form.get('marks', 10))

        q = Question(
            assessment_id=assessment.id,
            text=text,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            marks=marks
        )
        db.session.add(q)
        
        # Update total marks
        assessment.total_marks = sum([q.marks for q in assessment.questions]) + marks
        db.session.commit()
        flash('Question added!', 'success')
        return redirect(url_for('assessment.manage_questions', assessment_id=assessment.id))

    return render_template('assessment/manage_questions.html', assessment=assessment)


@assessment_bp.route('/assign/<int:app_id>', methods=['GET', 'POST'])
@login_required
def assign_assessment(app_id):
    if current_user.role not in ['recruiter', 'tpo', 'admin']:
        flash('Unauthorized action.', 'danger')
        return redirect(url_for('index'))

    app_obj = Application.query.get_or_404(app_id)
    assessments = Assessment.query.all()

    if request.method == 'POST':
        assessment_id = int(request.form.get('assessment_id'))

        existing = AssessmentAssignment.query.filter_by(assessment_id=assessment_id, candidate_id=app_obj.candidate_id, application_id=app_obj.id).first()
        if existing:
            flash('Assessment already assigned to candidate.', 'info')
            return redirect(url_for('recruiter.job_applicants', job_id=app_obj.job_id))

        assignment = AssessmentAssignment(
            assessment_id=assessment_id,
            candidate_id=app_obj.candidate_id,
            application_id=app_obj.id,
            status='Assigned'
        )
        app_obj.status = 'Assessment'
        db.session.add(assignment)
        db.session.commit()

        notify_user(app_obj.candidate.user_id, "Skill Assessment Assigned", f"You have been assigned the '{assignment.assessment.title}' assessment. Complete it from your dashboard.", link=url_for('candidate.dashboard'))
        flash('Assessment assigned to candidate successfully!', 'success')
        return redirect(url_for('recruiter.job_applicants', job_id=app_obj.job_id))

    return render_template('assessment/assign.html', application=app_obj, assessments=assessments)


@assessment_bp.route('/take/<int:assignment_id>', methods=['GET', 'POST'])
@login_required
def take_assessment(assignment_id):
    assignment = AssessmentAssignment.query.get_or_404(assignment_id)
    if current_user.role == 'candidate' and assignment.candidate_id != current_user.candidate_profile.id:
        flash('Unauthorized to take this test.', 'danger')
        return redirect(url_for('candidate.dashboard'))

    if assignment.status == 'Completed':
        flash('You have already completed this assessment.', 'info')
        return render_template('assessment/result.html', assignment=assignment)

    assessment = assignment.assessment

    if request.method == 'POST':
        total_score = 0
        total_possible = 0

        for q in assessment.questions:
            total_possible += q.marks
            user_ans = request.form.get(f'question_{q.id}')
            if user_ans and user_ans.strip().upper() == q.correct_option:
                total_score += q.marks

        score_percent = int((total_score / total_possible) * 100) if total_possible > 0 else 0
        passed = score_percent >= assessment.pass_marks

        assignment.score = score_percent
        assignment.passed = passed
        assignment.status = 'Completed'
        assignment.completed_at = datetime.utcnow()

        if assignment.application:
            assignment.application.status = 'Assessment'

        db.session.commit()

        notify_user(assignment.candidate.user_id, "Assessment Completed", f"Your result for '{assessment.title}': {score_percent}% ({'PASSED' if passed else 'FAILED'}).")
        flash(f'Assessment completed! Score: {score_percent}% ({'PASSED' if passed else 'FAILED'})', 'success')
        return render_template('assessment/result.html', assignment=assignment)

    assignment.status = 'Started'
    db.session.commit()

    return render_template('assessment/take.html', assignment=assignment, assessment=assessment)
