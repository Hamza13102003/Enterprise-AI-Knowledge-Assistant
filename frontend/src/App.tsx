import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from 'react'
import type { ChangeEvent } from 'react'
import './App.css'
import Login from './pages/Login'
import Register from './pages/Register'
import {
  authenticatedFetch,
  clearAccessToken,
  getAccessToken,
  parseApiError,
} from './services/api'
import {
  deleteDocument,
  getDocuments,
  uploadDocument,
} from './services/documents'
import type { DocumentItem } from './services/documents'
import { queryRAG } from './services/rag'
import type { RAGResponse } from './services/rag'

interface User {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  last_login: string | null
  created_at: string
  updated_at: string
}

type Screen =
  | 'login'
  | 'register'
  | 'dashboard'
  | 'documents'
  | 'assistant'

const navigationItems = [
  {
    label: 'Dashboard',
    icon: '⌂',
    screen: 'dashboard' as Screen,
  },
  {
    label: 'Documents',
    icon: '▤',
    screen: 'documents' as Screen,
  },
  {
    label: 'AI Assistant',
    icon: '✦',
    screen: 'assistant' as Screen,
  },
  {
    label: 'Settings',
    icon: '⚙',
    screen: 'dashboard' as Screen,
  },
]

function formatFileSize(bytes: number): string {
  if (bytes < 1024) {
    return `${bytes} B`
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatAssistantAnswer(answer: string): string {
  let cleaned = answer
    .replace(/\\-/g, '-')
    .replace(/^#{1,6}\s+/gm, '')
    .trim()

  if (cleaned.startsWith('- ')) {
    cleaned = cleaned.slice(2)
  }

  const items = cleaned
    .split(/\s+-\s+/)
    .map((item) => item.trim())
    .filter(Boolean)

  if (items.length > 1) {
    return items.map((item) => `• ${item}`).join('\n')
  }

  return cleaned
}

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/).filter(Boolean)

  if (parts.length === 0) {
    return 'U'
  }

  return parts
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() ?? '')
    .join('')
}

interface DashboardProps {
  user: User
  documents: DocumentItem[]
  isLoadingDocuments: boolean
  documentError: string
  onNavigate: (screen: Screen) => void
  onUpload: (file: File) => Promise<void>
  onLogout: () => void
}

