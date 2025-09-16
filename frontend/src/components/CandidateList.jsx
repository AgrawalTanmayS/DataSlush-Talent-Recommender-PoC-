import React from 'react';
import '../styles.css'; // import the CSS

function CandidateList({ candidates }) {
  return (
    <div>
      {candidates.map((c, idx) => (
        <div className="candidate-card" key={idx}>
          <div className="candidate-name">{c.name}</div>
          <div className="candidate-info">
            Skills: {c.skills ? c.skills.split(',').map(s => s.trim()).join(', ') : 'N/A'}
          </div>
          <div className="candidate-info">
            Location: {c.location || 'N/A'}
          </div>
          <div className="candidate-info">
            Match Score: {c.score ? c.score.toFixed(2) : 0}
          </div>
          <div className="candidate-info">
            Monthly Rate: {c.monthly_rate || 0} | Hourly Rate: {c.hourly_rate || 0}
          </div>
        </div>
      ))}
    </div>
  );
}

export default CandidateList;
