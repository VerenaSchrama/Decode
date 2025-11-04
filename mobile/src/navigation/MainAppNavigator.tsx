import React, { useState } from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { Ionicons } from '@expo/vector-icons';
import { StyleSheet } from 'react-native';
import { colors } from '../constants/colors';
import { useAppState } from '../contexts/AppStateContext';

// Import the main app screens
import SocialFeedScreen from '../screens/SocialFeedScreen';
import RecipeScreen from '../screens/RecipeScreen';
import DailyHabitsScreen from '../screens/DailyHabitsScreen';
import ProfileScreen from '../screens/ProfileScreen';
import AnalysisScreen from '../screens/AnalysisScreen';
import NutritionistChatScreen from '../screens/NutritionistChatScreen';

// Define parameter list for tab navigator
export type MainTabParamList = {
  Social: undefined;
  Recipes: undefined;
  Habits: { selectedHabits?: string[]; intakeData?: any };
  Diary: undefined;
  Profile: { intakeData?: any };
};

const Tab = createBottomTabNavigator<MainTabParamList>();

interface MainAppNavigatorProps {
  selectedHabits: string[];
  intakeData?: any;
  currentIntervention?: any;
}

function DiaryStack({ intakeData, currentIntervention, selectedHabits }: { intakeData?: any; currentIntervention?: any; selectedHabits: string[] }) {
  const [showChat, setShowChat] = useState(false);

  if (showChat) {
    return (
      <NutritionistChatScreen
        intakeData={intakeData}
        currentIntervention={currentIntervention}
        selectedHabits={selectedHabits}
        onBack={() => setShowChat(false)}
      />
    );
  }

  return (
    <AnalysisScreen
      intakeData={intakeData}
      currentIntervention={currentIntervention}
      selectedHabits={selectedHabits}
      onNavigateToChat={() => setShowChat(true)}
    />
  );
}

function MainAppNavigator({ selectedHabits, intakeData, currentIntervention }: MainAppNavigatorProps) {
  // ✅ Get state from AppStateContext (preferred) or fall back to props (backward compatibility)
  const { state } = useAppState();
  const finalSelectedHabits = state.selectedHabits.length > 0 ? state.selectedHabits : (selectedHabits || []);
  const finalIntakeData = state.intakeData || intakeData;
  const finalCurrentIntervention = state.currentIntervention || currentIntervention;
  
  return (
    // @ts-expect-error - React Navigation v7 type definition issue with id prop
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          let iconName: keyof typeof Ionicons.glyphMap;

          if (route.name === 'Social') {
            iconName = focused ? 'people' : 'people-outline';
          } else if (route.name === 'Recipes') {
            iconName = focused ? 'restaurant' : 'restaurant-outline';
          } else if (route.name === 'Habits') {
            iconName = focused ? 'checkmark-circle' : 'checkmark-circle-outline';
          } else if (route.name === 'Diary') {
            iconName = focused ? 'book' : 'book-outline';
          } else if (route.name === 'Profile') {
            iconName = focused ? 'person' : 'person-outline';
          } else {
            iconName = 'help-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: colors.primary,
        tabBarInactiveTintColor: '#9CA3AF',
        tabBarStyle: styles.tabBar,
        tabBarLabelStyle: styles.tabBarLabel,
        headerStyle: styles.header,
        headerTitleStyle: styles.headerTitle,
        headerTintColor: '#1F2937',
      })}
    >
      <Tab.Screen 
        name="Social" 
        component={SocialFeedScreen}
        options={{
          title: 'Community',
          headerTitle: 'Community Feed'
        }}
      />
      <Tab.Screen 
        name="Recipes" 
        component={RecipeScreen}
        options={{
          title: 'Recipes',
          headerTitle: 'Recipe Generator'
        }}
      />
      <Tab.Screen 
        name="Habits" 
        component={DailyHabitsScreen}
        options={{
          title: 'Habits',
          headerTitle: 'Daily Habits'
        }}
        initialParams={{ selectedHabits: finalSelectedHabits, intakeData: finalIntakeData }}
      />
      <Tab.Screen 
        name="Diary" 
        options={{
          title: 'Diary',
          headerTitle: 'Your Expert'
        }}
      >
        {() => <DiaryStack intakeData={finalIntakeData} currentIntervention={finalCurrentIntervention} selectedHabits={finalSelectedHabits} />}
      </Tab.Screen>
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          title: 'Profile',
          headerTitle: 'Your Profile'
        }}
        initialParams={{ intakeData: finalIntakeData }}
      />
    </Tab.Navigator>
  );
}

const styles = StyleSheet.create({
  tabBar: {
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    paddingTop: 8,
    paddingBottom: 8,
    height: 80,
  },
  tabBarLabel: {
    fontSize: 12,
    fontWeight: '500',
    marginTop: 4,
  },
  header: {
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    elevation: 0,
    shadowOpacity: 0,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
});

export default MainAppNavigator;
