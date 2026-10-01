const API_BASE_URL = 'http://localhost:8000/api/v1'

export function getAccessToken(): string | null {
  return sessionStorage.getItem('access_token')
}

export function clearAccessToken(): void {
  sessionStorage.removeItem('access_token')
}

export async function authenticatedFetch(
  path: string,
  options: RequestInit = {},
): Promise<Response> {
  const token = getAccessToken()

  const headers = new Headers(options.headers)

  if (token) {
    headers.set('Authorization', `Bearer ${token}`)
  }

  return fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  })
}

export async function parseApiError(
  response: Response,
  fallbackMessage: string,
): Promise<Error> {
  const errorData = await response.json().catch(() => null)

  return new Error(
    errorData?.detail ?? errorData?.message ?? fallbackMessage,
  )
}
