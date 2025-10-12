import React, { useState } from 'react';
import { View, Text } from 'react-native';
import { StoryIntakeData } from '../types/StoryIntake';
import TestScreen from '../screens/TestScreen';
import StoryIntakeScreen from '../screens/StoryIntakeScreen';
import ThankYouScreen from '../screens/ThankYouScreen';
import RecommendationsScreen from '../screens/RecommendationsScreen';
import HabitSelectionScreen from '../screens/HabitSelectionScreen';
import MainAppScreen from '../screens/MainAppScreen';

export type AppScreen = 'test' | 'story-intake' | 'thank-you' | 'recommendations' | 'habit-selection' | 'main-app';

interface AppNavigatorProps {
  currentScreen: AppScreen;
  onScreenChange: (screen: AppScreen) => void;
  intakeData?: StoryIntakeData;
  onIntakeComplete: (data: StoryIntakeData) => void;
  selectedHabits?: string[];
  onHabitsSelected?: (habits: string[]) => void;
  currentIntervention?: any;
  onInterventionSelected?: (intervention: any) => void;
}

export default function AppNavigator({
  currentScreen,
  onScreenChange,
  intakeData,
  onIntakeComplete,
  selectedHabits,
  onHabitsSelected,
  currentIntervention,
  onInterventionSelected,
}: AppNavigatorProps) {
  const handleStoryIntakeComplete = (data: StoryIntakeData) => {
    onIntakeComplete(data);
    onScreenChange('thank-you');
  };

  const handleViewRecommendations = () => {
    onScreenChange('recommendations');
  };

  const handleBackToIntake = () => {
    onScreenChange('story-intake');
  };

  const handleHabitsSelected = (habits: string[]) => {
    onHabitsSelected?.(habits);
    onScreenChange('habit-selection');
  };

  const handleStartMainApp = (habits: string[]) => {
    onHabitsSelected?.(habits);
    onScreenChange('main-app');
  };

  const handleBackToRecommendations = () => {
    onScreenChange('recommendations');
  };

  const handleInterventionSelected = (intervention: any, periodData: {
    durationDays: number;
    startDate: string;
    endDate: string;
  }) => {
    // Store intervention and period data for the main app
    console.log('Intervention selected:', intervention.name);
    console.log('Period data:', periodData);
    
    // Store the current intervention
    onInterventionSelected?.(intervention);
    
    // Extract habits from the selected intervention
    const interventionHabits = intervention.habits?.map((habit: any) => habit.description) || [];
    console.log('Intervention habits:', interventionHabits);
    
    // Pass the habits to the habit selection screen
    onHabitsSelected?.(interventionHabits);
    onScreenChange('habit-selection');
  };

  switch (currentScreen) {
    case 'test':
      return <TestScreen />;
    
    case 'story-intake':
      return (
        <StoryIntakeScreen
          onComplete={handleStoryIntakeComplete}
        />
      );
    
    case 'thank-you':
      return (
        <ThankYouScreen
          onViewRecommendations={handleViewRecommendations}
          intakeData={intakeData}
        />
      );
    
    case 'recommendations':
      return (
        <RecommendationsScreen
          intakeData={intakeData!}
          onBack={handleBackToIntake}
          onHabitsSelected={handleHabitsSelected}
          onInterventionSelected={handleInterventionSelected}
        />
      );
    
    case 'habit-selection':
      return (
        <HabitSelectionScreen
          recommendedHabits={selectedHabits || []}
          onHabitsSelected={handleStartMainApp}
          onBack={handleBackToRecommendations}
        />
      );
    
    case 'main-app':
      return (
        <MainAppScreen 
          selectedHabits={selectedHabits || []}
          intakeData={intakeData}
          currentIntervention={currentIntervention}
        />
      );
    
    default:
      return <TestScreen />;
  }
}

