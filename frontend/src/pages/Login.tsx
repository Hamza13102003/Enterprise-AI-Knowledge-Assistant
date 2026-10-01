import { useState } from 'react'
import type { FormEvent } from 'react'
import './Auth.css'
import { loginUser } from '../services/auth'

interface LoginProps {
  onLogin: (accessToken: string) => void
  onRegister: () => void
}

function Login({ onLogin, onRegister }: LoginProps) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    setError('')
    setIsLoading(true)

    try {
      const response = await loginUser({
        email,
        password,
      })

      if (!response.success || !response.data.access_token) {
        throw new Error('Login failed. Please try again.')
      }

      onLogin(response.data.access_token)
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to sign in. Please try again.',
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-brand">
        <div className="brand-mark">AI</div>

        <div>
          <strong>Knowledge Assistant</strong>
          <span>Enterprise AI</span>
        </div>
      </div>

      <main className="auth-container">
        <section className="auth-card">
          <div className="auth-header">
            <span className="auth-eyebrow">Welcome back</span>

            <h1>Sign in to your workspace</h1>

            <p>
              Access your organization's private knowledge base and AI
              assistant.
            </p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label htmlFor="login-email">
              Email address
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@company.com"
                autoComplete="email"
                required
              />
            </label>

            <label htmlFor="login-password">
              Password
              <input
                id="login-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="Enter your password"
                autoComplete="current-password"
                required
              />
            </label>

            {error && <p className="auth-error">{error}</p>}

            <button
              type="submit"
              className="auth-primary-button"
              disabled={isLoading}
            >
              {isLoading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>

          <div className="auth-divider">
            <span>New to the workspace?</span>
          </div>

          <button
            type="button"
            className="auth-secondary-button"
            onClick={onRegister}
          >
            Create an account
          </button>
        </section>

        <p className="auth-footer">
          Private enterprise knowledge • AI-powered search • RAG
        </p>
      </main>
    </div>
  )
}

export default Login