function Dashboard({
  user,
  documents,
  isLoadingDocuments,
  documentError,
  onNavigate,
  onUpload,
  onLogout,
}: DashboardProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadError, setUploadError] = useState('')

  const totalChunks = useMemo(
    () =>
      documents.reduce(
        (total, document) => total + document.chunks_count,
        0,
      ),
    [documents],
  )

  const handleUploadClick = () => {
    setUploadError('')
    fileInputRef.current?.click()
  }

  const handleFileChange = async (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0]

    if (!file) {
      return
    }

    setUploadError('')
    setUploading(true)

    try {
      await onUpload(file)
    } catch (error) {
      setUploadError(
        error instanceof Error
          ? error.message
          : 'Unable to upload the document.',
      )
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  return (
    <div className="app-shell">
      <Sidebar
        user={user}
        activeScreen="dashboard"
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">Workspace</span>
            <h2>Dashboard</h2>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="icon-button"
              aria-label="Notifications"
            >
              !
            </button>

            <button type="button" className="help-button">
              Help
            </button>
          </div>
        </header>

        <section className="dashboard">
          <div className="welcome-card">
            <div>
              <span className="card-label">Enterprise Knowledge</span>

              <h3>
                Your knowledge,
                <br />
                <span>intelligently connected.</span>
              </h3>

              <p>
                Upload your organization's documents and use AI to find
                answers grounded in your private knowledge base.
              </p>

              <div className="welcome-actions">
                <button
                  type="button"
                  className="primary-button"
                  onClick={handleUploadClick}
                  disabled={uploading}
                >
                  {uploading ? 'Uploading...' : '+ Upload document'}
                </button>

                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => onNavigate('documents')}
                >
                  View documents
                </button>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={handleFileChange}
                hidden
              />

              {uploadError && (
                <p className="dashboard-error">{uploadError}</p>
              )}
            </div>

            <div className="welcome-visual" aria-hidden="true">
              <div className="visual-orbit orbit-one" />
              <div className="visual-orbit orbit-two" />
              <div className="visual-core">✦</div>
            </div>
          </div>

          <div className="section-heading">
            <div>
              <span className="card-label">Overview</span>
              <h3>Knowledge workspace</h3>
            </div>

            <span className="workspace-badge">Ready</span>
          </div>

          <div className="stats-grid">
            <article className="stat-card">
              <div className="stat-icon">▤</div>
              <span>Documents</span>
              <strong>
                {isLoadingDocuments ? '...' : documents.length}
              </strong>
              <small>
                {documents.length === 0
                  ? 'No documents uploaded yet'
                  : 'Documents in your knowledge base'}
              </small>
            </article>

            <article className="stat-card">
              <div className="stat-icon">✦</div>
              <span>AI Queries</span>
              <strong>—</strong>
              <small>Ask the AI assistant</small>
            </article>

            <article className="stat-card">
              <div className="stat-icon">◈</div>
              <span>Knowledge Chunks</span>
              <strong>
                {isLoadingDocuments ? '...' : totalChunks}
              </strong>
              <small>Indexed knowledge</small>
            </article>

            <article className="stat-card">
              <div className="stat-icon">●</div>
              <span>System Status</span>
              <strong>Ready</strong>
              <small>All core services available</small>
            </article>
          </div>

          {documentError && (
            <section className="dashboard-message error">
              {documentError}
            </section>
          )}

          <section className="quick-start">
            <div className="quick-start-content">
              <span className="card-label">Get started</span>
              <h3>Build your private AI knowledge base</h3>
              <p>
                Upload PDFs, DOCX, or TXT documents. The assistant will
                process and index them so you can ask questions using
                retrieval-augmented generation.
              </p>
            </div>

            <div className="pipeline">
              <span>Document</span>
              <i>→</i>
              <span>Chunk</span>
              <i>→</i>
              <span>Embed</span>
              <i>→</i>
              <span>Retrieve</span>
              <i>→</i>
              <span>Answer</span>
            </div>
          </section>
        </section>
      </main>
    </div>
  )
}

interface DocumentsPageProps {
  user: User
  documents: DocumentItem[]
  isLoading: boolean
  error: string
  onNavigate: (screen: Screen) => void
  onUpload: (file: File) => Promise<void>
  onDelete: (documentId: string) => Promise<void>
  onLogout: () => void
}

