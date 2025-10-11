import React from 'react';
import MainAppNavigator from '../navigation/MainAppNavigator';

interface MainAppScreenProps {
  selectedHabits: string[];
  intakeData?: any;
  currentIntervention?: any;
}

export default function MainAppScreen({ selectedHabits, intakeData, currentIntervention }: MainAppScreenProps) {
  return (
    <MainAppNavigator 
      selectedHabits={selectedHabits} 
      intakeData={intakeData}
      currentIntervention={currentIntervention}
    />
  );
}

