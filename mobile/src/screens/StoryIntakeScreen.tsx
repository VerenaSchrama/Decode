import React, { useState, useEffect } from 'react';
import { View, StyleSheet, SafeAreaView } from 'react-native';
import { StoryIntakeData, STORY_INTAKE_STEPS } from '../types/StoryIntake';
import { NameStep } from '../components/story-intake/NameStep';
import { DateOfBirthStep } from '../components/story-intake/DateOfBirthStep';
import { LastPeriodStep } from '../components/story-intake/LastPeriodStep';
import { CycleLengthStep } from '../components/story-intake/CycleLengthStep';
import { SymptomsStep } from '../components/story-intake/SymptomsStep';
import { InterventionsStep } from '../components/story-intake/InterventionsStep';
import { DietaryStep } from '../components/story-intake/DietaryStep';
import { ConsentStep } from '../components/story-intake/ConsentStep';
import { useAuth } from '../contexts/AuthContext';

interface StoryIntakeScreenProps {
  onComplete: (data: StoryIntakeData) => void;
}

export default function StoryIntakeScreen({ onComplete }: StoryIntakeScreenProps) {
  const { user, session } = useAuth();
  const [currentStep, setCurrentStep] = useState(2); // Start at step 2 (LastPeriodStep) instead of 0 (NameStep) and 1 (DateOfBirthStep)
  const [formData, setFormData] = useState<StoryIntakeData>({
    profile: { 
      name: user?.name || '', // Pre-populate with name from authenticated user
      age: 25 // Default age, will be updated during intake
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
    if (currentStep > 2) { // Changed from 1 to 2 since we start at step 2
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
      
      // Debug: Log the data being sent
      console.log('🔍 DEBUG: Sending intake data:', JSON.stringify(data, null, 2));
      
      // User is already authenticated, so we can call the /recommend endpoint directly
      const response = await fetch('https://api.decode-app.nl/recommend', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${session?.access_token}`, // Use authenticated user's token
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      // Add the intake_id to the data for tracking
      const enhancedData = {
        ...data,
        intake_id: result.data_collection?.intake_id,
        recommendations: result.interventions
      };
      
      console.log('✅ Intake completed:', enhancedData);
      onComplete(enhancedData);
    } catch (error) {
      console.error('❌ Error completing intake:', error);
      // Still pass the data to parent even if API call fails
      onComplete(data);
    }
  };

  const renderStepComponent = () => {
    switch (currentStep) {
      case 2: // LastPeriodStep (was case 2, now case 2)
        return (
          <LastPeriodStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 3: // CycleLengthStep (was case 3, now case 3)
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
      case 4: // SymptomsStep (was case 4, now case 4)
        return (
          <SymptomsStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 5: // InterventionsStep (was case 5, now case 5)
        return (
          <InterventionsStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 6: // DietaryStep (was case 6, now case 6)
        return (
          <DietaryStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
      case 7: // ConsentStep (was case 7, now case 7)
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