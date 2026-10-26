import { useCallback, useEffect, useMemo, useState } from 'react'
import './App.css'

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000').replace(/\/$/, '')
const apiUrl = (path) => `${API_BASE_URL}${path}`
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
  const [accountType, setAccountType] = useState('personal')
  const [readinessResult, setReadinessResult] = useState(null)
  const [documentType, setDocumentType] = useState('identity')
  const [sampleText, setSampleText] = useState('')
  const [imageQuality, setImageQuality] = useState(80)
  const [documentResult, setDocumentResult] = useState(null)
  const [documentError, setDocumentError] = useState('')
  const [documentLoading, setDocumentLoading] = useState(false)
  const [sandboxStatus, setSandboxStatus] = useState(null)
  const [sandboxResult, setSandboxResult] = useState(null)
  const [sandboxError, setSandboxError] = useState('')

  const fetchReadiness = useCallback(async (selectedType) => {
    setLoading(true)
    setError('')
    try {
      const response = await fetch(apiUrl(`/api/readiness?account_type=${selectedType}`))
      if (!response.ok) {
        throw new Error(`Request failed with status ${response.status}`)
      }
      const result = await response.json()
      if (!Array.isArray(result.steps)) {
        throw new Error('The readiness response is missing checklist steps.')
      }
      setData(result)
      setCompletedSteps({})
      setReadinessResult(null)
    } catch (fetchError) {
      setError(
        fetchError instanceof TypeError
          ? 'We could not connect to the readiness service. Please check that the backend is running.'
          : 'We could not load your checklist. Please try again.',
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    const request = window.setTimeout(() => {
      fetchReadiness('personal')
    }, 0)
    return () => window.clearTimeout(request)
  }, [fetchReadiness])

  useEffect(() => {
    fetch(apiUrl('/api/paypal/sandbox/status'))
      .then((response) => response.ok ? response.json() : null)
      .then((result) => setSandboxStatus(result))
      .catch(() => setSandboxStatus(null))
  }, [])

  const steps = data?.steps ?? []
  const completedCount = steps.filter((step) => completedSteps[step.key]).length
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
    if (submittedQuestion.length < 2 || assistantLoading) return
    setAssistantLoading(true)
    setAssistantError('')
    setAssistantAnswer(null)
    try {
      const response = await fetch(apiUrl('/api/assistant'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: submittedQuestion }),
      })
      if (!response.ok) {
        const failure = await response.json().catch(() => ({}))
        const validationMessage = Array.isArray(failure.detail)
          ? failure.detail[0]?.msg?.replace(/^Value error, /, '')
          : failure.detail
        throw new Error(validationMessage || `Request failed with status ${response.status}`)
      }
      setAssistantAnswer(await response.json())
      setQuestion('')
    } catch (submitError) {
      setAssistantError(submitError instanceof TypeError
        ? 'The assistant is unavailable. Please check that the backend is running.'
        : submitError.message)
    } finally {
      setAssistantLoading(false)
    }
  }

  const changeAccountType = (selectedType) => {
    if (selectedType === accountType) return
    setAccountType(selectedType)
    fetchReadiness(selectedType)
  }

  const handleStepToggle = async (stepKey) => {
    const nextAnswers = { ...completedSteps, [stepKey]: !completedSteps[stepKey] }
    setCompletedSteps(nextAnswers)
    try {
      const response = await fetch(apiUrl('/api/readiness/evaluate'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ account_type: accountType, answers: nextAnswers }),
      })
      if (response.ok) setReadinessResult(await response.json())
    } catch {
      setReadinessResult(null)
    }
  }

  const loadSample = async () => {
    setDocumentError('')
    try {
      const response = await fetch(apiUrl(`/api/documents/sample?document_type=${documentType}`))
      if (!response.ok) throw new Error('Sample unavailable')
      const result = await response.json()
      setSampleText(result.sample_text)
      setDocumentResult(null)
    } catch {
      setDocumentError('The synthetic sample could not be loaded. Check that the backend is running.')
    }
  }

  const reviewDocument = async (event) => {
    event.preventDefault()
    if (!sampleText.trim()) return
    setDocumentLoading(true)
    setDocumentError('')
    setDocumentResult(null)
    try {
      const response = await fetch(apiUrl('/api/documents/review'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          document_type: documentType,
          sample_text: sampleText,
          image_quality: imageQuality,
          is_synthetic_or_redacted: true,
        }),
      })
      if (!response.ok) throw new Error('Review rejected')
      setDocumentResult(await response.json())
    } catch {
      setDocumentError('Review failed. Use only synthetic or fully redacted sample values.')
    } finally {
      setDocumentLoading(false)
    }
  }

  const createSandboxOrder = async () => {
    setSandboxError('')
    setSandboxResult(null)
    try {
      const response = await fetch(apiUrl('/api/paypal/sandbox/orders'), {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ amount: '1.00', currency: 'USD' }),
      })
      const result = await response.json()
      if (!response.ok) throw new Error(result.detail || 'Sandbox request failed')
      setSandboxResult(result)
    } catch (sandboxRequestError) {
      setSandboxError(sandboxRequestError.message)
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
            <div className="account-switch" aria-label="Account type">
              {['personal', 'business'].map((type) => (
                <button
                  className={accountType === type ? 'is-active' : ''}
                  key={type}
                  type="button"
                  onClick={() => changeAccountType(type)}
                >
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </button>
              ))}
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
                <button className="secondary-button" type="button" onClick={() => fetchReadiness(accountType)}>Try again</button>
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
                    const isComplete = Boolean(completedSteps[step.key])
                    return (
                      <label className={`step-row ${isComplete ? 'is-complete' : ''}`} key={step.id}>
                        <input
                          type="checkbox"
                          checked={isComplete}
                          onChange={() => handleStepToggle(step.key)}
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
                {readinessResult && (
                  <div className="readiness-result" role="status">
                    <span className="score-ring">{readinessResult.score}%</span>
                    <div>
                      <strong>Simulated readiness review</strong>
                      <p>{readinessResult.recommendation}</p>
                      <small>{readinessResult.disclaimer}</small>
                    </div>
                  </div>
                )}
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
                  minLength={2}
                  maxLength={500}
                  value={question}
                  onChange={(event) => setQuestion(event.target.value)}
                  placeholder="Type your question…"
                />
                <button type="submit" aria-label="Submit question" disabled={question.trim().length < 2 || assistantLoading}>
                  {assistantLoading ? '…' : '→'}
                </button>
              </form>
              {assistantError && <p className="assistant-error" role="alert">{assistantError}</p>}
              {assistantAnswer && (
                <div className="assistant-answer" role="status">
                  {assistantAnswer.topic && <strong>{assistantAnswer.topic}</strong>}
                  <p>{assistantAnswer.answer}</p>
                  {(assistantAnswer.sources || [{ url: assistantAnswer.source_url, title: 'Official guidance' }]).map((source) => (
                    <a href={source.url} key={`${source.url}:${source.title}`} target="_blank" rel="noreferrer">
                      {source.title} <span aria-hidden="true">↗</span>
                    </a>
                  ))}
                  <small>Answer mode: {assistantAnswer.provider || 'verified knowledge base'}</small>
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

        <section className="lab-grid" aria-label="Prototype labs">
          <form className="card lab-card" onSubmit={reviewDocument}>
            <p className="eyebrow">Safe sample lab</p>
            <h2>Simulated document review</h2>
            <p className="card-description">
              Test field extraction and readability using synthetic or fully redacted text only.
              Real identity documents are not accepted or stored.
            </p>
            <div className="field-row">
              <label>
                Sample type
                <select value={documentType} onChange={(event) => setDocumentType(event.target.value)}>
                  <option value="identity">Identity</option>
                  <option value="business">Business</option>
                  <option value="address">Address</option>
                </select>
              </label>
              <label>
                Readability: {imageQuality}%
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={imageQuality}
                  onChange={(event) => setImageQuality(Number(event.target.value))}
                />
              </label>
            </div>
            <label className="sample-label" htmlFor="sample-document">Synthetic/redacted fields</label>
            <textarea
              id="sample-document"
              value={sampleText}
              onChange={(event) => setSampleText(event.target.value)}
              placeholder="Load a safe sample or enter redacted key: value fields"
            />
            <div className="button-row">
              <button className="secondary-button" type="button" onClick={loadSample}>Load safe sample</button>
              <button className="primary-button" type="submit" disabled={!sampleText.trim() || documentLoading}>
                {documentLoading ? 'Reviewing…' : 'Review sample'}
              </button>
            </div>
            {documentError && <p className="inline-error" role="alert">{documentError}</p>}
            {documentResult && (
              <div className="lab-result" role="status">
                <strong>{documentResult.result === 'sample-ready' ? 'Sample looks ready' : 'Sample needs attention'}</strong>
                <p>{documentResult.recommendation}</p>
                <dl>
                  <div><dt>Readability</dt><dd>{documentResult.readability}</dd></div>
                  <div><dt>Fields found</dt><dd>{Object.keys(documentResult.extracted_fields).length}</dd></div>
                  <div><dt>Missing</dt><dd>{documentResult.missing_fields.join(', ') || 'None'}</dd></div>
                </dl>
                <small>{documentResult.disclaimer}</small>
              </div>
            )}
          </form>

          <section className="card lab-card sandbox-card" aria-labelledby="sandbox-title">
            <p className="eyebrow">Developer demonstration</p>
            <h2 id="sandbox-title">PayPal Sandbox checkout</h2>
            <p className="card-description">
              Create a USD 1.00 test order through the backend. Server credentials never enter the browser.
            </p>
            <div className="sandbox-state">
              <span className={`status-dot ${sandboxStatus?.configured ? '' : 'is-muted'}`} />
              {sandboxStatus?.configured ? 'Sandbox configured' : 'Credentials not configured'}
            </div>
            <button
              className="primary-button"
              type="button"
              disabled={!sandboxStatus?.configured}
              onClick={createSandboxOrder}
            >
              Create test order
            </button>
            {sandboxError && <p className="inline-error" role="alert">{sandboxError}</p>}
            {sandboxResult && (
              <div className="lab-result" role="status">
                <strong>Sandbox order {sandboxResult.status}</strong>
                <p>Order ID: {sandboxResult.id}</p>
                {sandboxResult.approve_url && (
                  <a href={sandboxResult.approve_url} target="_blank" rel="noreferrer">Open Sandbox approval ↗</a>
                )}
              </div>
            )}
            <div className="notice-box">
              <span className="notice-icon">i</span>
              <p>Sandbox payments test checkout only. They do not affect or represent PayPal KYC approval.</p>
            </div>
            <a className="help-link" href="https://developer.paypal.com/api/make-api-requests/" target="_blank" rel="noreferrer">
              PayPal Sandbox documentation <span aria-hidden="true">↗</span>
            </a>
          </section>
        </section>
      </main>

      <footer>
        <span>PayReady India · Independent prototype</span>
        <span>This is not an official PayPal service.</span>
      </footer>
    </div>
  )
}

export default App
