/**
 * Environment Configuration
 * Centralized configuration for different environments (development, staging, production)
 */

export interface ApiConfig {
  baseUrl: string;
  apiKey: string;
  timeout: number;
  retryAttempts: number;
}

export const API_CONFIG = {
  development: {
    baseUrl: 'http://localhost:8000',
    apiKey: 'dev-key-123', // For development only
    timeout: 10000, // 10 seconds
    retryAttempts: 3,
  },
  production: {
    baseUrl: 'https://your-production-api.com',
    apiKey: process.env.EXPO_PUBLIC_API_KEY || '',
    timeout: 15000, // 15 seconds
    retryAttempts: 2,
  },
  staging: {
    baseUrl: 'https://your-staging-api.com',
    apiKey: process.env.EXPO_PUBLIC_STAGING_API_KEY || '',
    timeout: 12000, // 12 seconds
    retryAttempts: 3,
  }
};

/**
 * Get the current environment
 */
const getEnvironment = (): keyof typeof API_CONFIG => {
  if (__DEV__) return 'development';
  if (process.env.EXPO_PUBLIC_ENV === 'staging') return 'staging';
  if (process.env.EXPO_PUBLIC_ENV === 'production') return 'production';
  return 'development'; // Default to development
};

/**
 * Get API configuration for current environment
 */
export const getApiConfig = (): ApiConfig => {
  const env = getEnvironment();
  const config = API_CONFIG[env];
  
  // Validate configuration
  if (!config.baseUrl) {
    throw new Error(`Missing baseUrl for environment: ${env}`);
  }
  
  return config;
};

/**
 * Get current environment name
 */
export const getCurrentEnvironment = (): string => {
  return getEnvironment();
};

/**
 * Check if we're in development mode
 */
export const isDevelopment = (): boolean => {
  return getEnvironment() === 'development';
};

/**
 * Check if we're in production mode
 */
export const isProduction = (): boolean => {
  return getEnvironment() === 'production';
};
