# HireMind – AI Recruitment & Placement Management System

HireMind is an AI-powered recruitment and campus placement management platform built to bridge candidates, recruiters, interviewers, hiring managers, placement officers (TPOs), corporate representatives, and system administrators through an end-to-end recruitment lifecycle.

---

## 🚀 Key Features & Modules

1. **Candidate Management**: Registration, profile building, skill inventory, PDF/DOCX resume upload, application tracking, assessment completion, and digital offer management.
2. **Job Management**: CRUD job postings, set required skills, minimum qualifications, minimum experience, salary packages, application deadlines, and view applicant pipelines.
3. **Campus Placement Management (TPO)**: Student batch database, corporate company directory, placement drive scheduling, multi-factor eligibility engine (CGPA, backlogs, branch, graduation year), hall ticket generation, placement reports, and **One-Student-One-Job policy** enforcement.
4. **AI Recruitment & Candidate Matching Engine**:
   - **Resume Text Parsing**: Extracts text from PDF, DOCX, and TXT resumes.
   - **Skill Extraction**: Identifies technical skills against a 50+ item dictionary using regex boundary matching.
   - **Candidate-Job Matching Score (0–100%)**: Calculates similarity using `scikit-learn` **TF-IDF Vectorization + Cosine Similarity**, combined with direct skill overlap ratio, qualification alignment, and experience thresholding.
   - **Candidate Ranking**: Ranks applicants automatically for recruiters with explicit explainability breakdowns (Matched skills, Missing skills, Qualification/Experience match, and AI recommendation statement).
5. **Skill Assessment Management**: Create aptitude, technical, and programming quizzes with MCQ options, assigned to candidates with automatic scoring and pass/fail determination.
6. **Interview Management**: Schedule technical, HR, managerial, and campus interviews with assigned interviewers, meeting links, instructions, and structured evaluation feedback forms.
7. **Selection & Offer Management**: Selection stage authorization, digital offer letter generation, joining date configuration, candidate acceptance/rejection, and automated placement status updates.
8. **Reports & Analytics**: Live database-driven Chart.js visual dashboards tailored for Admin, Recruiter, TPO, and Candidate roles.
9. **Notification Management**: In-app event notifications with unread badge indicators and direct links to actionable events.
10. **Admin & Security**: Password hashing with `Werkzeug`, session authentication via `Flask-Login`, role-based authorization, protected routes, user management, and real-time audit logging.

---

## 🛠️ Technology Stack

- **Backend**: Python 3.12, Flask 3.0
- **Database**: SQLite, SQLAlchemy ORM, Flask-SQLAlchemy
- **Authentication**: Flask-Login, Werkzeug Security
- **AI / NLP**: `scikit-learn` (TF-IDF Vectorizer + Cosine Similarity), `PyPDF2`, `python-docx`, `regex`
- **Frontend**: HTML5, CSS3 (Vanilla + Custom Glassmorphism Theme), Bootstrap 5.3, Bootstrap Icons, Chart.js 4.x

---

## 🔑 Demo Credentials

All demo accounts share the password: `password123`

| Role | Email | Password | Description |
| --- | --- | --- | --- |
| **Candidate / Student** | `student@hiremind.edu` | `password123` | Computer Science student profile with resume |
| **Recruiter / HR** | `recruiter@techcorp.com` | `password123` | HR recruiter at TechCorp Solutions |
| **Placement Officer (TPO)** | `tpo@hiremind.edu` | `password123` | Campus Placement Cell Administrator |
| **Interviewer** | `interviewer@techcorp.com` | `password123` | Technical interviewer |
| **Hiring Manager** | `hiring@techcorp.com` | `password123` | Executive hiring approval manager |
| **Company Representative** | `rep@innovate.com` | `password123` | Representative at InnovateTech Inc |
| **System Administrator** | `admin@hiremind.edu` | `password123` | Full system oversight and audit logs |

---

## ⚙️ Installation & Running on Windows

### 1. Prerequisites
Ensure Python 3.10+ is installed on Windows.

### 2. Setup Virtual Environment & Dependencies
Open PowerShell or Command Prompt in the `HireMind` folder:

```cmd
cd c:\Users\jyoth\Downloads\HireMind
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Database Seeding & Initialization
Run the database seed script to populate sample candidates, companies, jobs, placement drives, applications, assessments, interviews, and offers:

```cmd
python seed.py
```

### 4. Run the Flask Web Application

```cmd
python app.py
```

Open your browser and navigate to:
`http://127.0.0.1:5000`

---

## 📁 Project Structure

```text
HireMind/
├── app.py                     # Main Flask Application Entrypoint
├── config.py                  # Environment & App Configuration
├── seed.py                    # Database Seeder Script
├── requirements.txt           # Python Package Dependencies
├── README.md                  # System Documentation
├── .env.example               # Environment Variables Template
├── models/                    # SQLAlchemy Database Models
│   ├── __init__.py
│   ├── user.py
│   ├── candidate.py
│   ├── recruiter.py
│   ├── company.py
│   ├── job.py
│   ├── resume.py
│   ├── application.py
│   ├── placement.py
│   ├── assessment.py
│   ├── interview.py
│   ├── offer.py
│   ├── notification.py
│   └── audit.py
├── routes/                    # Modular Flask Blueprints
│   ├── auth.py
│   ├── candidate.py
│   ├── recruiter.py
│   ├── placement.py
│   ├── assessment.py
│   ├── interview.py
│   ├── hiring.py
│   └── admin.py
├── services/                  # Business Logic & AI Services
│   ├── resume_parser.py
│   ├── ai_matching.py
│   ├── notification_service.py
│   └── report_service.py
├── static/                    # Static CSS & JS Assets
│   ├── css/style.css
│   └── js/main.js
├── templates/                 # Jinja2 HTML Templates
│   ├── base.html
│   ├── index.html
│   ├── auth/
│   ├── candidate/
│   ├── recruiter/
│   ├── placement/
│   ├── assessment/
│   ├── interviewer/
│   ├── hiring_manager/
│   └── admin/
├── uploads/
│   └── resumes/               # Resume Upload Storage
└── instance/
    └── hiremind.db            # SQLite Database
```

---

## 🧠 AI Matching Engine Logic

The candidate matching engine does not use hardcoded or fake percentages. It executes a 4-part evaluation algorithm:
1. **Skill Overlap Analysis (45% weight)**: Compares the extracted candidate skills (from resume parsing + candidate profile) against the job's required skill set.
2. **TF-IDF Cosine Similarity (35% weight)**: Converts candidate biography, department, skills, and resume text alongside the job title, requirements, and description into TF-IDF term vectors, calculating exact cosine similarity ($\cos(\theta)$).
3. **Qualification Verification (10% weight)**: Checks minimum degree requirement (B.Tech, B.E, MCA, M.Tech).
4. **Experience Verification (10% weight)**: Verifies candidate experience against minimum required years.

Result outputs a transparent 0-100% score accompanied by explicit explainability pills:
- **Matched Skills**: e.g., `✓ Python`, `✓ SQL`, `✓ Flask`
- **Missing Skills**: e.g., `• Machine Learning`
- **AI Recommendation**: Plain language alignment summary.

---

## 🔮 Future Enhancements

- Integration with Video Interview APIs (WebRTC / Zoom SDK).
- Automated SMS/Email gateway support for notifications.
- Advanced NLP BERT-based semantic resume embeddings.
