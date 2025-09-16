import React, { useEffect, useState } from 'react';
import CandidateList from './components/CandidateList';
import './styles.css'; // import the CSS file

function App() {
  const [posts, setPosts] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [selected, setSelected] = useState(null);

  const BASE_URL = 'http://127.0.0.1:8000'; // Backend URL

  useEffect(() => {
    fetch(`${BASE_URL}/job_posts`)
      .then((res) => res.json())
      .then(setPosts)
      .catch(err => console.error("Error fetching job posts:", err));
  }, []);

  const loadRecs = (postId) => {
    setSelected(postId);
    fetch(`${BASE_URL}/recommend/${postId}`)
      .then((res) => res.json())
      .then(setCandidates)
      .catch(err => console.error("Error fetching recommendations:", err));
  };

  return (
    <div className="app-container">
      <h2>DataSlush — Talent Recommender (PoC)</h2>
      <div className="panel-container">
        {/* Job Posts horizontal card row */}
        <div className="job-list-row">
          {posts.map((p) => (
            <div
              key={p.id}
              className={`card job-card${selected === p.id ? ' selected' : ''}`}
            >
              <div className="card-title">{p.title}</div>
              <div className="card-description">
                {p.description.slice(0, 120)}...
              </div>
              <button
                className="recommend-btn"
                onClick={() => loadRecs(p.id)}
              >
                Recommend Top 10
              </button>
            </div>
          ))}
        </div>
        {/* Candidates Panel */}
        <div className="candidates-panel">
          <h3>Top Candidates</h3>
          {candidates.length === 0 && (
            <div>Select a post and click Recommend</div>
          )}
          <CandidateList candidates={candidates} />
        </div>
      </div>
    </div>
  );
}

export default App;
