import React, { useState, useEffect } from 'react';
import { View, StyleSheet, SafeAreaView } from 'react-native';
import { StoryIntakeData, STORY_INTAKE_STEPS } from '../types/StoryIntake';
import { SymptomsStep } from '../components/story-intake/SymptomsStep';
import { CycleLengthStep } from '../components/story-intake/CycleLengthStep';
import { LastPeriodStep } from '../components/story-intake/LastPeriodStep';
import { InterventionsStep } from '../components/story-intake/InterventionsStep';
import { DietaryStep } from '../components/story-intake/DietaryStep';
import { ConsentStep } from '../components/story-intake/ConsentStep';
import { useAuth } from '../contexts/AuthContext';
import { getApiConfig } from '../config/environment';

interface StoryIntakeScreenProps {
  onComplete: (data: StoryIntakeData) => void;
}

export default function StoryIntakeScreen({ onComplete }: StoryIntakeScreenProps) {
  const { user, session } = useAuth();
  const [currentStep, setCurrentStep] = useState(0); // Start at LastPeriodStep (step 0) - Name and Age collected during registration
  const [formData, setFormData] = useState<StoryIntakeData>({
    profile: { 
      name: user?.name || '', // Pre-populate with name from authenticated user
      age: user?.age || 25 // Use age from user profile if available, otherwise default to 25
    },
    lastPeriod: { date: '', hasPeriod: true, cycleLength: undefined },
    symptoms: { selected: [], additional: '' },
    interventions: { selected: [], additional: '' },
    dietaryPreferences: { selected: [], additional: '' },
    consent: false,
  });

  const handleNext = () => {
    // Skip CycleLengthStep if user doesn't have a period
    let nextStep = currentStep + 1;
    
    // If we're at step 1 (LastPeriod) and user doesn't have a period, skip to Interventions
    if (currentStep === 1 && formData.lastPeriod?.hasPeriod === false) {
      nextStep = 3; // Skip CycleLengthStep (2) and go to InterventionsStep (3)
    }
    
    // If we're going back to step 2 (CycleLength) but user doesn't have a period, skip it
    if (nextStep === 2 && formData.lastPeriod?.hasPeriod === false) {
      nextStep = 3;
    }
    
    if (nextStep < STORY_INTAKE_STEPS.length + 1) { // +1 to account for skipped step
      setCurrentStep(nextStep);
    }
  };

  const handleBack = () => {
    let prevStep = currentStep - 1;
    
    // If we're at Interventions (step 3) and user doesn't have a period, go back to LastPeriod
    if (currentStep === 3 && formData.lastPeriod?.hasPeriod === false) {
      prevStep = 1; // Go back to LastPeriod, skip CycleLength
    }
    
    if (prevStep >= 0) {
      setCurrentStep(prevStep);
    }
  };

  const handleUpdate = (data: Partial<StoryIntakeData>) => {
    setFormData({ ...formData, ...data });
  };

  const handleComplete = async (data: StoryIntakeData) => {
    // Use formData instead of data parameter to ensure all updates are included
    const finalData = { ...formData, ...data };
    
    try {
      // Check if user is authenticated
      if (!session?.access_token) {
        throw new Error('User not authenticated. Please log in to get recommendations.');
      }
      
      // Debug: Log the data being sent
      console.log('🔍 DEBUG: Sending intake data:', JSON.stringify(finalData, null, 2));
      
      // User is already authenticated, so we can call the /recommend endpoint directly
      const apiUrl = getApiConfig().baseUrl;
      const response = await fetch(`${apiUrl}/recommend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`, // Use authenticated user's token
        },
        body: JSON.stringify(finalData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Debug: Log the full response to see if intake_id is present
      console.log('🔍 DEBUG: Full backend response:', JSON.stringify(result, null, 2));
      console.log('🔍 DEBUG: data_collection:', result.data_collection);
      console.log('🔍 DEBUG: intake_id from response:', result.data_collection?.intake_id);
      
      // Add the intake_id to the data for tracking
      const enhancedData = {
        ...finalData,
        intake_id: result.data_collection?.intake_id,
        recommendations: result.interventions
      };
      
      console.log('✅ Intake completed with intake_id:', enhancedData.intake_id);
      onComplete(enhancedData);
    } catch (error) {
      console.error('❌ Error completing intake:', error);
      // Still pass the data to parent even if API call fails
      onComplete(finalData);
    }
  };

  // Calculate which step to show based on whether user has a period
  const getAdjustedStep = (step: number) => {
    // After LastPeriodStep (step 1), check if user doesn't have a period
    if (step === 2 && formData.lastPeriod?.hasPeriod === false) {
      return 3; // Skip CycleLengthStep, go to InterventionsStep
    }
    return step;
  };

  const renderStepComponent = () => {
    const adjustedStep = getAdjustedStep(currentStep);
    
    switch (adjustedStep) {
      case 0: // SymptomsStep (first step)
        return (
          <SymptomsStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 1: // LastPeriodStep (now second step)
        return (
          <LastPeriodStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 2: // CycleLengthStep (now third step, but skipped if no period)
        return (
          <CycleLengthStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 3: // InterventionsStep (fourth step)
        return (
          <InterventionsStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 4: // DietaryStep
        return (
          <DietaryStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 5: // ConsentStep
        return (
          <ConsentStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
            onComplete={handleComplete}
          />
        );
      default:
        return null;
    }
  };

  return (
    <View style={styles.container}>
      {renderStepComponent()}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
});