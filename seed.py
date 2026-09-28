import os
from datetime import datetime, timedelta
from app import create_app
from models import db
from models.user import User
from models.candidate import CandidateProfile
from models.recruiter import RecruiterProfile
from models.company import Company
from models.job import Job
from models.resume import Resume
from models.application import Application
from models.placement import PlacementDrive, PlacementRecord
from models.assessment import Assessment, Question, AssessmentAssignment
from models.interview import Interview, InterviewFeedback
from models.offer import Offer
from models.notification import Notification
from models.audit import AuditLog
from services.ai_matching import calculate_ai_match

def seed_database():
    app = create_app()
    with app.app_context():
        print("Resetting database schema...")
        db.drop_all()
        db.create_all()

        print("Seeding Companies...")
        c1 = Company(name="TechCorp Solutions", website="https://techcorp.example.com", industry="Software & Cloud", description="Leading enterprise software provider.", location="San Francisco, CA")
        c2 = Company(name="InnovateTech Inc", website="https://innovate.example.com", industry="AI & Analytics", description="Next-generation machine learning and data infrastructure.", location="Boston, MA")
        c3 = Company(name="CloudFlex Systems", website="https://cloudflex.example.com", industry="DevOps & AWS", description="Cloud architecture and microservice automation.", location="Seattle, WA")
        c4 = Company(name="DataDynamics", website="https://datadynamics.example.com", industry="Big Data & ML", description="Scalable data pipeline solutions.", location="Austin, TX")
        c5 = Company(name="CyberShield Security", website="https://cybershield.example.com", industry="Cybersecurity", description="Enterprise network security and compliance.", location="New York, NY")

        db.session.add_all([c1, c2, c3, c4, c5])
        db.session.commit()

        print("Seeding Demo Users across 7 User Roles...")
        # 1. Candidate
        u_cand1 = User(email="student@hiremind.edu", full_name="Alex Johnson", role="candidate")
        u_cand1.set_password("password123")

        u_cand2 = User(email="sarah.smith@hiremind.edu", full_name="Sarah Smith", role="candidate")
        u_cand2.set_password("password123")

        u_cand3 = User(email="david.lee@hiremind.edu", full_name="David Lee", role="candidate")
        u_cand3.set_password("password123")

        u_cand4 = User(email="priya.sharma@hiremind.edu", full_name="Priya Sharma", role="candidate")
        u_cand4.set_password("password123")

        u_cand5 = User(email="michael.brown@hiremind.edu", full_name="Michael Brown", role="candidate")
        u_cand5.set_password("password123")

        # 2. Recruiter
        u_rec = User(email="recruiter@techcorp.com", full_name="Rachel Green", role="recruiter")
        u_rec.set_password("password123")

        # 3. TPO Officer
        u_tpo = User(email="tpo@hiremind.edu", full_name="Dr. Robert Miller", role="tpo")
        u_tpo.set_password("password123")

        # 4. Interviewer
        u_int = User(email="interviewer@techcorp.com", full_name="James Wilson", role="interviewer")
        u_int.set_password("password123")

        # 5. Hiring Manager
        u_mgr = User(email="hiring@techcorp.com", full_name="Elena Rostova", role="hiring_manager")
        u_mgr.set_password("password123")

        # 6. Company Representative
        u_rep = User(email="rep@innovate.com", full_name="Marcus Vance", role="company_rep")
        u_rep.set_password("password123")

        # 7. Admin
        u_admin = User(email="admin@hiremind.edu", full_name="Administrator System", role="admin")
        u_admin.set_password("password123")

        db.session.add_all([u_cand1, u_cand2, u_cand3, u_cand4, u_cand5, u_rec, u_tpo, u_int, u_mgr, u_rep, u_admin])
        db.session.commit()

        print("Seeding Profiles...")
        cp1 = CandidateProfile(
            user_id=u_cand1.id, phone="+1 555-0192", department="Computer Science", cgpa=8.8,
            graduation_year=2026, backlogs=0, bio="Passionate full-stack developer with experience in Python, SQL, and React.",
            location="San Francisco, CA", qualification="B.Tech", experience_years=1.0,
            skills="Python, SQL, HTML, CSS, JavaScript, Flask, React, Git, Data Structures",
            certifications="AWS Cloud Practitioner, Scikit-learn Machine Learning"
        )
        cp2 = CandidateProfile(
            user_id=u_cand2.id, phone="+1 555-0193", department="Information Technology", cgpa=7.9,
            graduation_year=2026, backlogs=0, bio="Backend software enthusiast.",
            location="Boston, MA", qualification="B.Tech", experience_years=0.5,
            skills="Java, Spring Boot, SQL, MySQL, Git, REST API",
            certifications="Oracle Certified Java Programmer"
        )
        cp3 = CandidateProfile(
            user_id=u_cand3.id, phone="+1 555-0194", department="Electronics", cgpa=8.2,
            graduation_year=2026, backlogs=0, bio="Data science and NLP enthusiast.",
            location="Austin, TX", qualification="B.Tech", experience_years=0.0,
            skills="Python, Data Science, Machine Learning, TensorFlow, Pandas, NumPy, SQL",
            certifications="Deep Learning Specialization"
        )
        cp4 = CandidateProfile(
            user_id=u_cand4.id, phone="+1 555-0195", department="Computer Science", cgpa=9.1,
            graduation_year=2026, backlogs=0, bio="Competitive programmer and full stack AI engineer.",
            location="Seattle, WA", qualification="B.Tech", experience_years=1.5,
            skills="Python, C++, Java, SQL, Flask, Django, Machine Learning, NLP, Docker, AWS",
            certifications="AWS Solutions Architect"
        )
        cp5 = CandidateProfile(
            user_id=u_cand5.id, phone="+1 555-0196", department="Mechanical", cgpa=6.8,
            graduation_year=2026, backlogs=1, bio="Mechanical engineer expanding into Python scripting.",
            location="Chicago, IL", qualification="B.Tech", experience_years=0.0,
            skills="Python, C, HTML, CSS, CAD",
            certifications="AutoCAD Certified"
        )

        rp1 = RecruiterProfile(user_id=u_rec.id, company_id=c1.id, designation="Senior Talent Acquisition Lead", phone="+1 555-9001")
        rp2 = RecruiterProfile(user_id=u_rep.id, company_id=c2.id, designation="VP of University Recruiting", phone="+1 555-9002")

        db.session.add_all([cp1, cp2, cp3, cp4, cp5, rp1, rp2])
        db.session.commit()

        print("Seeding Sample Resumes...")
        res1 = Resume(
            candidate_id=cp1.id, filename="Alex_Johnson_Resume.pdf", filepath="uploads/resumes/demo_alex.pdf",
            extracted_text="Alex Johnson - Computer Science Student. Skills: Python, SQL, Flask, HTML, CSS, JavaScript, React, Data Structures. Experience: Built AI recruitment system.",
            extracted_education="B.Tech (Computer Science)", extracted_experience="1 years"
        )
        res1.set_parsed_skills(['Python', 'SQL', 'Flask', 'HTML', 'CSS', 'JavaScript', 'React', 'Data Structures'])

        res4 = Resume(
            candidate_id=cp4.id, filename="Priya_Sharma_Resume.pdf", filepath="uploads/resumes/demo_priya.pdf",
            extracted_text="Priya Sharma - Senior Computer Science Scholar. Skills: Python, C++, Java, SQL, Flask, Django, Machine Learning, NLP, Docker, AWS.",
            extracted_education="B.Tech (Computer Science)", extracted_experience="1.5 years"
        )
        res4.set_parsed_skills(['Python', 'C++', 'Java', 'SQL', 'Flask', 'Django', 'Machine Learning', 'NLP', 'Docker', 'AWS'])

        db.session.add_all([res1, res4])
        db.session.commit()

        print("Seeding Jobs (8 Jobs)...")
        j1 = Job(company_id=c1.id, recruiter_id=rp1.id, title="Software Engineer - Full Stack", description="Build high performance scalable web applications with Flask, Python, and modern JavaScript.", required_skills="Python, SQL, Flask, HTML, CSS, JavaScript", min_qualification="B.Tech", min_experience=0.0, salary_package="10-14 LPA", location="San Francisco, CA", deadline=datetime.utcnow() + timedelta(days=30), status="Open", job_type="Full-Time")
        j2 = Job(company_id=c1.id, recruiter_id=rp1.id, title="AI & NLP Machine Learning Engineer", description="Design machine learning models, TF-IDF vectorization pipelines, and natural language processing solutions.", required_skills="Python, Machine Learning, NLP, Scikit-Learn, Pandas, NumPy, SQL", min_qualification="B.Tech", min_experience=0.0, salary_package="14-18 LPA", location="San Francisco, CA", deadline=datetime.utcnow() + timedelta(days=25), status="Open", job_type="Full-Time")
        j3 = Job(company_id=c2.id, recruiter_id=rp2.id, title="Backend Java Developer", description="Develop microservices in Java Spring Boot and PostgreSQL.", required_skills="Java, Spring Boot, SQL, PostgreSQL, REST API, Git", min_qualification="B.Tech", min_experience=0.0, salary_package="9-12 LPA", location="Boston, MA", deadline=datetime.utcnow() + timedelta(days=20), status="Open", job_type="Full-Time")
        j4 = Job(company_id=c2.id, recruiter_id=rp2.id, title="Campus Placement Graduate Trainee", description="Special hiring drive for final year B.Tech computer science and IT students.", required_skills="Python, Java, SQL, Data Structures", min_qualification="B.Tech", min_experience=0.0, salary_package="8 LPA", location="Boston, MA", deadline=datetime.utcnow() + timedelta(days=15), status="Open", job_type="Placement Drive")
        j5 = Job(company_id=c3.id, recruiter_id=rp1.id, title="Cloud DevOps Engineer", description="Manage AWS cloud architecture, Docker containers, and CI/CD pipelines.", required_skills="AWS, Docker, Linux, CI/CD, Git, Python", min_qualification="B.Tech", min_experience=1.0, salary_package="12-16 LPA", location="Seattle, WA", deadline=datetime.utcnow() + timedelta(days=40), status="Open", job_type="Full-Time")
        j6 = Job(company_id=c4.id, recruiter_id=rp2.id, title="Data Analyst & SQL Specialist", description="Create interactive business dashboards using SQL, Tableau, and Python.", required_skills="SQL, Python, Tableau, Power BI, Excel", min_qualification="B.Tech", min_experience=0.0, salary_package="7-9 LPA", location="Austin, TX", deadline=datetime.utcnow() + timedelta(days=10), status="Open", job_type="Full-Time")
        j7 = Job(company_id=c5.id, recruiter_id=rp1.id, title="Cyber Security Associate", description="Analyze network security logs and vulnerability assessments.", required_skills="Linux, Security, Python, Networking", min_qualification="B.Tech", min_experience=0.0, salary_package="10 LPA", location="New York, NY", deadline=datetime.utcnow() + timedelta(days=12), status="Open", job_type="Full-Time")
        j8 = Job(company_id=c1.id, recruiter_id=rp1.id, title="Python Full-Stack Intern", description="Summer engineering internship for computer science undergraduates.", required_skills="Python, HTML, CSS, JavaScript, Git", min_qualification="B.Tech", min_experience=0.0, salary_package="30,000/mo Stipend", location="Remote", deadline=datetime.utcnow() + timedelta(days=45), status="Open", job_type="Internship")

        db.session.add_all([j1, j2, j3, j4, j5, j6, j7, j8])
        db.session.commit()

        print("Seeding Placement Drives (3 Drives)...")
        pd1 = PlacementDrive(company_id=c1.id, job_id=j1.id, title="TechCorp Annual Campus Hiring Drive 2026", drive_date=datetime.utcnow() + timedelta(days=10), venue="Main Campus Auditorium", min_cgpa=6.5, eligible_branches="Computer Science, Information Technology, Electronics", max_backlogs=0, graduation_year=2026, status="Active")
        pd2 = PlacementDrive(company_id=c2.id, job_id=j3.id, title="InnovateTech Mega Placement Drive", drive_date=datetime.utcnow() + timedelta(days=18), venue="Online Examination Hall A", min_cgpa=7.0, eligible_branches="Computer Science, Information Technology", max_backlogs=0, graduation_year=2026, status="Active")
        pd3 = PlacementDrive(company_id=c3.id, job_id=j5.id, title="CloudFlex Cloud & DevOps Drive", drive_date=datetime.utcnow() + timedelta(days=25), venue="Seminar Hall 2", min_cgpa=7.5, eligible_branches="Computer Science, Information Technology", max_backlogs=0, graduation_year=2026, status="Upcoming")

        db.session.add_all([pd1, pd2, pd3])
        db.session.commit()

        print("Seeding Candidate Applications with AI Match Engine...")
        app1_match = calculate_ai_match(cp1, j1, res1)
        app1 = Application(candidate_id=cp1.id, job_id=j1.id, status="AI Shortlisted", ai_score=app1_match['overall_score'])
        app1.set_ai_details_dict(app1_match)

        app2_match = calculate_ai_match(cp4, j2, res4)
        app2 = Application(candidate_id=cp4.id, job_id=j2.id, status="Interview", ai_score=app2_match['overall_score'])
        app2.set_ai_details_dict(app2_match)

        app3_match = calculate_ai_match(cp2, j3, None)
        app3 = Application(candidate_id=cp2.id, job_id=j3.id, status="Assessment", ai_score=app3_match['overall_score'])
        app3.set_ai_details_dict(app3_match)

        app4_match = calculate_ai_match(cp3, j6, None)
        app4 = Application(candidate_id=cp3.id, job_id=j6.id, status="Applied", ai_score=app4_match['overall_score'])
        app4.set_ai_details_dict(app4_match)

        db.session.add_all([app1, app2, app3, app4])
        db.session.commit()

        print("Seeding Skill Assessments & MCQ Questions...")
        ass1 = Assessment(title="Python & Web Frameworks Quiz", description="Core Python data structures, Flask routing, and SQL queries.", category="Technical", duration_minutes=30, pass_marks=60, total_marks=30, created_by_id=u_rec.id)
        db.session.add(ass1)
        db.session.flush()

        q1 = Question(assessment_id=ass1.id, text="Which of the following data structures in Python is immutable?", option_a="List", option_b="Dictionary", option_c="Tuple", option_d="Set", correct_option="C", marks=10)
        q2 = Question(assessment_id=ass1.id, text="What SQL keyword is used to retrieve unique distinct rows from a database table?", option_a="UNIQUE", option_b="DISTINCT", option_c="DIFFERENT", option_d="GROUP BY", correct_option="B", marks=10)
        q3 = Question(assessment_id=ass1.id, text="In Flask, which decorator is used to bind a Python function to a URL route?", option_a="@app.route()", option_b="@app.bind()", option_c="@app.url()", option_d="@app.path()", correct_option="A", marks=10)
        db.session.add_all([q1, q2, q3])

        assign1 = AssessmentAssignment(assessment_id=ass1.id, candidate_id=cp1.id, application_id=app1.id, status="Completed", score=90, passed=True, completed_at=datetime.utcnow() - timedelta(days=1))
        db.session.add(assign1)
        db.session.commit()

        print("Seeding Scheduled Interviews & Feedback...")
        int1 = Interview(application_id=app2.id, candidate_id=cp4.id, interviewer_id=u_int.id, title="Technical Deep Dive & NLP Architecture", interview_type="Technical", scheduled_time=datetime.utcnow() + timedelta(days=2, hours=3), duration_minutes=45, location_or_link="https://meet.hiremind.edu/room-tech-ai", instructions="Be prepared to whiteboard TF-IDF algorithms and Flask API design.", status="Scheduled")
        db.session.add(int1)
        db.session.commit()

        print("Seeding Digital Job Offers...")
        off1 = Offer(application_id=app1.id, candidate_id=cp1.id, company_id=c1.id, job_title=j1.title, salary_package="12 LPA", joining_date=datetime.utcnow() + timedelta(days=60), deadline=datetime.utcnow() + timedelta(days=15), offer_letter_text="We are thrilled to offer you the Full Stack Software Engineer role at TechCorp Solutions!", status="Sent")
        db.session.add(off1)
        db.session.commit()

        print("Seeding Notifications...")
        n1 = Notification(user_id=u_cand1.id, title="Welcome to HireMind", message="Your student account has been activated. Upload your resume to enable AI matching.", is_read=True)
        n2 = Notification(user_id=u_cand1.id, title="Official Job Offer Received", message="You have received a digital offer letter for 'Software Engineer - Full Stack' at TechCorp Solutions!", is_read=False)
        db.session.add_all([n1, n2])

        print("Seeding Audit Log...")
        al1 = AuditLog(user_id=u_admin.id, action="System Seeded", target="Database", details="Initial seed data loaded for demo testing.")
        db.session.add(al1)

        db.session.commit()

        print("\n" + "="*70)
        print(" SUCCESS: Database successfully populated with sample demo data!")
        print("="*70)
        print("\nDEMO LOGIN CREDENTIALS (Password for ALL accounts: password123):")
        print("  1. Candidate/Student:     student@hiremind.edu")
        print("  2. Recruiter/HR:          recruiter@techcorp.com")
        print("  3. Placement Officer/TPO: tpo@hiremind.edu")
        print("  4. Interviewer:           interviewer@techcorp.com")
        print("  5. Hiring Manager:        hiring@techcorp.com")
        print("  6. Company Rep:           rep@innovate.com")
        print("  7. System Administrator:  admin@hiremind.edu")
        print("="*70 + "\n")

if __name__ == '__main__':
    seed_database()
