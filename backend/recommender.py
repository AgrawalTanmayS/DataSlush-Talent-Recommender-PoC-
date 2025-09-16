# recommender.py
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import re

MODEL = None

def load_model(model_name='all-MiniLM-L6-v2'):
    """Load sentence transformer model once and reuse"""
    global MODEL
    if MODEL is None:
        MODEL = SentenceTransformer(model_name)
    return MODEL


def text_for_embedding(row):
    """Combine candidate fields into a single text for embeddings"""
    parts = []
    for k in ['bio', 'skills', 'software', 'platforms', 'niches', 'worked_with']:
        if k in row and pd.notna(row[k]):
            parts.append(str(row[k]))
    return ' '.join(parts)


def compute_embeddings(df, model):
    texts = [text_for_embedding(r) for _, r in df.iterrows()]
    embeddings = model.encode(texts, show_progress_bar=True)
    return embeddings


def skill_overlap_score(required_skills, candidate_skills):
    if not required_skills:
        return 0.0
    req = set([s.strip().lower() for s in required_skills if s.strip()])
    cand = set([s.strip().lower() for s in candidate_skills if s.strip()])
    if len(req) == 0:
        return 0.0
    return len(req & cand) / len(req)


def location_score(job_pref_locations, candidate_location):
    if not job_pref_locations:
        return 1.0
    cand = candidate_location.lower() if pd.notna(candidate_location) else ''
    for i, loc in enumerate(job_pref_locations):
        if loc.lower() in cand:
            return 1.0 - (0.1 * i)
    return 0.5


def rate_score(job_budget, candidate_rate, job_type='monthly'):
    try:
        if pd.isna(candidate_rate) or candidate_rate == '':
            return 0.5
        cand = float(candidate_rate)
    except:
        return 0.5

    if isinstance(job_budget, (list, tuple)):
        low, high = job_budget[0], job_budget[1]
    else:
        low, high = job_budget, job_budget

    if low is None or high is None:
        return 0.5

    if cand >= low and cand <= high:
        return 1.0
    dist = min(abs(cand - low), abs(cand - high))
    score = 1 / (1 + np.log1p(1 + dist))
    return float(score)


def normalize(x):
    x = np.array(x, dtype=float)
    if np.max(x) - np.min(x) == 0:
        return np.zeros_like(x)
    return (x - np.min(x)) / (np.max(x) - np.min(x))


def rank_candidates(job_post, candidates_df, candidates_embeddings, model):
    """Rank candidates for a given job post"""

    # ensure job_post fields exist
    job_text = str(job_post.get('description', ''))
    required_skills = job_post.get('required_skills', [])
    if isinstance(required_skills, list):
        job_text += ' ' + ' '.join(required_skills)
    elif isinstance(required_skills, str):
        job_text += ' ' + required_skills

    job_emb = model.encode([job_text])[0]
    sims = cosine_similarity([job_emb], candidates_embeddings)[0]

    skill_scores, loc_scores, rate_scores, views, softskill = [], [], [], [], []

    for idx, row in candidates_df.iterrows():
        # candidate skills parsing
        cand_skills = []
        if pd.notna(row.get('skills')):
            cand_skills = [s.strip() for s in re.split('[,;|/]', str(row['skills'])) if s.strip()]

        skill_scores.append(skill_overlap_score(required_skills, cand_skills))
        loc_scores.append(location_score(job_post.get('locations', []), row.get('location', '')))

        if job_post.get('budget_type', 'monthly') == 'monthly':
            rate_scores.append(rate_score(job_post.get('budget'), row.get('monthly_rate')))
        else:
            rate_scores.append(rate_score(job_post.get('budget'), row.get('hourly_rate')))

        views.append(row.get('view_count', 0))

        bio = str(row.get('bio', '')).lower()
        soft = 1.0 if any(x in bio for x in ['passion', 'energetic', 'team', 'lead']) else 0.5
        softskill.append(soft)

    # normalize all feature scores
    sim_n = normalize(sims)
    skill_n = normalize(skill_scores)
    loc_n = normalize(loc_scores)
    rate_n = normalize(rate_scores)
    views_n = normalize(views)
    soft_n = normalize(softskill)

    # weights
    w_sim, w_skill, w_loc, w_rate, w_views, w_soft = 0.40, 0.25, 0.10, 0.10, 0.05, 0.10

    final_scores = (w_sim * sim_n + w_skill * skill_n + w_loc * loc_n +
                    w_rate * rate_n + w_views * views_n + w_soft * soft_n)
    final_scores = 100 * (final_scores - final_scores.min()) / (final_scores.max() - final_scores.min() + 1e-9)

    candidates_df = candidates_df.copy()
    candidates_df['score'] = final_scores
    candidates_df['semantic_sim'] = sims

    # ensure all expected columns exist
    expected_cols = ["name","location","bio","skills","monthly_rate","hourly_rate","view_count"]
    for col in expected_cols:
        if col not in candidates_df.columns:
            candidates_df[col] = None

    ranked = candidates_df.sort_values('score', ascending=False)
    top10 = ranked.head(10)

    return top10
