export interface TempUser {
  email: string;
  password: string;
  name: string;
  age?: number;
  anonymous: boolean;
}

export interface User {
  id: string;
  email: string;
  name: string;
  age?: number;
  anonymous: boolean;
}

export interface AuthSession {
  access_token: string;
  refresh_token: string;
  expires_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  name: string;
  age?: number;
  anonymous: boolean;
}

export interface AuthResponse {
  success: boolean;
  user: User;
  session: AuthSession | null;
  email_confirmation_required?: boolean;
  message: string;
}

export interface AuthError {
  message: string;
  code?: string;
  details?: string;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
  session: AuthSession | null;
  isLoading: boolean;
  error: AuthError | null;
}
