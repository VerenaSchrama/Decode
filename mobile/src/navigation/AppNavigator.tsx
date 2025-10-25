import React, { useState } from 'react';
import { View, Text, Alert } from 'react-native';
import { StoryIntakeData } from '../types/StoryIntake';
import TestScreen from '../screens/TestScreen';
import StoryIntakeScreen from '../screens/StoryIntakeScreen';
import ThankYouScreen from '../screens/ThankYouScreen';
import RecommendationsScreen from '../screens/RecommendationsScreen';
import HabitSelectionScreen from '../screens/HabitSelectionScreen';
import MainAppScreen from '../screens/MainAppScreen';
import { interventionPeriodService } from '../services/interventionPeriodService';
import { useAuth } from '../contexts/AuthContext';

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
  const { session } = useAuth();
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

  const handleInterventionSelected = async (intervention: any, periodData: {
    durationDays: number;
    startDate: string;
    endDate: string;
  }) => {
    // Store intervention and period data for the main app
    console.log('Intervention selected:', intervention.name);
    console.log('Period data:', periodData);
    
    // Check if user is properly authenticated
    if (!session?.access_token) {
      console.error('❌ User not authenticated - cannot start intervention period');
      Alert.alert(
        'Authentication Required',
        'Please log in to start tracking your intervention.',
        [{ text: 'OK' }]
      );
      return;
    }
    
    // Store the current intervention
    onInterventionSelected?.(intervention);
    
    // Extract habits from the selected intervention
    const interventionHabits = intervention.habits?.map((habit: any) => habit.description) || [];
    console.log('Intervention habits:', interventionHabits);
    
    // Start tracking intervention period if user is authenticated
    if (session?.access_token && intakeData) {
      try {
        const startRequest = {
          intake_id: intakeData.intake_id || intakeData.id || 'temp-intake-id', // Use intake ID if available
          intervention_name: intervention.name,
          selected_habits: interventionHabits,
          intervention_id: intervention.id,
          planned_duration_days: periodData.durationDays,
          cycle_phase: intakeData.lastPeriod?.cyclePhase || 'follicular'
        };
        
        const result = await interventionPeriodService.startInterventionPeriod(
          startRequest,
          session.access_token
        );
        
        if (result.success) {
          console.log('✅ Intervention period tracking started:', result.period_id);
        } else {
          console.error('❌ Failed to start intervention period tracking:', result.error);
          // Show user-friendly error message
          Alert.alert(
            'Tracking Error',
            'Failed to start tracking your intervention. Please try again or contact support.',
            [{ text: 'OK' }]
          );
          return; // Don't continue to habit selection if tracking fails
        }
      } catch (error) {
        console.error('❌ Error starting intervention period tracking:', error);
      }
    } else {
      console.log('ℹ️ Skipping intervention period tracking - no session or intake data');
    }
    
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

