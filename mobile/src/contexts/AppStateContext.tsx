import React, { createContext, useContext, useState, useCallback } from 'react';
import { StoryIntakeData } from '../types/StoryIntake';

interface AppState {
  intakeData: StoryIntakeData | undefined;
  selectedHabits: string[];
  currentIntervention: any;
  currentScreen: 'test' | 'story-intake' | 'thank-you' | 'recommendations' | 'habit-selection' | 'main-app';
}

interface AppStateContextType {
  state: AppState;
  updateIntakeData: (data: StoryIntakeData) => void;
  updateSelectedHabits: (habits: string[]) => void;
  updateCurrentIntervention: (intervention: any) => void;
  updateCurrentScreen: (screen: AppState['currentScreen']) => void;
  resetAppState: () => void;
}

const initialState: AppState = {
  intakeData: undefined,
  selectedHabits: [],
  currentIntervention: undefined,
  currentScreen: 'test',
};

const AppStateContext = createContext<AppStateContextType | undefined>(undefined);

export function AppStateProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AppState>(initialState);

  const updateIntakeData = useCallback((data: StoryIntakeData) => {
    setState(prev => ({ ...prev, intakeData: data }));
  }, []);

  const updateSelectedHabits = useCallback((habits: string[]) => {
    setState(prev => ({ ...prev, selectedHabits: habits }));
  }, []);

  const updateCurrentIntervention = useCallback((intervention: any) => {
    setState(prev => ({ ...prev, currentIntervention: intervention }));
  }, []);

  const updateCurrentScreen = useCallback((screen: AppState['currentScreen']) => {
    setState(prev => ({ ...prev, currentScreen: screen }));
  }, []);

  const resetAppState = useCallback(() => {
    setState(initialState);
  }, []);

  return (
    <AppStateContext.Provider
      value={{
        state,
        updateIntakeData,
        updateSelectedHabits,
        updateCurrentIntervention,
        updateCurrentScreen,
        resetAppState,
      }}
    >
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context) {
    throw new Error('useAppState must be used within AppStateProvider');
  }
  return context;
}

