import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { AuthState, User, AuthSession, LoginRequest, RegisterRequest, AuthError } from '../types/Auth';
import authService from '../services/authService';

// Auth Actions
type AuthAction =
  | { type: 'AUTH_START' }
  | { type: 'AUTH_SUCCESS'; payload: { user: User; session: AuthSession } }
  | { type: 'AUTH_FAILURE'; payload: AuthError }
  | { type: 'AUTH_LOGOUT' }
  | { type: 'AUTH_CLEAR_ERROR' }
  | { type: 'AUTH_LOADING'; payload: boolean };

// Initial state
const initialState: AuthState = {
  isAuthenticated: false,
  user: null,
  session: null,
  isLoading: true,
  error: null,
};

// Auth reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'AUTH_START':
      return {
        ...state,
        isLoading: true,
        error: null,
      };
    case 'AUTH_SUCCESS':
      return {
        ...state,
        isAuthenticated: true,
        user: action.payload.user,
        session: action.payload.session,
        isLoading: false,
        error: null,
      };
    case 'AUTH_FAILURE':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        session: null,
        isLoading: false,
        error: action.payload,
      };
    case 'AUTH_LOGOUT':
      return {
        ...state,
        isAuthenticated: false,
        user: null,
        session: null,
        isLoading: false,
        error: null,
      };
    case 'AUTH_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      };
    case 'AUTH_CLEAR_ERROR':
      return {
        ...state,
        error: null,
      };
    default:
      return state;
  }
}

// Context type
interface AuthContextType extends AuthState {
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => Promise<void>;
  clearError: () => void;
  refreshUser: () => Promise<void>;
}

// Create context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Storage keys
const STORAGE_KEYS = {
  USER: '@auth_user',
  SESSION: '@auth_session',
};

