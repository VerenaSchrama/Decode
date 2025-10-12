/**
 * Environment Variables Example
 * Copy this file to env.ts and update the values for your environment
 */

export const ENV_VARS = {
  // Current environment (development, staging, production)
  ENV: 'development',
  
  // API Keys for different environments
  API_KEY: 'dev-key-123',
  STAGING_API_KEY: 'staging-key-123',
  PRODUCTION_API_KEY: 'production-key-123',
  
  // API URLs (optional - can be overridden in environment.ts)
  API_URL_DEV: 'http://192.168.3.107:8000',
  API_URL_STAGING: 'https://your-staging-api.com',
  API_URL_PRODUCTION: 'https://your-production-api.com',
  
  // Debug settings
  DEBUG: true,
  LOG_LEVEL: 'debug',
};
