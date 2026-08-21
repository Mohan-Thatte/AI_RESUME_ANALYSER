import React from 'react'

const DECISION_CLASS = {
  'Strong Shortlist': 'success',
  'Consider': 'warning',
  'Not Recommended': 'danger',
}

const ResultsDashboard = ({ result }) => {
  const {
    score,
    skill_breakdown,
    evidence,
    partial_skills,
    missing_skills,
    improvement_path,
    recruiter_decision,
  } = result

  return (
    <div>
      <div className="score-container">
        <h2>Match Score</h2>
        <div className="score-circle" style={{ '--score': `${score}%` }}>
          <span>{score}%</span>
        </div>
        <p style={{ color: 'var(--text-secondary)' }}>
          {score >= 80 ? 'Excellent Match!' : score >= 60 ? 'Good Match' : 'Needs Improvement'}
        </p>
        {recruiter_decision && (
          <span className={`chip ${DECISION_CLASS[recruiter_decision] || 'warning'}`}>
            {recruiter_decision}
          </span>
        )}
      </div>

      {skill_breakdown && (
        <div style={{ marginBottom: '2rem' }}>
          <h3>Score Breakdown</h3>
          <div className="breakdown-grid">
            {Object.entries(skill_breakdown).map(([label, value]) => (
              <div className="breakdown-item" key={label}>
                <div className="breakdown-label">
                  <span style={{ textTransform: 'capitalize' }}>{label}</span>
                  <span>{value}%</span>
                </div>
                <div className="breakdown-bar">
                  <div className="breakdown-fill" style={{ width: `${value}%` }} />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="grid-layout">
        <div>
          <h3>Matched Skills ✅</h3>
          <div className="chips-container">
            {evidence && evidence.length > 0 ? (
              evidence.map((item, idx) => (
                <span key={idx} className="chip success" title={item.found_in}>
                  {item.skill}
                </span>
              ))
            ) : (
              <p>No matched skills found.</p>
            )}
          </div>
        </div>

        <div>
          <h3>Missing Skills ❌</h3>
          <div className="chips-container">
            {missing_skills && missing_skills.length > 0 ? (
              missing_skills.map((skill, idx) => (
                <span key={idx} className="chip danger">{skill}</span>
              ))
            ) : (
              <p>No major missing skills!</p>
            )}
          </div>
        </div>
      </div>

      {partial_skills && partial_skills.length > 0 && (
        <div style={{ marginTop: '2rem' }}>
          <h3>Partial Matches ⚠️</h3>
          <div className="chips-container">
            {partial_skills.map((item, idx) => (
              <span key={idx} className="chip warning" title={item.evidence}>
                {item.skill}
              </span>
            ))}
          </div>
        </div>
      )}

      <div style={{ marginTop: '2rem' }}>
        <h3>Actionable Recommendations 💡</h3>
        <div className="recommendations">
          <ul>
            {improvement_path && improvement_path.length > 0 ? (
              improvement_path.map((rec, idx) => <li key={idx}>{rec}</li>)
            ) : (
              <li>No further recommendations at this time.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  )
}

export default ResultsDashboard
