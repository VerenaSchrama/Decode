import React from 'react';
import MainAppNavigator from '../navigation/MainAppNavigator';

// ✅ MainAppScreen no longer needs props - MainAppNavigator will get data from AppStateContext
// Keeping props interface for backward compatibility during migration
interface MainAppScreenProps {
  selectedHabits?: string[];
  intakeData?: any;
  currentIntervention?: any;
}

export default function MainAppScreen({ selectedHabits, intakeData, currentIntervention }: MainAppScreenProps) {
  // ✅ MainAppNavigator will now use AppStateContext directly instead of props
  // Props are kept for backward compatibility but will be ignored
  return (
    <MainAppNavigator 
      selectedHabits={selectedHabits || []} 
      intakeData={intakeData}
      currentIntervention={currentIntervention}
    />
  );
}

