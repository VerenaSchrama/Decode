import React, { useState, useEffect } from 'react';
import { View, StyleSheet, SafeAreaView } from 'react-native';
import { StoryIntakeData, STORY_INTAKE_STEPS } from '../types/StoryIntake';
import { LastPeriodStep } from '../components/story-intake/LastPeriodStep';
import { CycleLengthStep } from '../components/story-intake/CycleLengthStep';
import { SymptomsStep } from '../components/story-intake/SymptomsStep';
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
    if (currentStep < STORY_INTAKE_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleUpdate = (data: Partial<StoryIntakeData>) => {
    setFormData({ ...formData, ...data });
  };

  const handleComplete = async (data: StoryIntakeData) => {
    try {
      // Check if user is authenticated
      if (!session?.access_token) {
        throw new Error('User not authenticated. Please log in to get recommendations.');
      }
      
      // Use formData instead of data parameter to ensure all updates are included
      const finalData = { ...formData, ...data };
      
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
      
      // Add the intake_id to the data for tracking
      const enhancedData = {
        ...finalData,
        intake_id: result.data_collection?.intake_id,
        recommendations: result.interventions
      };
      
      console.log('✅ Intake completed:', enhancedData);
      onComplete(enhancedData);
    } catch (error) {
      console.error('❌ Error completing intake:', error);
      // Still pass the data to parent even if API call fails
      onComplete(finalData);
    }
  };

  const renderStepComponent = () => {
    switch (currentStep) {
      case 0: // LastPeriodStep
        return (
          <LastPeriodStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 1: // CycleLengthStep
        // Show CycleLengthStep only if user has periods and selected a date
        if (formData.lastPeriod?.hasPeriod && formData.lastPeriod?.date) {
          return (
            <CycleLengthStep
              data={formData}
              onUpdate={handleUpdate}
              onNext={handleNext}
              onBack={handleBack}
            />
          );
        } else {
          // Skip cycle length step and go to symptoms
          handleNext();
          return null;
        }
      case 2: // SymptomsStep
        return (
          <SymptomsStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 3: // InterventionsStep
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