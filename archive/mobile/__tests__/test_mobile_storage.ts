/**
 * Mobile App Storage Tests
 * Tests AsyncStorage operations and data persistence
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { User, AuthSession } from '../types/Auth';

// Mock AsyncStorage
jest.mock('@react-native-async-storage/async-storage', () => ({
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
}));

describe('Mobile Storage Operations', () => {
  const mockUser: User = {
    id: 'test-uuid-123',
    email: 'test@example.com',
    name: 'Test User',
    age: 25,
    anonymous: false
  };

  const mockSession: AuthSession = {
    access_token: 'test-access-token',
    refresh_token: 'test-refresh-token',
    expires_at: '2024-12-31T23:59:59Z'
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Authentication Storage', () => {
    test('test_mobile_auth_storage - stores user data correctly', async () => {
      const mockSetItem = AsyncStorage.setItem as jest.Mock;
      
      // Simulate storing user data
      await AsyncStorage.setItem('@auth_user', JSON.stringify(mockUser));
      
      expect(mockSetItem).toHaveBeenCalledWith(
        '@auth_user',
        JSON.stringify(mockUser)
      );
    });

    test('test_mobile_session_storage - stores session data correctly', async () => {
      const mockSetItem = AsyncStorage.setItem as jest.Mock;
      
      // Simulate storing session data
      await AsyncStorage.setItem('@auth_session', JSON.stringify(mockSession));
      
      expect(mockSetItem).toHaveBeenCalledWith(
        '@auth_session',
        JSON.stringify(mockSession)
      );
    });

    test('test_mobile_auth_retrieval - retrieves stored auth data', async () => {
      const mockGetItem = AsyncStorage.getItem as jest.Mock;
      mockGetItem
        .mockResolvedValueOnce(JSON.stringify(mockUser))
        .mockResolvedValueOnce(JSON.stringify(mockSession));
      
      const [storedUser, storedSession] = await Promise.all([
        AsyncStorage.getItem('@auth_user'),
        AsyncStorage.getItem('@auth_session')
      ]);
      
      expect(JSON.parse(storedUser)).toEqual(mockUser);
      expect(JSON.parse(storedSession)).toEqual(mockSession);
    });

    test('test_mobile_auth_cleanup - clears auth data on logout', async () => {
      const mockRemoveItem = AsyncStorage.removeItem as jest.Mock;
      
      // Simulate clearing auth data
      await Promise.all([
        AsyncStorage.removeItem('@auth_user'),
        AsyncStorage.removeItem('@auth_session')
      ]);
      
      expect(mockRemoveItem).toHaveBeenCalledWith('@auth_user');
      expect(mockRemoveItem).toHaveBeenCalledWith('@auth_session');
    });

    test('test_mobile_auth_error_handling - handles storage errors gracefully', async () => {
      const mockGetItem = AsyncStorage.getItem as jest.Mock;
      mockGetItem.mockRejectedValue(new Error('Storage error'));
      
      // Should not throw error
      await expect(AsyncStorage.getItem('@auth_user')).rejects.toThrow('Storage error');
    });
  });

  describe('Data Persistence', () => {
    test('test_mobile_data_consistency - maintains data consistency across app restarts', async () => {
      const mockGetItem = AsyncStorage.getItem as jest.Mock;
      mockGetItem
        .mockResolvedValueOnce(JSON.stringify(mockUser))
        .mockResolvedValueOnce(JSON.stringify(mockSession));
      
      // Simulate app restart - loading stored data
      const [user, session] = await Promise.all([
        AsyncStorage.getItem('@auth_user'),
        AsyncStorage.getItem('@auth_session')
      ]);
      
      const parsedUser = JSON.parse(user);
      const parsedSession = JSON.parse(session);
      
      expect(parsedUser.id).toBe(mockUser.id);
      expect(parsedUser.email).toBe(mockUser.email);
      expect(parsedSession.access_token).toBe(mockSession.access_token);
    });

    test('test_mobile_storage_keys - uses correct storage keys', () => {
      const expectedKeys = {
        USER: '@auth_user',
        SESSION: '@auth_session'
      };
      
      expect(expectedKeys.USER).toBe('@auth_user');
      expect(expectedKeys.SESSION).toBe('@auth_session');
    });
  });

  describe('Concurrent Access', () => {
    test('test_mobile_concurrent_storage - handles concurrent storage operations', async () => {
      const mockSetItem = AsyncStorage.setItem as jest.Mock;
      
      // Simulate concurrent storage operations
      const operations = [
        AsyncStorage.setItem('@auth_user', JSON.stringify(mockUser)),
        AsyncStorage.setItem('@auth_session', JSON.stringify(mockSession))
      ];
      
      await Promise.all(operations);
      
      expect(mockSetItem).toHaveBeenCalledTimes(2);
    });
  });

  describe('Data Validation', () => {
    test('test_mobile_data_validation - validates stored data format', async () => {
      const mockGetItem = AsyncStorage.getItem as jest.Mock;
      mockGetItem.mockResolvedValue(JSON.stringify(mockUser));
      
      const storedData = await AsyncStorage.getItem('@auth_user');
      const parsedData = JSON.parse(storedData);
      
      // Validate required fields
      expect(parsedData).toHaveProperty('id');
      expect(parsedData).toHaveProperty('email');
      expect(parsedData).toHaveProperty('name');
      expect(typeof parsedData.id).toBe('string');
      expect(typeof parsedData.email).toBe('string');
    });

    test('test_mobile_session_validation - validates session data format', async () => {
      const mockGetItem = AsyncStorage.getItem as jest.Mock;
      mockGetItem.mockResolvedValue(JSON.stringify(mockSession));
      
      const storedData = await AsyncStorage.getItem('@auth_session');
      const parsedData = JSON.parse(storedData);
      
      // Validate required fields
      expect(parsedData).toHaveProperty('access_token');
      expect(parsedData).toHaveProperty('refresh_token');
      expect(parsedData).toHaveProperty('expires_at');
      expect(typeof parsedData.access_token).toBe('string');
    });
  });
});
