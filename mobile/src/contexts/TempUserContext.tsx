import React, { createContext, useContext, useState, ReactNode } from 'react';
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

export function TempUserProvider({ children }: TempUserProviderProps) {
  const [tempUser, setTempUser] = useState<TempUser | null>(null);

  const clearTempUser = () => {
    setTempUser(null);
  };

  return (
    <TempUserContext.Provider value={{ tempUser, setTempUser, clearTempUser }}>
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
