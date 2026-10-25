from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re

def calculate_ai_match(candidate_profile, job, resume=None):
    """
    Computes real AI match score between candidate and job requirements using TF-IDF + Cosine Similarity
    and direct skill set analysis.
    Returns: dict with overall_score, matched_skills, missing_skills, qual_match, exp_match, recommendation
    """
    # 1. Gather Candidate Skills
    candidate_skills = set()
    if candidate_profile and candidate_profile.skills:
        for s in candidate_profile.skills.split(','):
            if s.strip():
                candidate_skills.add(s.strip().lower())
                
    if resume:
        parsed_skills = resume.get_parsed_skills()
        for s in parsed_skills:
            candidate_skills.add(s.lower())

    # 2. Gather Job Skills
    job_skills_raw = [s.strip() for s in job.required_skills.split(',') if s.strip()]
    job_skills = set(s.lower() for s in job_skills_raw)

    # 3. Direct Skill Overlap Analysis
    matched_skills = []
    missing_skills = []
    
    for js in job_skills_raw:
        if js.lower() in candidate_skills:
            matched_skills.append(js)
        else:
            missing_skills.append(js)

    skill_overlap_ratio = len(matched_skills) / len(job_skills_raw) if job_skills_raw else 1.0

    # 4. TF-IDF Vectorization + Cosine Similarity
    candidate_text_corpus = " ".join(candidate_skills) + " "
    if candidate_profile and candidate_profile.bio:
        candidate_text_corpus += candidate_profile.bio + " "
    if candidate_profile and candidate_profile.department:
        candidate_text_corpus += candidate_profile.department + " "
    if resume and resume.extracted_text:
        candidate_text_corpus += resume.extracted_text[:1000] # limit length for clean vectorization

    job_text_corpus = job.title + " " + job.required_skills + " " + job.description

    try:
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform([candidate_text_corpus, job_text_corpus])
        cosine_sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except Exception:
        cosine_sim = skill_overlap_ratio

    # 5. Qualification Match
    qual_match = True
    if job.min_qualification and candidate_profile:
        # Simple qualification keyword check
        req_q = job.min_qualification.lower()
        cand_q = (candidate_profile.qualification or "").lower()
        if req_q not in cand_q and cand_q not in req_q:
            # Check for B.Tech vs B.E equivalence
            if 'b.tech' in req_q or 'b.e' in req_q:
                qual_match = any(k in cand_q for k in ['b.tech', 'b.e', 'bca', 'm.tech', 'mca'])
            else:
                qual_match = False

    # 6. Experience Match
    cand_exp = candidate_profile.experience_years if candidate_profile else 0.0
    exp_match = cand_exp >= job.min_experience

    # 7. Weighted Score Calculation
    # Weights: Skill Overlap 45%, TF-IDF Cosine Similarity 35%, Qualification Match 10%, Experience Match 10%
    score = (
        (skill_overlap_ratio * 45.0) +
        (cosine_sim * 35.0) +
        (10.0 if qual_match else 0.0) +
        (10.0 if exp_match else 0.0)
    )

    final_score = round(min(max(score, 10.0), 99.0), 1)

    # Recommendation synthesis
    if final_score >= 80:
        recommendation = "High Alignment: Candidate meets primary technical requirements and skill stack."
    elif final_score >= 60:
        recommendation = "Moderate Alignment: Candidate possesses core requirements with minor skill gaps."
    else:
        recommendation = "Low Alignment: Significant skill gaps identified relative to job description."

    return {
        'overall_score': final_score,
        'matched_skills': matched_skills,
        'missing_skills': missing_skills,
        'qualification_match': qual_match,
        'experience_match': exp_match,
        'recommendation': recommendation,
        'cosine_similarity': round(float(cosine_sim), 2)
    }
