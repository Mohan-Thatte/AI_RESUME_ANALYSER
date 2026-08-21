import { useState } from 'react'
import ResultsDashboard from './components/ResultsDashboard'

function App() {
  const [file, setFile] = useState(null)
  const [jobDescription, setJobDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
    }
  }

  const handleAnalyze = async () => {
    if (!file || !jobDescription) {
      setError("Please provide both a resume (PDF) and a job description.")
      return
    }

    setError('')
    setLoading(true)
    setResult(null)

    const formData = new FormData()
    formData.append('resume', file)
    formData.append('job_description', jobDescription)

    try {
      const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
      const response = await fetch(`${API_URL}/api/match`, {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        let detail = 'Failed to analyze the resume. Make sure the backend is running.'
        try {
          const errBody = await response.json()
          if (errBody && errBody.detail) detail = errBody.detail
        } catch (_) {
          // response body wasn't JSON; keep the generic message
        }
        throw new Error(detail)
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="app-container">
      <h1>ResumeMatch AI</h1>

      {!result ? (
        <div className="glass-panel">
          <div className="grid-layout">
            <div className="input-group">
              <label>Upload Resume (PDF)</label>
              <div className="file-upload">
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                />
                <p>
                  {file ? file.name : "Drag & Drop or Click to Browse"}
                </p>
              </div>
            </div>

            <div className="input-group">
              <label>Job Description</label>
              <textarea
                placeholder="Paste the target job description here..."
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
            </div>
          </div>

          {error && <p style={{ color: 'var(--danger-color)', textAlign: 'center', marginBottom: '1rem' }}>{error}</p>}

          <button
            className="btn-primary"
            onClick={handleAnalyze}
            disabled={loading}
          >
            {loading ? "Analyzing with AI..." : "Analyze Match"}
          </button>
        </div>
      ) : (
        <div className="glass-panel results-dashboard">
          <button
            className="btn-primary"
            style={{ marginBottom: '2rem', width: 'auto' }}
            onClick={() => setResult(null)}
          >
            ← New Analysis
          </button>
          <ResultsDashboard result={result} />
        </div>
      )}
    </div>
  )
}

export default App
