export interface User {
  id: string;
  email: string;
  name: string;
  age?: number;
  date_of_birth?: string;
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
  date_of_birth?: string;
  anonymous: boolean;
}

export interface AuthResponse {
  success: boolean;
  user: User;
  session: AuthSession;
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
  isNewUser: boolean; // Track if user just registered
}
