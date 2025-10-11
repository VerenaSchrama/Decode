/**
 * Environment Configuration
 * Centralized configuration for different environments (development, staging, production)
 */

export interface ApiConfig {
  baseUrl: string;
  timeout: number;
  retryAttempts: number;
}

export const API_CONFIG = {
  development: {
    baseUrl: 'http://localhost:8000',
    timeout: 10000, // 10 seconds
    retryAttempts: 3,
  },
  production: {
    baseUrl: 'http://65.108.149.135',  // Reverted to HTTP temporarily
    timeout: 15000,
    retryAttempts: 2,
  },
  staging: {
    baseUrl: 'http://65.108.149.135', // Same as production for now
    timeout: 12000, // 12 seconds
    retryAttempts: 3,
  }
};

/**
 * Get the current environment
 */
const getEnvironment = (): keyof typeof API_CONFIG => {
  // Check if we're in development mode
  if (typeof window !== 'undefined' && window.location.hostname === 'localhost') {
    return 'development';
  }
  
  // Check Vercel environment variables
  if (process.env.NEXT_PUBLIC_ENV === 'staging') return 'staging';
  if (process.env.NEXT_PUBLIC_ENV === 'production') return 'production';
  if (process.env.VERCEL_ENV === 'production') return 'production';
  if (process.env.VERCEL_ENV === 'preview') return 'staging';
  
  // Default to production for Vercel deployments
  return 'production';
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
