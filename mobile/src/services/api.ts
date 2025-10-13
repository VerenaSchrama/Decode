import axios from 'axios';

// API configuration
import { getApiConfig } from '../config/environment';

const API_BASE_URL = getApiConfig().baseUrl; // Local development server

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

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
    // Calculate age from date of birth
    const calculateAge = (dateOfBirth: string) => {
      if (!dateOfBirth || dateOfBirth.trim() === '') return 25; // Default age
      
      const today = new Date();
      const birthDate = new Date(dateOfBirth);
      
      // Check if the date is valid
      if (isNaN(birthDate.getTime())) {
        console.warn('Invalid date of birth provided:', dateOfBirth);
        return 25; // Default age for invalid dates
      }
      
      let age = today.getFullYear() - birthDate.getFullYear();
      const monthDiff = today.getMonth() - birthDate.getMonth();
      if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
      }
      
      // Ensure age is within reasonable bounds
      if (age < 13 || age > 120) {
        console.warn('Calculated age out of bounds:', age, 'using default');
        return 25;
      }
      
      return age;
    };

            // Transform the Story Intake data to match your backend's expected format
            const calculatedAge = calculateAge(storyIntakeData.profile.dateOfBirth);
            console.log('📊 Age calculation:', {
              dateOfBirth: storyIntakeData.profile.dateOfBirth,
              calculatedAge: calculatedAge
            });
            
            const userInput = {
              profile: {
                name: storyIntakeData.profile.name || 'Anonymous',
                age: calculatedAge,
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
