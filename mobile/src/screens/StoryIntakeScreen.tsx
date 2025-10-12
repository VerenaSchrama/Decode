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
import { useTempUser } from '../contexts/TempUserContext';

interface StoryIntakeScreenProps {
  onComplete: (data: StoryIntakeData) => void;
}

export default function StoryIntakeScreen({ onComplete }: StoryIntakeScreenProps) {
  const { tempUser } = useTempUser();
  const [currentStep, setCurrentStep] = useState(1); // Start at step 1 (DateOfBirthStep) instead of 0 (NameStep)
  const [formData, setFormData] = useState<StoryIntakeData>({
    profile: { 
      name: tempUser?.name || '', // Pre-populate with name from registration
      dateOfBirth: tempUser?.date_of_birth || '' 
    },
    lastPeriod: { date: '', hasPeriod: true, cycleLength: undefined },
    symptoms: { selected: [], additional: '' },
    interventions: { selected: [], additional: '' },
    dietaryPreferences: { selected: [], additional: '' },
    consent: false,
    anonymous: tempUser?.anonymous || false,
  });

  const handleNext = () => {
    if (currentStep < STORY_INTAKE_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) { // Changed from 0 to 1 since we start at step 1
      setCurrentStep(currentStep - 1);
    }
  };

  const handleUpdate = (data: Partial<StoryIntakeData>) => {
    setFormData({ ...formData, ...data });
  };

  const handleComplete = (data: StoryIntakeData) => {
    onComplete(data);
  };

  const renderStepComponent = () => {
    switch (currentStep) {
      case 1: // DateOfBirthStep (was case 1, now case 1)
        return (
          <DateOfBirthStep
            data={formData}
            onUpdate={handleUpdate}
            onNext={handleNext}
            onBack={handleBack}
          />
        );
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