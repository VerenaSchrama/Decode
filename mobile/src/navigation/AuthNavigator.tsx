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
    onRegisterSuccess();
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
