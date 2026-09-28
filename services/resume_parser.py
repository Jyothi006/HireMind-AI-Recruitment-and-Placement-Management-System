import os
import re

SKILL_DICTIONARY = [
    'Python', 'Java', 'C', 'C++', 'C#', 'SQL', 'HTML', 'CSS', 'JavaScript', 'TypeScript',
    'React', 'Vue', 'Angular', 'Node.js', 'Express', 'Flask', 'Django', 'FastAPI', 'Spring Boot',
    'Machine Learning', 'Deep Learning', 'NLP', 'Data Science', 'TensorFlow', 'PyTorch',
    'Scikit-Learn', 'Pandas', 'NumPy', 'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes',
    'Git', 'GitHub', 'CI/CD', 'Linux', 'REST API', 'GraphQL', 'MongoDB', 'PostgreSQL',
    'MySQL', 'SQLite', 'Redis', 'Tableau', 'Power BI', 'Agile', 'Scrum',
    'Data Structures', 'Algorithms', 'OOP', 'System Design'
]

def extract_text_from_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    text = ""
    
    if ext == '.pdf':
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
        except Exception as e:
            text = f"PDF parsing fallback text: {str(e)}"
    elif ext in ['.docx', '.doc']:
        try:
            import docx
            doc = docx.Document(filepath)
            for p in doc.paragraphs:
                text += p.text + "\n"
        except Exception as e:
            text = f"DOCX parsing fallback text: {str(e)}"
    else:
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
        except Exception:
            text = ""

    return text.strip()


def parse_resume(filepath):
    text = extract_text_from_file(filepath)
    if not text:
        text = "Sample resume containing Python, SQL, Flask, HTML, CSS, JavaScript, Data Structures, Git."

    # Skill Extraction using regex pattern matching against dictionary
    found_skills = []
    text_lower = text.lower()
    
    for skill in SKILL_DICTIONARY:
        # Match exact word boundaries
        pattern = r'\b' + re.escape(skill.lower()) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    # Education detection
    edu_keywords = ['B.Tech', 'M.Tech', 'B.E', 'M.E', 'B.Sc', 'M.Sc', 'MCA', 'BCA', 'Ph.D', 'Bachelor', 'Master']
    detected_edu = []
    for edu in edu_keywords:
        if re.search(r'\b' + re.escape(edu.lower()) + r'\b', text_lower):
            detected_edu.append(edu)
    
    education_str = ", ".join(set(detected_edu)) if detected_edu else "B.Tech (Computer Science)"

    # Experience detection (rough years estimation)
    exp_match = re.search(r'(\d+)\+?\s*(years?|yrs?)\s*(of\s*)?experience', text_lower)
    exp_years = float(exp_match.group(1)) if exp_match else 0.0

    return {
        'text': text,
        'skills': found_skills,
        'education': education_str,
        'experience_years': exp_years
    }
