import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { TempUser } from '../types/Auth';

interface TempUserContextType {
  tempUser: TempUser | null;
  setTempUser: (user: TempUser | null) => void;
  clearTempUser: () => void;
}

const TempUserContext = createContext<TempUserContextType | undefined>(undefined);

interface TempUserProviderProps {
  children: ReactNode;
}

const TEMP_USER_STORAGE_KEY = 'temp_user_data';

export function TempUserProvider({ children }: TempUserProviderProps) {
  const [tempUser, setTempUser] = useState<TempUser | null>(null);
  const [isLoaded, setIsLoaded] = useState(false);

  // Load temp user data from storage on mount
  useEffect(() => {
    const loadTempUser = async () => {
      try {
        const stored = await AsyncStorage.getItem(TEMP_USER_STORAGE_KEY);
        if (stored) {
          const parsedUser = JSON.parse(stored);
          console.log('TempUserContext: Loaded temp user from storage:', parsedUser);
          setTempUser(parsedUser);
        }
      } catch (error) {
        console.error('TempUserContext: Error loading temp user:', error);
      } finally {
        setIsLoaded(true);
      }
    };
    loadTempUser();
  }, []);

  const setTempUserWithStorage = async (user: TempUser | null) => {
    console.log('TempUserContext: Setting temp user:', user);
    setTempUser(user);
    
    try {
      if (user) {
        await AsyncStorage.setItem(TEMP_USER_STORAGE_KEY, JSON.stringify(user));
        console.log('TempUserContext: Stored temp user to storage');
      } else {
        await AsyncStorage.removeItem(TEMP_USER_STORAGE_KEY);
        console.log('TempUserContext: Removed temp user from storage');
      }
    } catch (error) {
      console.error('TempUserContext: Error storing temp user:', error);
    }
  };

  const clearTempUser = async () => {
    console.log('TempUserContext: Clearing temp user');
    setTempUser(null);
    try {
      await AsyncStorage.removeItem(TEMP_USER_STORAGE_KEY);
      console.log('TempUserContext: Cleared temp user from storage');
    } catch (error) {
      console.error('TempUserContext: Error clearing temp user:', error);
    }
  };

  return (
    <TempUserContext.Provider value={{ 
      tempUser, 
      setTempUser: setTempUserWithStorage, 
      clearTempUser 
    }}>
      {children}
    </TempUserContext.Provider>
  );
}

export const useTempUser = () => {
  const context = useContext(TempUserContext);
  if (context === undefined) {
    throw new Error('useTempUser must be used within a TempUserProvider');
  }
  return context;
};