// Auth Provider
interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Load stored auth data on app start
  useEffect(() => {
    loadStoredAuth();
  }, []);

  // Setup automatic token refresh every 50 minutes (tokens expire after 60 minutes)
  useEffect(() => {
    if (state.isAuthenticated && state.session) {
      const refreshInterval = setInterval(async () => {
        try {
          console.log('🔄 Auto-refreshing session...');
          await refreshUser();
        } catch (error) {
          console.error('Failed to auto-refresh session:', error);
        }
      }, 50 * 60 * 1000); // Every 50 minutes

      return () => clearInterval(refreshInterval);
    }
  }, [state.isAuthenticated, state.session]);

  // Refresh token on component mount if session exists
  useEffect(() => {
    if (state.isAuthenticated && state.session && state.user) {
      refreshUser().catch(err => console.error('Failed to refresh user on mount:', err));
    }
  }, [state.isAuthenticated]);

  const loadStoredAuth = async () => {
    try {
      const [storedUser, storedSession] = await Promise.all([
        AsyncStorage.getItem(STORAGE_KEYS.USER),
        AsyncStorage.getItem(STORAGE_KEYS.SESSION),
      ]);

      if (storedUser && storedSession) {
        const user = JSON.parse(storedUser);
        const session = JSON.parse(storedSession);

        // Check if session has required fields
        if (user?.id && session?.access_token) {
          // Check if session is not too old (e.g., less than 30 days)
          const sessionAge = Date.now() - (session.created_at || 0);
          const maxAge = 30 * 24 * 60 * 60 * 1000; // 30 days in milliseconds
          
          if (sessionAge > maxAge) {
            console.log('⚠️ Session too old, clearing stored auth');
            await clearStoredAuth();
            dispatch({ type: 'AUTH_LOGOUT' });
            return;
          }
          
          // Try to verify token, but don't fail if verification doesn't work
          try {
            const isValid = await authService.verifyToken(session.access_token);
            if (isValid) {
              dispatch({
                type: 'AUTH_SUCCESS',
                payload: { user, session },
              });
              console.log('✅ Restored user session with verified token:', user.email);
            } else {
              // Token verification failed, but restore session anyway to prevent logout
              dispatch({
                type: 'AUTH_SUCCESS',
                payload: { user, session },
              });
              console.log('⚠️ Restored user session without token verification:', user.email);
            }
          } catch (error) {
            // If verification fails, restore session anyway
            dispatch({
              type: 'AUTH_SUCCESS',
              payload: { user, session },
            });
            console.log('⚠️ Restored user session after verification error:', user.email);
          }
        } else {
          // Invalid stored data, clear it
          await clearStoredAuth();
          dispatch({ type: 'AUTH_LOGOUT' });
        }
      } else {
        dispatch({ type: 'AUTH_LOGOUT' });
      }
    } catch (error) {
      console.error('Error loading stored auth:', error);
      dispatch({ type: 'AUTH_LOGOUT' });
    } finally {
      dispatch({ type: 'AUTH_LOADING', payload: false });
    }
  };

  const storeAuth = async (user: User, session: AuthSession) => {
    try {
      // Add created_at timestamp if not present
      const sessionWithTimestamp = {
        ...session,
        created_at: session.created_at || Date.now()
      };
      
      await Promise.all([
        AsyncStorage.setItem(STORAGE_KEYS.USER, JSON.stringify(user)),
        AsyncStorage.setItem(STORAGE_KEYS.SESSION, JSON.stringify(sessionWithTimestamp)),
      ]);
    } catch (error) {
      console.error('Error storing auth data:', error);
    }
  };

  const clearStoredAuth = async () => {
    try {
      await Promise.all([
        AsyncStorage.removeItem(STORAGE_KEYS.USER),
        AsyncStorage.removeItem(STORAGE_KEYS.SESSION),
      ]);
    } catch (error) {
      console.error('Error clearing stored auth:', error);
    }
  };

  const login = async (credentials: LoginRequest) => {
    try {
      dispatch({ type: 'AUTH_START' });

      const response = await authService.login(credentials);
      
      await storeAuth(response.user, response.session);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user: response.user, session: response.session },
      });
    } catch (error) {
      const authError: AuthError = {
        message: error instanceof Error ? error.message : 'Login failed',
        code: 'LOGIN_ERROR',
      };
      dispatch({ type: 'AUTH_FAILURE', payload: authError });
      throw error;
    }
  };

  const register = async (userData: RegisterRequest) => {
    try {
      dispatch({ type: 'AUTH_START' });

      const response = await authService.register(userData);
      
      // User is immediately authenticated after registration
      await storeAuth(response.user, response.session);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user: response.user, session: response.session },
      });
    } catch (error) {
      const authError: AuthError = {
        message: error instanceof Error ? error.message : 'Registration failed',
        code: 'REGISTER_ERROR',
      };
      dispatch({ type: 'AUTH_FAILURE', payload: authError });
      throw error;
    }
  };

  const logout = async () => {
    console.log('🔴 AuthContext: logout called');
    try {
      if (state.session?.access_token) {
        console.log('🔴 AuthContext: Calling authService.logout');
        await authService.logout(state.session.access_token);
        console.log('🔴 AuthContext: authService.logout completed');
      } else {
        console.log('🔴 AuthContext: No access token found');
      }
    } catch (error) {
      console.error('🔴 AuthContext: Logout error:', error);
    } finally {
      console.log('🔴 AuthContext: Clearing stored auth and dispatching logout');
      await clearStoredAuth();
      dispatch({ type: 'AUTH_LOGOUT' });
      console.log('🔴 AuthContext: Logout completed');
    }
  };

  const clearError = () => {
    dispatch({ type: 'AUTH_CLEAR_ERROR' });
  };

  const refreshUser = async () => {
    if (!state.user?.id || !state.session?.access_token) return;

    try {
      dispatch({ type: 'AUTH_LOADING', payload: true });
      
      const user = await authService.getUserProfile(state.user.id, state.session.access_token);
      
      dispatch({
        type: 'AUTH_SUCCESS',
        payload: { user, session: state.session },
      });
    } catch (error) {
      console.error('Error refreshing user:', error);
      // Don't dispatch error for refresh - just keep current state
    } finally {
      dispatch({ type: 'AUTH_LOADING', payload: false });
    }
  };

  const value: AuthContextType = {
    ...state,
    login,
    register,
    logout,
    clearError,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

// Hook to use auth context
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