function DocumentsPage({
  user,
  documents,
  isLoading,
  error,
  onNavigate,
  onUpload,
  onDelete,
  onLogout,
}: DocumentsPageProps) {
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [uploading, setUploading] = useState(false)
  const [actionError, setActionError] = useState('')

  const handleUpload = async (
    event: ChangeEvent<HTMLInputElement>,
  ) => {
    const file = event.target.files?.[0]

    if (!file) {
      return
    }

    setActionError('')
    setUploading(true)

    try {
      await onUpload(file)
    } catch (uploadError) {
      setActionError(
        uploadError instanceof Error
          ? uploadError.message
          : 'Unable to upload the document.',
      )
    } finally {
      setUploading(false)
      event.target.value = ''
    }
  }

  const handleDelete = async (documentId: string) => {
    const confirmed = window.confirm(
      'Are you sure you want to delete this document?',
    )

    if (!confirmed) {
      return
    }

    setActionError('')

    try {
      await onDelete(documentId)
    } catch (deleteError) {
      setActionError(
        deleteError instanceof Error
          ? deleteError.message
          : 'Unable to delete the document.',
      )
    }
  }

  return (
    <div className="app-shell">
      <Sidebar
        user={user}
        activeScreen="documents"
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">Workspace</span>
            <h2>Documents</h2>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="primary-button"
              onClick={() => fileInputRef.current?.click()}
              disabled={uploading}
            >
              {uploading ? 'Uploading...' : '+ Upload document'}
            </button>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt"
              onChange={handleUpload}
              hidden
            />
          </div>
        </header>

        <section className="dashboard">
          <div className="section-heading document-page-heading">
            <div>
              <span className="card-label">Knowledge Base</span>
              <h3>Your documents</h3>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={() => onNavigate('dashboard')}
            >
              Back to dashboard
            </button>
          </div>

          {error && (
            <section className="dashboard-message error">
              {error}
            </section>
          )}

          {actionError && (
            <section className="dashboard-message error">
              {actionError}
            </section>
          )}

          {isLoading ? (
            <section className="document-empty">
              <strong>Loading documents...</strong>
              <span>Retrieving your knowledge base.</span>
            </section>
          ) : documents.length === 0 ? (
            <section className="document-empty">
              <div className="stat-icon">▤</div>
              <strong>No documents yet</strong>
              <span>
                Upload a PDF, DOCX, or TXT file to build your knowledge
                base.
              </span>
              <button
                type="button"
                className="primary-button"
                onClick={() => fileInputRef.current?.click()}
              >
                + Upload your first document
              </button>
            </section>
          ) : (
            <section className="documents-list">
              {documents.map((document) => (
                <article className="document-row" key={document.id}>
                  <div className="document-icon">▤</div>

                  <div className="document-main">
                    <strong>{document.filename}</strong>
                    <span>
                      {formatFileSize(document.file_size)} •{' '}
                      {document.chunks_count} chunks •{' '}
                      {formatDate(document.created_at)}
                    </span>
                  </div>

                  <span
                    className={`document-status ${document.status}`}
                  >
                    {document.status}
                  </span>

                  <button
                    type="button"
                    className="document-delete"
                    onClick={() => handleDelete(document.id)}
                    aria-label={`Delete ${document.filename}`}
                  >
                    Delete
                  </button>
                </article>
              ))}
            </section>
          )}
        </section>
      </main>
    </div>
  )
}

interface AssistantPageProps {
  user: User
  documents: DocumentItem[]
  onNavigate: (screen: Screen) => void
  onLogout: () => void
}

