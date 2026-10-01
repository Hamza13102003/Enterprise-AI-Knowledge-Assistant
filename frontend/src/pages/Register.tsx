import { useState } from 'react'
import type { FormEvent } from 'react'
import './Auth.css'
import { registerUser } from '../services/auth'

interface RegisterProps {
  onRegistered: () => void
  onLogin: () => void
}

function Register({ onRegistered, onLogin }: RegisterProps) {
  const [fullName, setFullName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    setError('')

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    setIsLoading(true)

    try {
      const response = await registerUser({
        full_name: fullName,
        email,
        password,
      })

      if (!response.success || !response.data.id) {
        throw new Error('Registration failed. Please try again.')
      }

      onRegistered()
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : 'Unable to create your account. Please try again.',
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
            <span className="auth-eyebrow">Get started</span>

            <h1>Create your account</h1>

            <p>
              Create an account to build and access your private AI knowledge
              workspace.
            </p>
          </div>

          <form className="auth-form" onSubmit={handleSubmit}>
            <label htmlFor="register-name">
              Full name
              <input
                id="register-name"
                type="text"
                value={fullName}
                onChange={(event) => setFullName(event.target.value)}
                placeholder="Your full name"
                autoComplete="name"
                minLength={2}
                maxLength={255}
                required
              />
            </label>

            <label htmlFor="register-email">
              Email address
              <input
                id="register-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@company.com"
                autoComplete="email"
                required
              />
            </label>

            <label htmlFor="register-password">
              Password
              <input
                id="register-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="At least 8 characters"
                autoComplete="new-password"
                minLength={8}
                maxLength={128}
                required
              />
            </label>

            <label htmlFor="register-confirm-password">
              Confirm password
              <input
                id="register-confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Repeat your password"
                autoComplete="new-password"
                minLength={8}
                maxLength={128}
                required
              />
            </label>

            {error && <p className="auth-error">{error}</p>}

            <button
              type="submit"
              className="auth-primary-button"
              disabled={isLoading}
            >
              {isLoading ? 'Creating account...' : 'Create account'}
            </button>
          </form>

          <div className="auth-divider">
            <span>Already have an account?</span>
          </div>

          <button
            type="button"
            className="auth-secondary-button"
            onClick={onLogin}
          >
            Back to sign in
          </button>
        </section>

        <p className="auth-footer">
          Your account will provide access to your own knowledge workspace.
        </p>
      </main>
    </div>
  )
}

export default Register