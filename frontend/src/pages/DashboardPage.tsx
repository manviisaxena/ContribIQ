import { useEffect, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/useAuth'
import { useAnalysis } from '../hooks/useAnalysis'
import { parseGitHubRepository } from '../utils/validation'
import BrandLogo from '../components/BrandLogo'
import '../styles/dashboard.css'

export default function DashboardPage() {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()
  const analysis = useAnalysis()
  const [repository, setRepository] = useState('')
  const [inputError, setInputError] = useState('')
  const busy = analysis.status === 'starting' || analysis.status === 'running' || analysis.status === 'done'

  useEffect(() => {
    if (token && analysis.status === 'done' && analysis.taskId) {
      navigate(`/overview/${encodeURIComponent(analysis.taskId)}`)
    }
  }, [token, analysis.status, analysis.taskId, navigate])

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (busy) return
    const parsed = parseGitHubRepository(repository)
    if (!parsed) {
      setInputError('Enter a GitHub repository URL or owner/repository, for example psf/requests.')
      return
    }
    setInputError('')
    await analysis.run(parsed.owner, parsed.repo)
  }

  function handleLogout() {
    analysis.reset()
    logout()
  }

  if (!token) return <Navigate to="/login" replace />

  return (
    <div className="dashboard-page">
      <header className="dashboard-header">
        <BrandLogo />
        <button
          onClick={handleLogout}
          className="dashboard-secondary"
        >
          Sign out
        </button>
      </header>

      <main className="dashboard-main">
        <h1>
          Welcome back{user?.name ? `, ${user.name}` : ''}
        </h1>
        <p className="dashboard-copy">
          Find your starting point in an open-source repository.
        </p>

        <section className="dashboard-card" aria-labelledby="analysis-heading">
          <h2 id="analysis-heading">Analyze a repository</h2>
          <form onSubmit={handleSubmit} noValidate aria-busy={busy}>
            <label htmlFor="repository">GitHub repository</label>
            <p id="repository-help">Paste a public GitHub repository URL or enter owner/repository.</p>
            <div className="dashboard-input-row">
              <input
                id="repository"
                name="repository"
                type="text"
                placeholder="https://github.com/psf/requests"
                value={repository}
                onChange={event => { setRepository(event.target.value); setInputError('') }}
                disabled={busy}
                aria-invalid={!!inputError}
                aria-describedby={inputError ? 'repository-help repository-error' : 'repository-help'}
                autoCapitalize="none"
                spellCheck={false}
              />
              <button type="submit" className="dashboard-primary" disabled={busy}>
                {busy ? 'Analyzing...' : analysis.status === 'error' ? 'Try again' : 'Analyze repository'}
              </button>
            </div>
            {inputError && <p id="repository-error" className="dashboard-error" role="alert">{inputError}</p>}
          </form>

          {analysis.error && <p className="dashboard-error" role="alert">{analysis.error}</p>}
          {busy && (
            <div className="dashboard-progress" role="status">
              <p>{analysis.status === 'starting' ? 'Submitting analysis...' : 'Analyzing repository. This can take up to two minutes.'}</p>
              <p className="dashboard-copy">Keep the background worker running while analysis completes.</p>
            </div>
          )}
          {analysis.steps.length > 0 && (
            <ul className="dashboard-steps" aria-label="Analysis steps">
              {analysis.steps.map((step, index) => (
                <li key={`${step.step}-${index}`}>
                  <span>{step.step.replace(/_/g, ' ')}</span>
                  <span className={step.status === 'error' ? 'dashboard-error' : ''}>
                    {step.status === 'done' ? 'Complete' : step.status}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
    </div>
  )
}
