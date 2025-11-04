/**
 * Global Token Refresh Manager
 * 
 * Prevents concurrent refresh attempts across axios and fetch-based API calls.
 * Supabase refresh tokens are single-use (rotation), so concurrent refreshes
 * with the same token will cause "Already Used" errors.
 * 
 * This manager ensures only ONE refresh happens at a time globally.
 */

let isRefreshing = false;
let refreshPromise: Promise<any> | null = null;
let refreshTokenCallback: ((refreshToken: string) => Promise<any>) | null = null;

/**
 * Set the refresh token callback (called by AuthContext)
 */
export function setRefreshTokenCallback(callback: ((refreshToken: string) => Promise<any>) | null) {
  refreshTokenCallback = callback;
}

/**
 * Perform token refresh with global lock
 * 
 * If a refresh is already in progress, waits for it instead of starting a new one.
 * This prevents "Already Used" errors from concurrent refresh attempts.
 * 
 * @returns Promise resolving to new session with fresh tokens
 */
export async function performTokenRefresh(): Promise<any> {
  // If refresh is already in progress, wait for it
  if (isRefreshing && refreshPromise) {
    console.log('⏳ Global refresh already in progress, waiting...');
    return refreshPromise;
  }

  // Start new refresh
  isRefreshing = true;
  
  const AsyncStorage = require('@react-native-async-storage/async-storage').default;
  
  refreshPromise = (async () => {
    try {
      // Get refresh token from storage
      const storedSession = await AsyncStorage.getItem('@auth_session');
      
      if (!storedSession) {
        throw new Error('No stored session found');
      }
      
      const session = JSON.parse(storedSession);
      
      if (!session.refresh_token) {
        throw new Error('No refresh token available');
      }
      
      if (!refreshTokenCallback) {
        throw new Error('No refresh token callback registered');
      }
      
      console.log('🔄 Performing global token refresh...');
      
      // Call refresh callback (registered by AuthContext)
      const newSession = await refreshTokenCallback(session.refresh_token);
      
      // Save new session immediately (critical for token rotation)
      await AsyncStorage.setItem('@auth_session', JSON.stringify({
        ...newSession,
        created_at: Date.now(),
      }));
      
      console.log('✅ Global token refresh completed and saved');
      
      return newSession;
    } catch (error) {
      console.error('❌ Global token refresh failed:', error);
      throw error;
    } finally {
      isRefreshing = false;
      refreshPromise = null;
    }
  })();
  
  return refreshPromise;
}

/**
 * Check if a refresh is currently in progress
 */
export function isRefreshInProgress(): boolean {
  return isRefreshing;
}

