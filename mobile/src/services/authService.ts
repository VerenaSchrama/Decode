import { getApiConfig } from '../config/environment';
import { 
  LoginRequest, 
  RegisterRequest, 
  AuthResponse, 
  User, 
  AuthSession 
} from '../types/Auth';

class AuthService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = getApiConfig().baseUrl;
  }

  /**
   * Register a new user
   */
  async register(userData: RegisterRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }

  /**
   * Login user
   */
  async login(credentials: LoginRequest): Promise<AuthResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  }

  /**
   * Logout user
   */
  async logout(accessToken: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/logout`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        console.warn('Logout request failed:', response.status);
      }
    } catch (error) {
      console.error('Logout error:', error);
      // Don't throw error for logout - user should be logged out locally anyway
    }
  }

  /**
   * Get user profile
   */
  async getUserProfile(userId: string, accessToken: string): Promise<User> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/profile/${userId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.profile;
    } catch (error) {
      console.error('Get profile error:', error);
      throw error;
    }
  }

  /**
   * Verify token
   */
  async verifyToken(accessToken: string): Promise<boolean> {
    try {
      const response = await fetch(`${this.baseUrl}/auth/verify`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (response.ok) {
        return true;
      } else {
        console.warn('Token verification failed:', response.status);
        return false;
      }
    } catch (error) {
      console.error('Token verification error:', error);
      // If verification fails due to network issues, assume token is valid
      // This prevents users from being logged out due to temporary network problems
      return true;
    }
  }
}

export default new AuthService();
