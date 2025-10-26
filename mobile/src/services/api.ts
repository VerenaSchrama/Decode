import axios from 'axios';
import { getApiConfig } from '../config/environment';

export const API_BASE_URL = getApiConfig().baseUrl; // Local development server

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30s for RAG processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Global variable to store refresh callback (set by AuthContext)
let refreshTokenCallback: ((refreshToken: string) => Promise<any>) | null = null;

export const setRefreshTokenCallback = (callback: (refreshToken: string) => Promise<any>) => {
  refreshTokenCallback = callback;
};

// Add response interceptor for automatic token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't tried refreshing yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Get the refresh token from AsyncStorage
        const AsyncStorage = require('@react-native-async-storage/async-storage').default;
        const storedSession = await AsyncStorage.getItem('@auth_session');
        
        if (storedSession && refreshTokenCallback) {
          const session = JSON.parse(storedSession);
          
          if (session.refresh_token) {
            console.log('🔄 Token expired, refreshing...');
            
            // Call refresh callback
            const newSession = await refreshTokenCallback(session.refresh_token);
            
            // Update the stored session
            await AsyncStorage.setItem('@auth_session', JSON.stringify({
              ...newSession,
              created_at: Date.now(),
            }));

            // Update the authorization header for the retry
            originalRequest.headers.Authorization = `Bearer ${newSession.access_token}`;
            
            console.log('✅ Token refreshed successfully, retrying request');
            
            // Retry the original request
            return api(originalRequest);
          }
        }
      } catch (refreshError) {
        console.error('❌ Token refresh failed:', refreshError);
        // If refresh fails, redirect to login screen
        // This would require navigation context, so we'll just reject the error
      }
    }

    return Promise.reject(error);
  }
);

// API endpoints
export const endpoints = {
  recommend: '/recommend',
  health: '/health',
  interventions: '/interventions',
  userInsights: (userId: string) => `/user/${userId}/insights`,
  userHabits: (userId: string) => `/user/${userId}/habits`,
  customInterventions: '/admin/custom-interventions',
};

// Health check function
export const checkAPIHealth = async () => {
  try {
    const response = await api.get(endpoints.health);
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
};

// Get recommendations
export const getRecommendations = async (storyIntakeData: any, accessToken?: string) => {
  try {
    // Age is provided directly from registration, no need to calculate
    console.log('📊 Profile data:', {
      name: storyIntakeData.profile.name,
      age: storyIntakeData.profile.age
    });
    
    // Transform the Story Intake data to match your backend's expected format
    const userInput = {
      profile: {
        name: storyIntakeData.profile.name || 'Anonymous',
        age: storyIntakeData.profile.age || 25, // Use age from profile directly
      },
              lastPeriod: storyIntakeData.lastPeriod || null,
              symptoms: {
                selected: storyIntakeData.symptoms.selected || [],
                additional: storyIntakeData.symptoms.additional || '',
              },
              interventions: {
                selected: storyIntakeData.interventions.selected || [],
                additional: storyIntakeData.interventions.additional || '',
              },
              dietaryPreferences: {
                selected: storyIntakeData.dietaryPreferences?.selected || [],
                additional: storyIntakeData.dietaryPreferences?.additional || '',
              },
              consent: storyIntakeData.consent || false,
            };

    console.log('📤 Sending to API:', JSON.stringify(userInput, null, 2));
    console.log('🌐 API URL:', API_BASE_URL + endpoints.recommend);
    
    // Include authentication token if provided
    const headers: any = {
      'Content-Type': 'application/json',
    };
    
    if (accessToken) {
      headers['Authorization'] = `Bearer ${accessToken}`;
      console.log('🔐 Including authentication token');
    }
    
    const response = await api.post(endpoints.recommend, userInput, { headers });
    console.log('✅ API Response received:', response.status);
    return {
      success: true,
      data: response.data,
    };
  } catch (error: any) {
    console.error('❌ API Error Details:', {
      message: error.message,
      code: error.code,
      response: error.response?.data,
      status: error.response?.status,
      statusText: error.response?.statusText,
      config: {
        url: error.config?.url,
        method: error.config?.method,
        baseURL: error.config?.baseURL,
      }
    });
    
    // Extract meaningful error message
    let errorMessage = 'Network Error';
    if (error.code === 'NETWORK_ERROR' || error.message?.includes('Network Error')) {
      errorMessage = 'Network Error - Please check your connection';
    } else if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        errorMessage = error.response.data.detail.map((err: any) => err.msg).join(', ');
      } else {
        errorMessage = error.response.data.detail;
      }
    } else if (error.message) {
      errorMessage = error.message;
    }
    
    return {
      success: false,
      error: errorMessage,
    };
  }
};

// Get user insights
export const getUserInsights = async (userId: string) => {
  try {
    const response = await api.get(endpoints.userInsights(userId));
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
};

// Get user habits
export const getUserHabits = async (userId: string) => {
  try {
    const response = await api.get(endpoints.userHabits(userId));
    return {
      success: true,
      data: response.data,
    };
  } catch (error) {
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
};
