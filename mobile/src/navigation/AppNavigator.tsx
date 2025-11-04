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
import { useAppState } from '../contexts/AppStateContext';
import { getApiConfig } from '../config/environment';

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
  // ✅ Get AppStateContext functions at component level (hooks must be called at top level)
  const { updateIntakeData, updateSelectedHabits, updateCurrentScreen, updateCurrentIntervention } = useAppState();
  
  const handleStoryIntakeComplete = (data: StoryIntakeData) => {
    // ✅ Update intake data in AppStateContext (no setTimeout needed!)
    updateIntakeData(data);
    // ✅ Update screen immediately - state is already updated
    updateCurrentScreen('thank-you');
    // Still call the callback for backward compatibility
    onIntakeComplete(data);
    onScreenChange('thank-you');
  };

  const handleViewRecommendations = () => {
    updateCurrentScreen('recommendations');
    onScreenChange('recommendations');
  };

  const handleBackToIntake = () => {
    updateCurrentScreen('story-intake');
    onScreenChange('story-intake');
  };

  const handleHabitsSelected = (habits: string[]) => {
    // ✅ Update habits in AppStateContext
    updateSelectedHabits(habits);
    // Callbacks for backward compatibility
    onHabitsSelected?.(habits);
    updateCurrentScreen('habit-selection');
    onScreenChange('habit-selection');
  };

  const handleStartMainApp = (habits: string[]) => {
    // ✅ Update habits in AppStateContext
    updateSelectedHabits(habits);
    // Callbacks for backward compatibility
    onHabitsSelected?.(habits);
    updateCurrentScreen('main-app');
    onScreenChange('main-app');
  };

  const handleBackToRecommendations = () => {
    updateCurrentScreen('recommendations');
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
    
    // ✅ Store the current intervention in AppStateContext
    updateCurrentIntervention(intervention);
    // Callback for backward compatibility
    onInterventionSelected?.(intervention);
    
    // Extract habits from the selected intervention
    const interventionHabits = intervention.habits?.map((habit: any) => habit.description) || [];
    console.log('Intervention habits:', interventionHabits);
    
    // Start tracking intervention period
    // Debug: Log intake data to see what we have
    console.log('🔍 DEBUG: intakeData:', JSON.stringify(intakeData, null, 2));
    console.log('🔍 DEBUG: intakeData?.intake_id:', intakeData?.intake_id);
    
    // Get or validate intake_id from backend API
    let validIntakeId = intakeData?.intake_id;
    
    // If intake_id is missing, try to fetch the most recent intake from backend
    if (!validIntakeId) {
      console.log('⚠️ intake_id not found in intakeData, fetching from backend API...');
      try {
        const apiUrl = getApiConfig().baseUrl;
        const response = await fetch(`${apiUrl}/user/intake/latest`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${session.access_token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (response.ok) {
          const result = await response.json();
          if (result.success && result.intake_id) {
            validIntakeId = result.intake_id;
            console.log('✅ Found intake_id from backend:', validIntakeId);
          } else {
            console.warn('⚠️ No intake_id found in backend response:', result);
          }
        } else {
          console.error('❌ Error fetching intake_id from backend:', response.status);
        }
      } catch (error) {
        console.error('❌ Error in backend fetch:', error);
      }
    }
    
    // Check if we have a valid intake_id
    if (!validIntakeId) {
      console.error('❌ No intake_id available - cannot start intervention period');
      console.error('❌ Full intakeData object:', intakeData);
      Alert.alert(
        'Missing Data',
        'Unable to start intervention tracking. Please complete the intake first.',
        [{ text: 'OK' }]
      );
      return;
    }
    
    try {
      const startRequest = {
        intake_id: validIntakeId,
        intervention_name: intervention.name,
        selected_habits: interventionHabits,
        intervention_id: intervention.id,
        planned_duration_days: periodData.durationDays,
        start_date: periodData.startDate, // User-selected start date
        // cycle_phase is now fetched automatically by backend from cycle_phases table
      };
      
      console.log('📤 Starting intervention period with request:', startRequest);
      console.log('🔍 DEBUG: session.access_token exists?', !!session.access_token);
      console.log('🔍 DEBUG: session.access_token length:', session.access_token?.length);
      console.log('🔍 DEBUG: session.access_token preview:', session.access_token?.substring(0, 20) + '...');
      
      const result = await interventionPeriodService.startInterventionPeriod(
        startRequest,
        session.access_token
      );
      
      if (result.success) {
        console.log('✅ Intervention period tracking started:', result.period_id);
      } else {
        console.error('❌ Failed to start intervention period tracking:', result.error);
        Alert.alert(
          'Tracking Error',
          'Failed to start tracking your intervention. Please try again or contact support.',
          [{ text: 'OK' }]
        );
        return;
      }
    } catch (error) {
      console.error('❌ Error starting intervention period tracking:', error);
      Alert.alert(
        'Tracking Error',
        'Failed to start tracking your intervention. Please try again or contact support.',
        [{ text: 'OK' }]
      );
      return;
    }
    
    // ✅ Pass the habits to the habit selection screen using AppStateContext
    updateSelectedHabits(interventionHabits);
    // Callbacks for backward compatibility
    onHabitsSelected?.(interventionHabits);
    updateCurrentScreen('habit-selection');
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

