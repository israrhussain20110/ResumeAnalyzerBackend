import torch
from transformers import pipeline
from sklearn.metrics.pairwise import cosine_similarity

# Load BERT model once
nlp = pipeline('feature-extraction', model='distilbert-base-uncased', framework='pt')

def calculate_similarity(text1, text2):
    if not text1.strip() or not text2.strip():
        return 0.0

    vec1 = nlp(text1)
    vec2 = nlp(text2)
    vec1_mean = torch.mean(torch.tensor(vec1), dim=1)
    vec2_mean = torch.mean(torch.tensor(vec2), dim=1)
    similarity = cosine_similarity(vec1_mean, vec2_mean)[0][0]
    return similarity

def check_resume_structure(resume_text):
    sections = {
        'Contact Information': False,
        'Summary or Objective': False,
        'Skills': False,
        'Experience': False,
        'Education': False,
        'Certifications': False,
        'Projects': False
    }

    keywords = {
        'Contact Information': ['contact', 'email', 'phone', 'address'],
        'Summary or Objective': ['summary', 'objective', 'overview', 'profile'],
        'Skills': ['skill', 'competency', 'proficiency'],
        'Experience': ['experience', 'work history', 'employment'],
        'Education': ['education', 'academic background', 'qualification'],
        'Certifications': ['certification', 'certificate'],
        'Projects': ['project', 'portfolio']
    }

    for line in resume_text.split('\n'):
        for section, terms in keywords.items():
            if any(term in line.lower() for term in terms):
                sections[section] = True

    structure_score = sum(sections.values()) / len(sections) * 100
    return structure_score, sections

def score_resume(resume_data, job_description_data):
    resume_entities = set(resume_data['entities'])
    job_entities = set(job_description_data['keywords'])

    entity_score = len(resume_entities & job_entities) / len(job_entities) * 100 if job_entities else 0
    skills_score = calculate_similarity(resume_data['skills'], job_description_data['skills']) * 100
    experience_score = calculate_similarity(resume_data['experience'], job_description_data['experience']) * 100
    education_score = calculate_similarity(resume_data['education'], job_description_data['education']) * 100
    structure_score, sections = check_resume_structure(resume_data['full_text'])

    total_score = (
        0.3 * entity_score +
        0.3 * skills_score +
        0.2 * experience_score +
        0.2 * education_score +
        0.1 * structure_score
    )

    return {
        'total_score': round(total_score, 2),
        'entity_score': round(entity_score, 2),
        'skills_score': round(skills_score, 2),
        'experience_score': round(experience_score, 2),
        'education_score': round(education_score, 2),
        'structure_score': round(structure_score, 2),
        'sections': sections
    }

def generate_feedback(resume_data, job_description_data):
    feedback = []
    job_keywords = job_description_data['keywords']
    resume_skills = set(resume_data['skills'].split())
    resume_experience = set(resume_data['experience'].split())
    resume_education = set(resume_data['education'].split())

    missing_skills = job_keywords - resume_skills
    missing_experience = job_keywords - resume_experience
    missing_education = job_keywords - resume_education

    if missing_skills:
        feedback.append(
            f"Your skills section could be improved. Consider including skills such as: {', '.join(list(missing_skills)[:10])}."
        )
    if missing_experience:
        feedback.append(
            f"Your experience section could be improved. Consider including experiences such as: {', '.join(list(missing_experience)[:10])}."
        )
    if missing_education:
        feedback.append(
            f"Your education section could be improved. Ensure it highlights education such as: {', '.join(list(missing_education)[:10])}."
        )

    structure_score, sections = check_resume_structure(resume_data['full_text'])
    missing_sections = [sec for sec, present in sections.items() if not present]
    if missing_sections:
        feedback.append(
            f"Your resume is missing the following sections: {', '.join(missing_sections)}."
        )

    return ' '.join(feedback[:3])
