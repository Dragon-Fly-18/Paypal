import { useEffect, useMemo, useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000/api/readiness'
const ASSISTANT_URL = 'http://127.0.0.1:8000/api/assistant'
const SUGGESTED_QUESTIONS = [
  'Why might verification be delayed?',
  'How do I prepare for verification?',
  'What should I check before receiving payments?',
]

function SparkIcon() {
  return (
    <svg aria-hidden="true" className="spark-icon" viewBox="0 0 24 24">
      <path d="M12 2.5 14.1 9.9 21.5 12l-7.4 2.1L12 21.5l-2.1-7.4L2.5 12l7.4-2.1L12 2.5Z" />
    </svg>
  )
}

function App() {
  const [data, setData] = useState(null)
  const [completedSteps, setCompletedSteps] = useState({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [question, setQuestion] = useState('')
  const [assistantAnswer, setAssistantAnswer] = useState(null)
  const [assistantLoading, setAssistantLoading] = useState(false)
  const [assistantError, setAssistantError] = useState('')

  const fetchReadiness = async () => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(API_URL)
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }
      const result = await response.json()
      if (!Array.isArray(result.steps)) {
        throw new Error('The readiness response is missing checklist steps.')
      }
      setData(result)
    } catch (fetchError) {
      setError(
        fetchError instanceof TypeError
          ? 'We could not connect to the readiness service. Please check that the backend is running.'
          : 'We could not load your checklist. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const request = window.setTimeout(() => {
      fetchReadiness()
    }, 0)
    return () => window.clearTimeout(request)
  }, [])

  const steps = data?.steps ?? []
  const completedCount = steps.filter((step) => completedSteps[step.id]).length
  const progress = steps.length
    ? Math.min(100, Math.round((completedCount / steps.length) * 100))
    : 0

  const statusText = useMemo(
    () => `${completedCount} of ${steps.length} steps complete`,
    [completedCount, steps.length],
  )

  const handleQuestionSubmit = async (event) => {
    event.preventDefault()
    const submittedQuestion = question.trim()
    if (!submittedQuestion || assistantLoading) return
    setAssistantLoading(true)
    setAssistantError('')
    setAssistantAnswer(null)
    try {
      const response = await fetch(ASSISTANT_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: submittedQuestion }),
      })
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }
      setAssistantAnswer(await response.json())
      setQuestion('')
    } catch (submitError) {
      setAssistantError(
        submitError instanceof TypeError
          ? 'The assistant is unavailable. Please check that the backend is running.'
          : 'The assistant could not answer right now. Please try again.',
      )
    } finally {
      setAssistantLoading(false)
    }
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="/" aria-label="PayReady India home">
          <span className="brand-mark">P</span>
          <span>PayReady <strong>India</strong></span>
        </a>
        <span className="tools-label">Merchant tools <span className="status-dot" /></span>
      </header>

      <main>
        <section className="hero-panel" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">Your onboarding companion</p>
            <h1 id="hero-title">Get ready to accept payments.</h1>
            <p className="hero-text">
              A simple, practical guide to help you understand the steps
              involved in getting payment-ready in India.
            </p>
            <a className="primary-button" href="#checklist">
              Start your checklist <span aria-hidden="true">→</span>
            </a>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="art-orbit orbit-one" />
            <div className="art-orbit orbit-two" />
            <div className="art-card">
              <span className="art-check">✓</span>
              <span><strong>Ready to grow</strong><small>Stay on track</small></span>
            </div>
            <div className="art-bar bar-one" />
            <div className="art-bar bar-two" />
            <div className="art-dot dot-one" />
            <div className="art-dot dot-two" />
          </div>
        </section>

        <div className="dashboard-grid">
          <section className="checklist-card card" id="checklist" aria-labelledby="checklist-title">
            <div className="section-heading">
              <div>
                <p className="eyebrow">Step-by-step guide</p>
                <h2 id="checklist-title">{data?.title || 'Merchant readiness checklist'}</h2>
              </div>
              {!loading && !error && <span className="completion-count">{statusText}</span>}
            </div>

            {loading && (
              <div className="loading-state" role="status">
                <span className="spinner" /> Loading your checklist…
              </div>
            )}
            {error && (
              <div className="error-state" role="alert">
                <strong>Something went wrong</strong>
                <p>{error}</p>
                <button className="secondary-button" type="button" onClick={fetchReadiness}>Try again</button>
              </div>
            )}
            {!loading && !error && (
              <>
                <div className="progress-summary">
                  <div className="progress-track" aria-label={`${progress}% complete`}>
                    <span style={{ width: `${progress}%` }} />
                  </div>
                  <strong>{progress}%</strong>
                </div>
                <div className="steps-list">
                  {steps.map((step, index) => {
                    const isComplete = Boolean(completedSteps[step.id])
                    return (
                      <label className={`step-row ${isComplete ? 'is-complete' : ''}`} key={step.id}>
                        <input
                          type="checkbox"
                          checked={isComplete}
                          onChange={() =>
                            setCompletedSteps((current) => ({
                              ...current,
                              [step.id]: !current[step.id],
                            }))
                          }
                        />
                        <span className="custom-checkbox" aria-hidden="true">{isComplete ? '✓' : ''}</span>
                        <span className="step-number">{String(index + 1).padStart(2, '0')}</span>
                        <span className="step-content">
                          <strong>{step.title}</strong>
                          <span>{step.description}</span>
                        </span>
                        <span className="step-status">{isComplete ? 'Done' : 'To do'}</span>
                      </label>
                    )
                  })}
                </div>
                <div className="notice-box">
                  <span className="notice-icon">i</span>
                  <p>{data.notice}</p>
                </div>
                <a
                  className="help-link"
                  href={data.official_help_url}
                  target="_blank"
                  rel="noreferrer"
                >
                  View official PayPal guidance <span aria-hidden="true">↗</span>
                </a>
              </>
            )}
          </section>

          <aside className="side-column">
            <section className="assistant-card card" aria-labelledby="assistant-title">
              <div className="assistant-icon"><SparkIcon /></div>
              <p className="eyebrow">Prototype assistant</p>
              <h2 id="assistant-title">Ask PayReady</h2>
              <p className="card-description">
                Ask about common onboarding topics. Answers are general guidance, not account decisions.
              </p>
              <div className="question-list">
                {SUGGESTED_QUESTIONS.map((suggestion) => (
                  <button type="button" key={suggestion} onClick={() => setQuestion(suggestion)}>
                    {suggestion} <span aria-hidden="true">→</span>
                  </button>
                ))}
              </div>
              <form className="question-form" onSubmit={handleQuestionSubmit}>
                <label className="sr-only" htmlFor="question">Ask a question</label>
                <input
                  id="question"
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Type your question…"
                />
                <button type="submit" aria-label="Submit question" disabled={!question.trim() || assistantLoading}>
                  {assistantLoading ? '…' : '→'}
                </button>
              </form>
              {assistantError && <p className="assistant-error" role="alert">{assistantError}</p>}
              {assistantAnswer && (
                <div className="assistant-answer" role="status">
                  {assistantAnswer.topic && <strong>{assistantAnswer.topic}</strong>}
                  <p>{assistantAnswer.answer}</p>
                  <a href={assistantAnswer.source_url} target="_blank" rel="noreferrer">
                    Read official guidance <span aria-hidden="true">↗</span>
                  </a>
                </div>
              )}
              <p className="prototype-note">Prototype · General guidance only · Questions are not stored</p>
            </section>

            <section className="safety-card" aria-labelledby="safety-title">
              <div className="safety-icon">✓</div>
              <div>
                <h2 id="safety-title">Keep your account safe</h2>
                <p>Never enter your PayPal password, PAN/Aadhaar numbers, or identity documents into this prototype.</p>
              </div>
            </section>
          </aside>
        </div>
      </main>

      <footer>
        <span>PayReady India · Independent prototype</span>
        <span>This is not an official PayPal service.</span>
      </footer>
    </div>
  )
}

export default App