function AssistantPage({
  user,
  documents,
  onNavigate,
  onLogout,
}: AssistantPageProps) {
  const [query, setQuery] = useState('')
  const [result, setResult] = useState<RAGResponse | null>(null)
  const [isQuerying, setIsQuerying] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    const trimmedQuery = query.trim()

    if (!trimmedQuery || isQuerying) {
      return
    }

    setError('')
    setIsQuerying(true)

    try {
      const response = await queryRAG({
        query: trimmedQuery,
        top_k: 5,
      })

      setResult(response)
    } catch (queryError) {
      setError(
        queryError instanceof Error
          ? queryError.message
          : 'Unable to get an answer from the AI assistant.',
      )
    } finally {
      setIsQuerying(false)
    }
  }

  const clearConversation = () => {
    setQuery('')
    setResult(null)
    setError('')
  }

  return (
    <div className="app-shell">
      <Sidebar
        user={user}
        activeScreen="assistant"
        onNavigate={onNavigate}
        onLogout={onLogout}
      />

      <main className="main-content">
        <header className="topbar">
          <div>
            <span className="eyebrow">Workspace</span>
            <h2>AI Assistant</h2>
          </div>

          <div className="topbar-actions">
            <button
              type="button"
              className="help-button"
              onClick={clearConversation}
            >
              Clear
            </button>
          </div>
        </header>

        <section className="dashboard">
          <section className="welcome-card">
            <div>
              <span className="card-label">Private AI</span>

              <h3>
                Ask questions about
                <br />
                <span>your knowledge base.</span>
              </h3>

              <p>
                The assistant retrieves relevant information from your
                uploaded documents and uses it to generate a grounded
                answer.
              </p>
            </div>

            <div className="welcome-visual" aria-hidden="true">
              <div className="visual-orbit orbit-one" />
              <div className="visual-orbit orbit-two" />
              <div className="visual-core">✦</div>
            </div>
          </section>

          <section className="quick-start">
            <div className="quick-start-content">
              <span className="card-label">Ask the assistant</span>
              <h3>
                Search across {documents.length}{' '}
                {documents.length === 1 ? 'document' : 'documents'}
              </h3>
              <p>
                Ask a question and the RAG pipeline will retrieve the
                most relevant knowledge before generating the answer.
              </p>
            </div>

            <form
              className="assistant-form"
              onSubmit={handleSubmit}
            >
              <textarea
                value={query}
                onChange={(event) => setQuery(event.target.value)}
                placeholder="Ask something about your uploaded documents..."
                rows={4}
                maxLength={5000}
                disabled={isQuerying}
              />

              <div className="assistant-form-footer">
                <span>{query.length}/5000</span>

                <button
                  type="submit"
                  className="primary-button"
                  disabled={!query.trim() || isQuerying}
                >
                  {isQuerying ? 'Thinking...' : 'Ask AI'}
                </button>
              </div>
            </form>
          </section>

          {error && (
            <section className="dashboard-message error">
              {error}
            </section>
          )}

          {isQuerying && (
            <section className="dashboard-message">
              Searching your knowledge base and generating an answer...
            </section>
          )}

          {result && !isQuerying && (
            <>
              <section className="assistant-answer">
                <div className="section-heading">
                  <div>
                    <span className="card-label">Answer</span>
                    <h3>AI response</h3>
                  </div>
                </div>

                <div className="assistant-answer-content">
                  {formatAssistantAnswer(result.answer)
                    .split('\n')
                    .map((line, index) => (
                           <span key={`${line}-${index}`}>
                              {line}
                              <br />
                            </span>
                          ))}
                </div>
              </section>

              <section className="quick-start">
                <div className="quick-start-content">
                  <span className="card-label">Sources</span>
                  <h3>
                    Retrieved knowledge ({result.sources.length})
                  </h3>
                  <p>
                    These document chunks were retrieved from your
                    private knowledge base for this answer.
                  </p>
                </div>

                {result.sources.length === 0 ? (
                  <div className="dashboard-message">
                    No source chunks were returned.
                  </div>
                ) : (
                  <div className="assistant-sources">
                    {result.sources.map((source, index) => (
                      <article
                        className="assistant-source"
                        key={source.chunk_id}
                      >
                        <div className="assistant-source-header">
                          <strong>Source {index + 1}</strong>
                          <span>
                            Relevance: {source.score.toFixed(3)}
                          </span>
                        </div>

                        <p>{source.content}</p>
                      </article>
                    ))}
                  </div>
                )}
              </section>
            </>
          )}
        </section>
      </main>
    </div>
  )
}

interface SidebarProps {
  user: User
  activeScreen: Screen
  onNavigate: (screen: Screen) => void
  onLogout: () => void
}

