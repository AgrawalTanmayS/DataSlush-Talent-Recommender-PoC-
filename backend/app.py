# app.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from recommender import load_model, compute_embeddings, rank_candidates
from utils import load_candidates, parse_job_postings
import os
import pandas as pd

app = FastAPI()

# CORS - allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """
    Load model and candidate data when the backend starts.
    """
    global MODEL, CANDIDATES_DF, CAND_EMBS
    MODEL = load_model()
    base = os.path.dirname(__file__)
    csv_path = os.path.join(base, "data", "talent_profiles.csv")

    # Load candidates + pre-compute embeddings
    CANDIDATES_DF = load_candidates(csv_path)
    CAND_EMBS = compute_embeddings(CANDIDATES_DF, MODEL)

@app.get("/job_posts")
async def get_posts():
    """
    Return available job posts.
    """
    posts = parse_job_postings()
    return posts

@app.get("/recommend/{post_id}")
async def recommend(post_id: str):
    """
    Recommend top candidates for a given job post
    """
    posts = parse_job_postings()

    # Look up job post by ID
    post = next((p for p in posts if p["id"] == post_id), None)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Rank candidates
    top10 = rank_candidates(post, CANDIDATES_DF, CAND_EMBS, MODEL)

    # Ensure all expected columns exist
    expected_cols = ["name", "location", "bio", "skills", "monthly_rate", "hourly_rate", "view_count", "score"]
    for col in expected_cols:
        if col not in top10.columns:
            top10[col] = None

    return top10[expected_cols].to_dict(orient="records")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
