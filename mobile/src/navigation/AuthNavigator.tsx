import React, { useState } from 'react';
import { createStackNavigator } from '@react-navigation/stack';
import LoginScreen from '../screens/LoginScreen';
import RegisterScreen from '../screens/RegisterScreen';

export type AuthStackParamList = {
  Login: undefined;
  Register: undefined;
};

const Stack = createStackNavigator<AuthStackParamList>();

interface AuthNavigatorProps {
  onLoginSuccess: () => void;
  onRegisterSuccess: () => void;
}

export default function AuthNavigator({ onLoginSuccess, onRegisterSuccess }: AuthNavigatorProps) {
  console.log('AuthNavigator: Props received:', { onLoginSuccess: !!onLoginSuccess, onRegisterSuccess: !!onRegisterSuccess });
  
  const [currentScreen, setCurrentScreen] = useState<'login' | 'register'>('login');

  const handleNavigateToRegister = () => {
    setCurrentScreen('register');
  };

  const handleNavigateToLogin = () => {
    setCurrentScreen('login');
  };

  const handleLoginSuccess = () => {
    onLoginSuccess();
  };

  const handleRegisterSuccess = () => {
    console.log('AuthNavigator: handleRegisterSuccess called');
    console.log('AuthNavigator: calling onRegisterSuccess...');
    onRegisterSuccess();
    console.log('AuthNavigator: onRegisterSuccess called');
  };

  return (
    <>
      {currentScreen === 'login' ? (
        <LoginScreen
          onNavigateToRegister={handleNavigateToRegister}
          onLoginSuccess={handleLoginSuccess}
        />
      ) : (
        <RegisterScreen
          onNavigateToLogin={handleNavigateToLogin}
          onRegisterSuccess={handleRegisterSuccess}
        />
      )}
    </>
  );
}
