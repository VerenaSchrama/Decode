import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';
import { DailyProgressAPI } from '../services/dailyProgressApi';
import { useAuth } from '../contexts/AuthContext';
import CustomInterventionScreen from './CustomInterventionScreen';

interface AnalysisScreenProps {
  intakeData?: any;
  currentIntervention?: any;
  selectedHabits?: string[];
  onNavigateToChat: () => void;
}

export default function AnalysisScreen({
  intakeData,
  currentIntervention,
  selectedHabits,
  onNavigateToChat,
}: AnalysisScreenProps) {
  const { user } = useAuth();
  const [currentStreak, setCurrentStreak] = useState<number>(0);
  const [isLoadingStreak, setIsLoadingStreak] = useState(true);
  const [showCustomIntervention, setShowCustomIntervention] = useState(false);

  const loadStreak = async () => {
    try {
      console.log('🔄 AnalysisScreen: Loading streak...');
      // Use authenticated user ID
      const userId = user?.id;
      if (!userId) {
        console.error('No authenticated user found');
        return;
      }
      console.log('Using user ID:', userId);
      const streakResponse = await DailyProgressAPI.getHabitStreak(userId);
      console.log('✅ AnalysisScreen: Streak loaded:', streakResponse.current_streak);
      setCurrentStreak(streakResponse.current_streak);
    } catch (error) {
      console.error('❌ AnalysisScreen: Error loading streak:', error);
    } finally {
      setIsLoadingStreak(false);
    }
  };

  useEffect(() => {
    loadStreak();
  }, []);

  // Refresh streak when screen comes into focus
  useFocusEffect(
    React.useCallback(() => {
      console.log('🎯 AnalysisScreen: Screen focused, refreshing streak...');
      loadStreak();
    }, [])
  );
  const getCyclePhaseInfo = () => {
    if (!intakeData?.lastPeriod) return null;
    
    const lastPeriod = intakeData.lastPeriod;
    if (!lastPeriod.hasPeriod) {
      return {
        phase: 'No Cycle',
        description: 'Focus on overall hormonal health optimization',
        color: '#6b7280'
      };
    }
    
    // Simple cycle phase calculation
    if (lastPeriod.date && lastPeriod.cycleLength) {
      const lastPeriodDate = new Date(lastPeriod.date);
      const today = new Date();
      const daysSince = Math.floor((today.getTime() - lastPeriodDate.getTime()) / (1000 * 60 * 60 * 24));
      const currentDay = (daysSince % lastPeriod.cycleLength) + 1;
      
      if (currentDay <= 5) {
        return {
          phase: 'Menstrual Phase',
          description: 'Focus on iron-rich foods and gentle movement',
          color: '#dc2626'
        };
      } else if (currentDay <= 13) {
        return {
          phase: 'Follicular Phase',
          description: 'Support hormone production with healthy fats',
          color: '#059669'
        };
      } else if (currentDay <= 16) {
        return {
          phase: 'Ovulatory Phase',
          description: 'Optimize energy with complex carbohydrates',
          color: '#d97706'
        };
      } else if (currentDay <= lastPeriod.cycleLength - 5) {
        return {
          phase: 'Luteal Phase',
          description: 'Support progesterone with magnesium-rich foods',
          color: '#7c3aed'
        };
      } else {
        return {
          phase: 'Pre-menstrual Phase',
          description: 'Focus on mood-supporting nutrients and hydration',
          color: '#be185d'
        };
      }
    }
    
    return null;
  };

  const cycleInfo = getCyclePhaseInfo();

  const handleCustomInterventionValidate = (intervention: any) => {
    // TODO: Save custom intervention and start tracking
    console.log('Custom intervention validated:', intervention);
    setShowCustomIntervention(false);
    // Show success message
    Alert.alert('Success', 'Your custom intervention has been validated and is ready to track!');
  };

  if (showCustomIntervention) {
    return (
      <CustomInterventionScreen
        onBack={() => setShowCustomIntervention(false)}
        onValidate={handleCustomInterventionValidate}
        userContext={intakeData}
      />
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Weekly Summary */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Your Progress</Text>
          <View style={styles.summaryRow}>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryLabel}>Today's Mood</Text>
              <Text style={styles.summaryValue}>- -</Text>
            </View>
            <View style={styles.summaryItem}>
              <Text style={styles.summaryLabel}>Habits</Text>
              <View style={styles.streakContainer}>
                <Text style={styles.summaryValue}>
                  {isLoadingStreak ? '...' : currentStreak > 0 ? `${currentStreak} day streak` : 'Ready to start'}
                </Text>
                {isLoadingStreak && (
                  <Ionicons name="sync" size={14} color={colors.primary} style={styles.loadingIcon} />
                )}
              </View>
            </View>
          </View>
        </View>

        {/* AI Insights - Coming Soon */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Personal insights from your Nutritionist</Text>
          <View style={styles.comingSoonContainer}>
            <Text style={styles.comingSoonTitle}>Coming Soon</Text>
            <Text style={styles.comingSoonText}>
              AI-powered insights and analytics based on your tracking patterns are coming soon!
            </Text>
          </View>
        </View>

        {/* Chat Access Card */}
        <TouchableOpacity style={styles.chatCard} onPress={onNavigateToChat}>
          <View style={styles.chatCardContent}>
            <View style={styles.chatIcon}>
              <Text style={styles.chatIconText}>💬</Text>
            </View>
            <View style={styles.chatTextContainer}>
              <Text style={styles.chatTitle}>Start expert chat</Text>
              <Text style={styles.chatDescription}>
                Get personalized science-based answers based on your profile and progress
              </Text>
            </View>
            <Text style={styles.chatArrow}>→</Text>
          </View>
        </TouchableOpacity>

        {/* Current Status Overview */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Your Current Status</Text>
          
          {/* Cycle Phase */}
          {cycleInfo && (
            <View style={styles.statusItem}>
              <View style={styles.statusHeader}>
                <View style={[styles.statusDot, { backgroundColor: cycleInfo.color }]} />
                <Text style={styles.statusLabel}>Current Phase</Text>
              </View>
              <Text style={styles.statusValue}>{cycleInfo.phase}</Text>
              <Text style={styles.statusDescription}>{cycleInfo.description}</Text>
            </View>
          )}

          {/* Current Intervention */}
          {currentIntervention && (
            <View style={styles.statusItem}>
              <View style={styles.statusHeader}>
                <View style={[styles.statusDot, { backgroundColor: colors.primary }]} />
                <Text style={styles.statusLabel}>Active Intervention</Text>
              </View>
              <Text style={styles.statusValue}>{currentIntervention.name}</Text>
              <Text style={styles.statusDescription}>
                {currentIntervention.habits?.length || 0} habits to track
              </Text>
            </View>
          )}

          {/* Selected Habits */}
          {selectedHabits && selectedHabits.length > 0 && (
            <View style={styles.statusItem}>
              <View style={styles.statusHeader}>
                <View style={[styles.statusDot, { backgroundColor: '#10b981' }]} />
                <Text style={styles.statusLabel}>Tracking Habits</Text>
              </View>
              <Text style={styles.statusValue}>{selectedHabits.length} habits</Text>
              <Text style={styles.statusDescription}>
                {selectedHabits.slice(0, 2).join(', ')}
                {selectedHabits.length > 2 && ` +${selectedHabits.length - 2} more`}
              </Text>
            </View>
          )}
        </View>

        {/* Create Custom Intervention */}
        <TouchableOpacity 
          style={[styles.card, styles.customInterventionCard]}
          onPress={() => setShowCustomIntervention(true)}
        >
          <View style={styles.customInterventionContent}>
            <Text style={styles.customInterventionIcon}>🧪</Text>
            <View style={styles.customInterventionTextContainer}>
              <Text style={styles.customInterventionTitle}>Create Custom Intervention</Text>
              <Text style={styles.customInterventionDescription}>
                Design and validate your own intervention with scientific feedback
              </Text>
            </View>
            <Text style={styles.customInterventionArrow}>→</Text>
          </View>
        </TouchableOpacity>

        {/* Profile Summary */}
        {intakeData && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Your Health Profile</Text>
            
            {intakeData.symptoms?.selected && intakeData.symptoms.selected.length > 0 && (
              <View style={styles.profileItem}>
                <Text style={styles.profileLabel}>Symptoms & Conditions</Text>
                <Text style={styles.profileValue}>
                  {intakeData.symptoms.selected.join(', ')}
                </Text>
              </View>
            )}

            {intakeData.dietaryPreferences?.selected && intakeData.dietaryPreferences.selected.length > 0 && (
              <View style={styles.profileItem}>
                <Text style={styles.profileLabel}>Dietary Preferences</Text>
                <Text style={styles.profileValue}>
                  {intakeData.dietaryPreferences.selected.join(', ')}
                </Text>
              </View>
            )}

            {intakeData.interventions?.selected && intakeData.interventions.selected.length > 0 && (
              <View style={styles.profileItem}>
                <Text style={styles.profileLabel}>Previous Interventions</Text>
                <Text style={styles.profileValue}>
                  {intakeData.interventions.selected.map((item: any) => 
                    typeof item === 'string' ? item : item.intervention
                  ).join(', ')}
                </Text>
              </View>
            )}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  content: {
    padding: 16,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1f2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
  },
  chatCard: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4,
    borderWidth: 2,
    borderColor: colors.primary,
    transform: [{ scale: 1.02 }],
  },
  chatCardContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 20,
  },
  chatIcon: {
    width: 52,
    height: 52,
    borderRadius: 26,
    backgroundColor: colors.primary,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 3,
  },
  chatIconText: {
    fontSize: 24,
    color: '#ffffff',
  },
  chatTextContainer: {
    flex: 1,
  },
  chatTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: 4,
  },
  chatDescription: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  chatArrow: {
    fontSize: 24,
    color: colors.primary,
    fontWeight: '700',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 4,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 16,
  },
  statusItem: {
    marginBottom: 16,
  },
  statusHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginRight: 8,
  },
  statusLabel: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: '500',
  },
  statusValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginBottom: 4,
  },
  statusDescription: {
    fontSize: 14,
    color: '#6b7280',
  },
  profileItem: {
    marginBottom: 12,
  },
  profileLabel: {
    fontSize: 14,
    color: '#6b7280',
    fontWeight: '500',
    marginBottom: 4,
  },
  profileValue: {
    fontSize: 16,
    color: '#1f2937',
  },
  actionButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f3f4f6',
  },
  actionIcon: {
    fontSize: 20,
    marginRight: 12,
  },
  actionContent: {
    flex: 1,
  },
  actionTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1f2937',
    marginBottom: 2,
  },
  actionDescription: {
    fontSize: 14,
    color: '#6b7280',
  },
  // Weekly summary styles
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  summaryItem: {
    alignItems: 'center',
  },
  summaryLabel: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 4,
  },
  summaryValue: {
    fontSize: 24,
    fontWeight: '600',
    color: '#1f2937',
  },
  streakContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  loadingIcon: {
    marginLeft: 8,
  },
  // AI insights styles
  insightItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    paddingVertical: 8,
  },
  insightIcon: {
    fontSize: 16,
    marginRight: 12,
    marginTop: 2,
  },
  insightText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  comingSoonContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  comingSoonIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  comingSoonTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12,
  },
  comingSoonText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    lineHeight: 22,
  },
  customInterventionCard: {
    backgroundColor: '#F0F9FF',
    borderWidth: 2,
    borderColor: colors.primary,
    borderRadius: 12,
    marginBottom: 16,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  customInterventionContent: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
  },
  customInterventionIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  customInterventionTextContainer: {
    flex: 1,
  },
  customInterventionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.primary,
    marginBottom: 4,
  },
  customInterventionDescription: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  customInterventionArrow: {
    fontSize: 20,
    color: colors.primary,
    fontWeight: '600',
  },
});
