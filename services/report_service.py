from models import db
from models.user import User
from models.candidate import CandidateProfile
from models.company import Company
from models.job import Job
from models.application import Application
from models.placement import PlacementDrive, PlacementRecord
from models.offer import Offer

def get_admin_metrics():
    total_candidates = CandidateProfile.query.count()
    total_recruiters = User.query.filter_by(role='recruiter').count()
    total_jobs = Job.query.count()
    total_companies = Company.query.count()
    total_drives = PlacementDrive.query.count()
    total_applications = Application.query.count()
    total_selected = Application.query.filter(Application.status.in_(['Selected', 'Offer Received', 'Offer Accepted'])).count()
    total_placed = PlacementRecord.query.count()

    # Job status distribution
    open_jobs = Job.query.filter_by(status='Open').count()
    closed_jobs = Job.query.filter_by(status='Closed').count()
    draft_jobs = Job.query.filter_by(status='Draft').count()

    # Application statuses
    status_counts = {
        'Applied': Application.query.filter_by(status='Applied').count(),
        'AI Shortlisted': Application.query.filter_by(status='AI Shortlisted').count(),
        'Assessment': Application.query.filter_by(status='Assessment').count(),
        'Interview': Application.query.filter_by(status='Interview').count(),
        'Selected': total_selected,
        'Rejected': Application.query.filter_by(status='Rejected').count()
    }

    return {
        'total_candidates': total_candidates,
        'total_recruiters': total_recruiters,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_drives': total_drives,
        'total_applications': total_applications,
        'total_selected': total_selected,
        'total_placed': total_placed,
        'job_status_dist': {'Open': open_jobs, 'Closed': closed_jobs, 'Draft': draft_jobs},
        'app_status_dist': status_counts
    }


def get_tpo_metrics():
    total_students = CandidateProfile.query.count()
    placed_students = CandidateProfile.query.filter(CandidateProfile.placement_status.like('Placed%')).count()
    unplaced_students = total_students - placed_students
    drives = PlacementDrive.query.all()
    companies = Company.query.count()

    # Branch wise placements
    dept_stats = {}
    candidates = CandidateProfile.query.all()
    for c in candidates:
        dept = c.department or 'General'
        if dept not in dept_stats:
            dept_stats[dept] = {'total': 0, 'placed': 0}
        dept_stats[dept]['total'] += 1
        if 'Placed' in (c.placement_status or ''):
            dept_stats[dept]['placed'] += 1

    return {
        'total_students': total_students,
        'placed_students': placed_students,
        'unplaced_students': unplaced_students,
        'total_drives': len(drives),
        'total_companies': companies,
        'dept_stats': dept_stats
    }


def get_recruiter_metrics(recruiter_id):
    jobs = Job.query.filter_by(recruiter_id=recruiter_id).all() if recruiter_id else Job.query.all()
    job_ids = [j.id for j in jobs]
    
    total_apps = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0
    shortlisted = Application.query.filter(Application.job_id.in_(job_ids), Application.status == 'AI Shortlisted').count() if job_ids else 0
    selected = Application.query.filter(Application.job_id.in_(job_ids), Application.status.in_(['Selected', 'Offer Received', 'Offer Accepted'])).count() if job_ids else 0

    return {
        'total_jobs': len(jobs),
        'total_applicants': total_apps,
        'ai_shortlisted': shortlisted,
        'selected_candidates': selected
    }
