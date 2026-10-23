export interface LoginPayload {
  email: string
  password: string
  rememberMe: boolean
}

export interface LoginResponse {
  token: string
  user: { id: string; email: string; name: string }
}

export async function loginWithEmail(payload: LoginPayload): Promise<LoginResponse> {
  await new Promise(r => setTimeout(r, 1600))
  if (payload.email === 'fail@test.com') {
    throw new Error('Invalid email or password. Please try again.')
  }
  return {
    token: 'mock-jwt-token',
    user: { id: '1', email: payload.email, name: payload.email.split('@')[0] },
  }
}

export async function requestPasswordReset(email: string): Promise<void> {
  await new Promise(r => setTimeout(r, 800))
  console.log('Password reset requested for', email)
}

export function getGitHubOAuthUrl(): string {
  return '#github-oauth'
}
