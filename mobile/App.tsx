import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { View, TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import AppNavigator, { AppScreen } from './src/navigation/AppNavigator';
import AuthNavigator from './src/navigation/AuthNavigator';
import { StoryIntakeData } from './src/types/StoryIntake';
import { colors } from './src/constants/colors';
import { ToastProvider, useToast } from './src/contexts/ToastContext';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { AppStateProvider, useAppState } from './src/contexts/AppStateContext';
import SessionService from './src/services/sessionService';

// Main App Component with Authentication
function AppContent() {
  const { isAuthenticated, isLoading, user } = useAuth();
  const toast = useToast();
  // ✅ Use AppStateContext instead of local useState
  const { state, updateIntakeData, updateSelectedHabits, updateCurrentIntervention, updateCurrentScreen } = useAppState();
  console.log('AppContent: Auth state:', { isAuthenticated, isLoading });
  const [isNewRegistration, setIsNewRegistration] = useState(false);
  const [isLoadingSession, setIsLoadingSession] = useState(false);

  const handleScreenChange = (screen: AppScreen) => {
    // ✅ Update screen in AppStateContext
    updateCurrentScreen(screen);
  };

  const handleIntakeComplete = (data: StoryIntakeData) => {
    console.log('🔍 DEBUG App.tsx: handleIntakeComplete called with data:', JSON.stringify(data, null, 2));
    console.log('🔍 DEBUG App.tsx: intake_id in data:', data.intake_id);
    // ✅ Update intake data in AppStateContext
    updateIntakeData(data);
  };

  const handleHabitsSelected = (habits: string[]) => {
    // ✅ Update habits in AppStateContext
    updateSelectedHabits(habits);
  };

  const handleInterventionSelected = (intervention: any) => {
    // ✅ Update intervention in AppStateContext
    updateCurrentIntervention(intervention);
  };

  const loadUserSessionData = async () => {
    if (!user?.id) return;
    
    try {
      setIsLoadingSession(true);
      console.log('🔄 AppContent: Loading user session data for:', user.id);
      
      const sessionData = await SessionService.restoreUserSession(user.id);
      
      if (sessionData) {
        console.log('✅ AppContent: Session data loaded:', sessionData);
        
        // ✅ Restore intake data using AppStateContext
        if (sessionData.intake_data) {
          updateIntakeData(sessionData.intake_data as unknown as StoryIntakeData);
        }
        
        // ✅ Restore current intervention using AppStateContext
        if (sessionData.current_intervention) {
          updateCurrentIntervention(sessionData.current_intervention);
        }
        
        // ✅ Restore selected habits using AppStateContext
        if (sessionData.selected_habits && sessionData.selected_habits.length > 0) {
          updateSelectedHabits(sessionData.selected_habits);
        }
        
        console.log('✅ AppContent: User session restored successfully');
        toast.showToast('Welcome back! Your data has been restored.', 'success');
      } else {
        console.log('ℹ️ AppContent: No existing session data found');
      }
    } catch (error) {
      console.error('❌ AppContent: Error loading session data:', error);
      toast.showToast('Failed to load your data. Please try again.', 'error');
    } finally {
      setIsLoadingSession(false);
    }
  };

  const handleLoginSuccess = async () => {
    // Returning users go directly to main app
    setIsNewRegistration(false);
    
    // Load user session data before navigating
    await loadUserSessionData();
    
    // ✅ Update screen using AppStateContext
    updateCurrentScreen('main-app');
  };

  const handleRegisterSuccess = () => {
    console.log('handleRegisterSuccess called');
    console.log('Current screen before:', state.currentScreen);
    // New users go to story intake
    setIsNewRegistration(true);
    // ✅ Update screen using AppStateContext
    updateCurrentScreen('story-intake');
    console.log('Current screen after:', 'story-intake');
    console.log('isNewRegistration set to:', true);
  };

  // Handle initial routing when user is already authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading && user?.id) {
      // Only auto-route if this is NOT a new registration
      // New registrations are handled by handleRegisterSuccess()
      if (!isNewRegistration) {
        // If user is already authenticated (returning user), load session data and go to main app
        loadUserSessionData().then(() => {
          // ✅ Update screen using AppStateContext
          updateCurrentScreen('main-app');
        });
      }
      // If isNewRegistration is true, don't override the screen set by handleRegisterSuccess
    }
  }, [isAuthenticated, isLoading, isNewRegistration, user?.id]);

  // Show loading screen while checking authentication or loading session
  if (isLoading || isLoadingSession) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>
          {isLoading ? 'Loading...' : 'Restoring your data...'}
        </Text>
      </View>
    );
  }

  // Show authentication screens if not authenticated
  if (!isAuthenticated) {
    return (
      <View style={styles.container}>
        <AuthNavigator 
          onLoginSuccess={handleLoginSuccess}
          onRegisterSuccess={handleRegisterSuccess}
        />
        <StatusBar style="auto" />
      </View>
    );
  }

  // Show main app if authenticated
  // ✅ Use state from AppStateContext instead of local state
  console.log('Rendering AppNavigator with currentScreen:', state.currentScreen);
  return (
    <View style={styles.container}>
      <AppNavigator
        currentScreen={state.currentScreen}
        onScreenChange={handleScreenChange}
        intakeData={state.intakeData}
        onIntakeComplete={handleIntakeComplete}
        selectedHabits={state.selectedHabits}
        onHabitsSelected={handleHabitsSelected}
        currentIntervention={state.currentIntervention}
        onInterventionSelected={handleInterventionSelected}
      />
      
      <StatusBar style="auto" />
    </View>
  );
}

// Main App Export with Providers
export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <AppStateProvider>
          <NavigationContainer>
            <AppContent />
          </NavigationContainer>
        </AppStateProvider>
      </ToastProvider>
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#6B7280',
  },
});
