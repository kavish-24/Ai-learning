
import { useState } from "react";
import "./App.css";

function App() {
  const [resume, setResume] = useState(null);
  const [jobDescription, setJobDescription] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();

    if (!resume || !jobDescription.trim()) {
      setError("Upload a resume and enter a job description.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    const formData = new FormData();
    formData.append("resume", resume);
    formData.append("job_description", jobDescription);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/score-resume",
        {
          method: "POST",
          body: formData
        }
      );

      if (!response.ok) {
        throw new Error("Failed to evaluate resume.");
      }

      const data = await response.json();
      setResult(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <header>
        <h1>Resume ATS Analyzer</h1>
        <p>Evaluate your resume against a job description.</p>
      </header>

      <form onSubmit={handleSubmit} className="form">

        <div className="field">
          <label>Upload Resume (PDF)</label>

          <input
            type="file"
            accept=".pdf,application/pdf"
            onChange={(e) => setResume(e.target.files[0])}
          />

          {resume && <p>{resume.name}</p>}
        </div>

        <div className="field">
          <label>Job Description</label>

          <textarea
            rows="10"
            placeholder="Paste the job description here..."
            value={jobDescription}
            onChange={(e) => setJobDescription(e.target.value)}
          />
        </div>

        <button type="submit" disabled={loading}>
          {loading ? "Analyzing..." : "Analyze Resume"}
        </button>

      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <section className="results">

          <h2>ATS Evaluation</h2>

          <div className="score">
            <span>{result.overall_score}</span>
            <p>Overall Match Score / 100</p>
          </div>

          <h3>Score Breakdown</h3>

          {[
            ["Technical Skills", result.skills_score],
            ["Experience", result.experience_score],
            ["Projects", result.projects_score],
            ["Education", result.education_score],
            ["Keywords", result.keyword_score]
          ].map(([name, score]) => (
            <div className="score-row" key={name}>
              <span>{name}</span>
              <strong>{Math.round(score * 100)}%</strong>
            </div>
          ))}

          <h3>Matched Skills</h3>
          <ul>
            {result.matched_skills.map((skill, i) => (
              <li key={i}>{skill}</li>
            ))}
          </ul>

          <h3>Missing Skills</h3>
          <ul>
            {result.missing_skills.map((skill, i) => (
              <li key={i}>{skill}</li>
            ))}
          </ul>

          <h3>Strengths</h3>
          <ul>
            {result.strengths.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>

          <h3>Weaknesses</h3>
          <ul>
            {result.weaknesses.map((item, i) => (
              <li key={i}>{item}</li>
            ))}
          </ul>

          <h3>Recommendation</h3>
          <p>{result.recommendation}</p>

        </section>
      )}
    </div>
  );
}

export default App;