function Sidebar({
  user,
  activeScreen,
  onNavigate,
  onLogout,
}: SidebarProps) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-mark">AI</div>
        <div>
          <h1>Knowledge Assistant</h1>
          <span>Enterprise AI</span>
        </div>
      </div>

      <nav className="sidebar-nav" aria-label="Main navigation">
        <span className="nav-section-title">Workspace</span>

        {navigationItems.map((item) => (
          <button
            key={item.label}
            type="button"
            className={`nav-item ${
              item.screen === activeScreen ? 'active' : ''
            }`}
            onClick={() => onNavigate(item.screen)}
          >
            <span className="nav-icon" aria-hidden="true">
              {item.icon}
            </span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>

      <div className="sidebar-bottom">
        <div className="system-status">
          <span className="status-dot" />
          <div>
            <strong>System ready</strong>
            <span>AI services connected</span>
          </div>
        </div>

        <div className="user-card">
          <div className="avatar">{getInitials(user.full_name)}</div>

          <div className="user-info">
            <strong>{user.full_name}</strong>
            <span>{user.email}</span>
          </div>

          <button
            type="button"
            className="logout-button"
            aria-label="Logout"
            onClick={onLogout}
          >
            ↪
          </button>
        </div>
      </div>
    </aside>
  )
}

function App() {
  const [screen, setScreen] = useState<Screen>('login')
  const [user, setUser] = useState<User | null>(null)
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [isInitializing, setIsInitializing] = useState(true)
  const [isLoadingDocuments, setIsLoadingDocuments] = useState(false)
  const [documentError, setDocumentError] = useState('')

  const loadCurrentUser = async (): Promise<User> => {
    const response = await authenticatedFetch('/me')

    if (!response.ok) {
      throw await parseApiError(
        response,
        'Your session is no longer valid.',
      )
    }

    const result = (await response.json()) as {
      success: boolean
      message: string
      data: User
    }

    if (!result.success || !result.data) {
      throw new Error('Unable to load your account.')
    }

    return result.data
  }

  const loadDocuments = async () => {
    setIsLoadingDocuments(true)
    setDocumentError('')

    try {
      const result = await getDocuments()
      setDocuments(result)
    } catch (error) {
      setDocumentError(
        error instanceof Error
          ? error.message
          : 'Unable to load your documents.',
      )
    } finally {
      setIsLoadingDocuments(false)
    }
  }

  useEffect(() => {
    const restoreSession = async () => {
      const token = getAccessToken()

      if (!token) {
        setIsInitializing(false)
        return
      }

      try {
        const currentUser = await loadCurrentUser()

        setUser(currentUser)
        setScreen('dashboard')
        await loadDocuments()
      } catch {
        clearAccessToken()
        setUser(null)
        setScreen('login')
      } finally {
        setIsInitializing(false)
      }
    }

    void restoreSession()
  }, [])

  const handleLogin = async (accessToken: string) => {
    sessionStorage.setItem('access_token', accessToken)

    try {
      const currentUser = await loadCurrentUser()

      setUser(currentUser)
      setScreen('dashboard')
      await loadDocuments()
    } catch (error) {
      clearAccessToken()
      throw error
    }
  }

  const handleUpload = async (file: File) => {
    await uploadDocument(file)
    await loadDocuments()
  }

  const handleDelete = async (documentId: string) => {
    await deleteDocument(documentId)
    await loadDocuments()
  }

  const handleLogout = () => {
    clearAccessToken()
    setUser(null)
    setDocuments([])
    setScreen('login')
  }

  if (isInitializing) {
    return (
      <div className="app-loading">
        <span>Loading workspace...</span>
      </div>
    )
  }

  if (screen === 'login') {
    return (
      <Login
        onLogin={(token) => {
          void handleLogin(token).catch(() => undefined)
        }}
        onRegister={() => setScreen('register')}
      />
    )
  }

  if (screen === 'register') {
    return (
      <Register
        onRegistered={() => setScreen('login')}
        onLogin={() => setScreen('login')}
      />
    )
  }

  if (!user) {
    return null
  }

  if (screen === 'documents') {
    return (
      <DocumentsPage
        user={user}
        documents={documents}
        isLoading={isLoadingDocuments}
        error={documentError}
        onNavigate={setScreen}
        onUpload={handleUpload}
        onDelete={handleDelete}
        onLogout={handleLogout}
      />
    )
  }

  if (screen === 'assistant') {
    return (
      <AssistantPage
        user={user}
        documents={documents}
        onNavigate={setScreen}
        onLogout={handleLogout}
      />
    )
  }

  return (
    <Dashboard
      user={user}
      documents={documents}
      isLoadingDocuments={isLoadingDocuments}
      documentError={documentError}
      onNavigate={setScreen}
      onUpload={handleUpload}
      onLogout={handleLogout}
    />
  )
}

export default App
