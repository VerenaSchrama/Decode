import React, { useState, useEffect } from 'react';
import { StatusBar } from 'expo-status-bar';
import { View, TouchableOpacity, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import AppNavigator, { AppScreen } from './src/navigation/AppNavigator';
import AuthNavigator from './src/navigation/AuthNavigator';
import EmailConfirmationScreen from './src/screens/EmailConfirmationScreen';
import EmailConfirmedScreen from './src/screens/EmailConfirmedScreen';
import { StoryIntakeData } from './src/types/StoryIntake';
import { colors } from './src/constants/colors';
import { ToastProvider, useToast } from './src/contexts/ToastContext';
import { AuthProvider, useAuth } from './src/contexts/AuthContext';
import { TempUserProvider } from './src/contexts/TempUserContext';

// Main App Component with Authentication
function AppContent() {
  const { isAuthenticated, isLoading, emailConfirmationRequired, user, clearEmailConfirmation } = useAuth();
  const toast = useToast();
  console.log('AppContent: Auth state:', { isAuthenticated, isLoading, emailConfirmationRequired, user: user?.email });
  const [currentScreen, setCurrentScreen] = useState<AppScreen>('test');
  const [intakeData, setIntakeData] = useState<StoryIntakeData | undefined>();
  const [selectedHabits, setSelectedHabits] = useState<string[]>([]);
  const [currentIntervention, setCurrentIntervention] = useState<any>(undefined);
  const [isNewRegistration, setIsNewRegistration] = useState(false);

  const handleScreenChange = (screen: AppScreen) => {
    setCurrentScreen(screen);
  };

  const handleIntakeComplete = (data: StoryIntakeData) => {
    setIntakeData(data);
  };

  const handleHabitsSelected = (habits: string[]) => {
    setSelectedHabits(habits);
  };

  const handleInterventionSelected = (intervention: any) => {
    setCurrentIntervention(intervention);
  };

  const handleLoginSuccess = () => {
    // Returning users go directly to main app
    setIsNewRegistration(false);
    setCurrentScreen('main-app');
  };

  const handleRegisterSuccess = () => {
    console.log('handleRegisterSuccess called');
    console.log('Current screen before:', currentScreen);
    // New users go to story intake
    setIsNewRegistration(true);
    setCurrentScreen('story-intake');
    console.log('Current screen after:', 'story-intake');
    console.log('isNewRegistration set to:', true);
  };

  // Handle initial routing when user is already authenticated
  useEffect(() => {
    if (isAuthenticated && !isLoading) {
      // Only auto-route if this is NOT a new registration
      // New registrations are handled by handleRegisterSuccess()
      if (!isNewRegistration) {
        // If user is already authenticated (returning user), go to main app
        setCurrentScreen('main-app');
      } else {
        // If this is a new registration that just completed email verification,
        // go to recommendations instead of main app
        setCurrentScreen('recommendations');
        setIsNewRegistration(false); // Reset the flag
      }
    }
  }, [isAuthenticated, isLoading, isNewRegistration]);

  // Show loading screen while checking authentication
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={colors.primary} />
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  // Show email confirmation screen if email confirmation is required
  if (emailConfirmationRequired) {
    return (
      <View style={styles.container}>
        <EmailConfirmationScreen 
          email={user?.email}
          onResendEmail={async () => {
            try {
              console.log('Resending confirmation email to:', user?.email);
              // Call the backend API to resend confirmation email
              const response = await fetch('https://api.decode-app.nl/auth/resend-confirmation', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                },
                body: JSON.stringify({ email: user?.email }),
              });
              
              if (response.ok) {
                console.log('Confirmation email resent successfully');
                toast.showToast('Confirmation email sent! Please check your inbox.', 'success');
              } else {
                console.error('Failed to resend confirmation email');
                toast.showToast('Failed to resend email. Please try again.', 'error');
              }
            } catch (error) {
              console.error('Error resending confirmation email:', error);
              toast.showToast('Network error. Please check your connection and try again.', 'error');
            }
          }}
          onBackToLogin={() => {
            // Reset email confirmation state and go back to login
            console.log('Going back to login');
            clearEmailConfirmation();
            setCurrentScreen('test');
          }}
        />
        <StatusBar style="auto" />
      </View>
    );
  }

  // Show authentication screens if not authenticated AND not in new registration flow AND not requiring email confirmation
  if (!isAuthenticated && !isNewRegistration && !emailConfirmationRequired) {
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
  console.log('Rendering AppNavigator with currentScreen:', currentScreen);
  return (
    <View style={styles.container}>
      <AppNavigator
        currentScreen={currentScreen}
        onScreenChange={handleScreenChange}
        intakeData={intakeData}
        onIntakeComplete={handleIntakeComplete}
        selectedHabits={selectedHabits}
        onHabitsSelected={handleHabitsSelected}
        currentIntervention={currentIntervention}
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
      <TempUserProvider>
        <ToastProvider>
          <NavigationContainer>
            <AppContent />
          </NavigationContainer>
        </ToastProvider>
      </TempUserProvider>
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
