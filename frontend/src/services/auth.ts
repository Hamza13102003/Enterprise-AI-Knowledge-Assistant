export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  email: string
  password: string
  full_name: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserResponse {
  id: string
  email: string
  full_name: string
  role: string
  is_active: boolean
  last_login: string | null
  created_at: string
  updated_at: string
}

export interface APIResponse<T> {
  success: boolean
  message: string
  data: T
}

const API_BASE_URL = 'http://localhost:8000/api/v1'

export async function loginUser(
  payload: LoginRequest,
): Promise<APIResponse<TokenResponse>> {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)

    throw new Error(
      errorData?.detail ?? 'Unable to sign in. Please check your credentials.',
    )
  }

  return response.json() as Promise<APIResponse<TokenResponse>>
}

export async function registerUser(
  payload: RegisterRequest,
): Promise<APIResponse<UserResponse>> {
  const response = await fetch(`${API_BASE_URL}/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => null)

    throw new Error(
      errorData?.detail ?? 'Unable to create your account. Please try again.',
    )
  }

  return response.json() as Promise<APIResponse<UserResponse>>
}