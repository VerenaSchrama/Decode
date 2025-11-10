import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  Alert,
  Modal,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';
import CustomInterventionScreen from './CustomInterventionScreen';
import { interventionPeriodService } from '../services/interventionPeriodService';
import { useAuth } from '../contexts/AuthContext';
import { useFocusEffect } from '@react-navigation/native';
import { apiService } from '../services/apiService';
import { useAppState } from '../contexts/AppStateContext';

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
  const { user, session } = useAuth();
  const { updateCurrentScreen } = useAppState();
  const [showCustomIntervention, setShowCustomIntervention] = useState(false);
  const [showInterventionModal, setShowInterventionModal] = useState(false);
  
  // Progress metrics state
  const [progressMetrics, setProgressMetrics] = useState<{
    averageMood: number | null;
    daysPassed: number;
    totalDays: number;
    fullyCompletedDays: number;
    isLoading: boolean;
    hasIntervention: boolean;
    hasHabits: boolean;
  }>({
    averageMood: null,
    daysPassed: 0,
    totalDays: 0,
    fullyCompletedDays: 0,
    isLoading: true,
    hasIntervention: false,
    hasHabits: false,
  });

  // Load progress metrics using backend endpoint
  const loadProgressMetrics = async () => {
    if (!user?.id || !session?.access_token) {
      setProgressMetrics(prev => ({ ...prev, isLoading: false, hasIntervention: false, hasHabits: false }));
      return;
    }

    try {
      setIsLoadingProgress(true);
      
      // Get active intervention period
      const periodResponse = await interventionPeriodService.getActiveInterventionPeriod(session.access_token);
      
      if (!periodResponse.success || !periodResponse.period) {
        // No active intervention
        setProgressMetrics(prev => ({ 
          ...prev, 
          isLoading: false, 
          hasIntervention: false, 
          hasHabits: false 
        }));
        return;
      }

      const period = periodResponse.period;
      
      // Check if there are active habits
      let hasActiveHabits = false;
      try {
        // Check selectedHabits from props first
        if (selectedHabits && selectedHabits.length > 0) {
          hasActiveHabits = true;
        } else {
          // Fallback: check via API
          const habitsResponse = await apiService.getActiveHabits(user.id);
          hasActiveHabits = habitsResponse && habitsResponse.habits && habitsResponse.habits.length > 0;
        }
      } catch (error) {
        console.error('Error checking active habits:', error);
        // If API fails, check if period has selected_habits
        hasActiveHabits = period.selected_habits && period.selected_habits.length > 0;
      }

      // If no habits, return early with hasIntervention=true, hasHabits=false
      if (!hasActiveHabits) {
        setProgressMetrics(prev => ({
          ...prev,
          isLoading: false,
          hasIntervention: true,
          hasHabits: false,
        }));
        return;
      }

      // Has both intervention and habits - use backend progress endpoint
      console.log('📊 Loading progress metrics for period:', period.id);
      const progressResponse = await interventionPeriodService.getInterventionPeriodProgress(
        period.id,
        session.access_token
      );

      if (progressResponse.success && progressResponse.metrics) {
        const metrics = progressResponse.metrics;
        setProgressMetrics({
          averageMood: metrics.average_mood,
          daysPassed: metrics.days_passed,
          totalDays: metrics.total_days,
          fullyCompletedDays: metrics.fully_completed_days,
          isLoading: false,
          hasIntervention: true,
          hasHabits: true,
        });
        console.log('✅ Progress metrics loaded:', metrics);
      } else {
        console.error('❌ Failed to load progress metrics:', progressResponse.error);
        // Fallback to showing intervention exists but no metrics
        setProgressMetrics(prev => ({
          ...prev,
          isLoading: false,
          hasIntervention: true,
          hasHabits: true,
        }));
      }
    } catch (error) {
      console.error('Error loading progress metrics:', error);
      setProgressMetrics(prev => ({ ...prev, isLoading: false }));
    }
  };

  const [isLoadingProgress, setIsLoadingProgress] = useState(false);

  useEffect(() => {
    loadProgressMetrics();
  }, [user?.id, currentIntervention]);

  // Refresh when screen comes into focus (e.g., after saving daily progress)
  useFocusEffect(
    React.useCallback(() => {
      console.log('🔄 AnalysisScreen: Screen focused, refreshing progress metrics...');
      loadProgressMetrics();
    }, [user?.id, session?.access_token])
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
    <>
      {/* Intervention Details Modal */}
      <Modal
        visible={showInterventionModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowInterventionModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>{currentIntervention?.name || 'Intervention Details'}</Text>
              <TouchableOpacity
                style={styles.modalCloseButton}
                onPress={() => setShowInterventionModal(false)}
              >
                <Ionicons name="close" size={24} color="#1F2937" />
              </TouchableOpacity>
            </View>
            
            <ScrollView style={styles.modalScrollView} showsVerticalScrollIndicator={false}>
              {/* Intervention Explanation/Description */}
              {currentIntervention?.profile_match && (
                <View style={styles.modalSection}>
                  <Text style={styles.modalSectionTitle}>About this intervention</Text>
                  <Text style={styles.modalSectionText}>{currentIntervention.profile_match}</Text>
                </View>
              )}
              
              {/* Why Recommended */}
              {currentIntervention?.why_recommended && (
                <View style={styles.modalSection}>
                  <Text style={styles.modalSectionTitle}>Why this is recommended</Text>
                  <Text style={styles.modalSectionText}>{currentIntervention.why_recommended}</Text>
                </View>
              )}
              
              {/* What You'll Be Doing */}
              {currentIntervention?.what_will_you_be_doing && (
                <View style={styles.modalSection}>
                  <Text style={styles.modalSectionTitle}>What you'll be doing</Text>
                  <Text style={styles.modalSectionText}>{currentIntervention.what_will_you_be_doing}</Text>
                </View>
              )}
              
              {/* Habits */}
              {currentIntervention?.habits && currentIntervention.habits.length > 0 && (
                <View style={styles.modalSection}>
                  <Text style={styles.modalSectionTitle}>Habits to track</Text>
                  {currentIntervention.habits.map((habit: any, index: number) => (
                    <View key={index} style={styles.modalHabitItem}>
                      <Text style={styles.modalHabitNumber}>{index + 1}.</Text>
                      <Text style={styles.modalHabitText}>
                        {typeof habit === 'string' ? habit : habit.description}
                      </Text>
                    </View>
                  ))}
                </View>
              )}
              
              {/* Scientific Source */}
              {currentIntervention?.scientific_source && (
                <View style={styles.modalSection}>
                  <Text style={styles.modalSectionTitle}>Scientific source</Text>
                  <Text style={styles.modalSectionText}>{currentIntervention.scientific_source}</Text>
                </View>
              )}
            </ScrollView>
            
            <View style={styles.modalFooter}>
              <TouchableOpacity
                style={styles.modalCloseButtonLarge}
                onPress={() => setShowInterventionModal(false)}
              >
                <Text style={styles.modalCloseButtonText}>Close</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Intervention Progress */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Your Intervention Progress</Text>
          
          {progressMetrics.isLoading ? (
            <View style={styles.progressLoadingContainer}>
              <Text style={styles.progressLoadingText}>Loading progress...</Text>
            </View>
          ) : !progressMetrics.hasIntervention ? (
            <View style={styles.progressEmptyContainer}>
              <Ionicons name="information-circle-outline" size={48} color={colors.textSecondary} />
              <Text style={styles.progressEmptyText}>
                You currently have no active intervention
              </Text>
              <Text style={styles.progressEmptySubtext}>
                Complete an intake to start tracking your progress
              </Text>
            </View>
          ) : !progressMetrics.hasHabits ? (
            <View style={styles.progressEmptyContainer}>
              <Ionicons name="checkmark-circle-outline" size={48} color={colors.textSecondary} />
              <Text style={styles.progressEmptyText}>
                You currently have no active habits
              </Text>
              <Text style={styles.progressEmptySubtext}>
                Select habits to start tracking your daily progress
              </Text>
            </View>
          ) : progressMetrics.totalDays === 0 ? (
            <View style={styles.progressLoadingContainer}>
              <Text style={styles.progressLoadingText}>No active intervention period found</Text>
            </View>
          ) : (
              <View style={styles.progressMetricsContainer}>
                {/* Average Mood */}
                <View style={styles.progressMetric}>
                  <View style={styles.progressMetricHeader}>
                    <Ionicons name="happy-outline" size={20} color={colors.primary} />
                    <Text style={styles.progressMetricLabel}>Average Mood</Text>
                  </View>
                  <Text style={styles.progressMetricValue}>
                    {progressMetrics.averageMood !== null
                      ? `${progressMetrics.averageMood.toFixed(1)} / 5.0`
                      : 'No data yet'}
                  </Text>
                  {progressMetrics.averageMood !== null && (
                    <View style={styles.moodBarContainer}>
                      <View
                        style={[
                          styles.moodBarFill,
                          {
                            width: `${(progressMetrics.averageMood / 5) * 100}%`,
                            backgroundColor: progressMetrics.averageMood >= 4
                              ? '#10B981'
                              : progressMetrics.averageMood >= 3
                              ? '#F59E0B'
                              : '#EF4444',
                          },
                        ]}
                      />
                    </View>
                  )}
                  {progressMetrics.averageMood === null && (
                    <Text style={styles.progressMetricSubtext}>
                      Track your mood to see your average
                    </Text>
                  )}
                </View>

                {/* Days Progress */}
                <View style={styles.progressMetric}>
                  <View style={styles.progressMetricHeader}>
                    <Ionicons name="calendar-outline" size={20} color={colors.primary} />
                    <Text style={styles.progressMetricLabel}>Days Progress</Text>
                  </View>
                  <Text style={styles.progressMetricValue}>
                    Day {progressMetrics.daysPassed} of {progressMetrics.totalDays}
                  </Text>
                  <View style={styles.progressBarContainer}>
                    <View
                      style={[
                        styles.progressBarFill,
                        {
                          width: `${Math.min((progressMetrics.daysPassed / progressMetrics.totalDays) * 100, 100)}%`,
                        },
                      ]}
                    />
                  </View>
                  <Text style={styles.progressMetricSubtext}>
                    {progressMetrics.totalDays - progressMetrics.daysPassed > 0
                      ? `${progressMetrics.totalDays - progressMetrics.daysPassed} days remaining`
                      : 'Period completed!'}
                  </Text>
                </View>

                {/* Fully Completed Days */}
                <View style={styles.progressMetric}>
                  <View style={styles.progressMetricHeader}>
                    <Ionicons name="checkmark-circle-outline" size={20} color={colors.primary} />
                    <Text style={styles.progressMetricLabel}>Perfect Days</Text>
                  </View>
                  <Text style={styles.progressMetricValue}>
                    {progressMetrics.fullyCompletedDays} / {progressMetrics.totalDays} days
                  </Text>
                  <View style={styles.progressBarContainer}>
                    <View
                      style={[
                        styles.progressBarFill,
                        {
                          width: `${Math.min((progressMetrics.fullyCompletedDays / progressMetrics.totalDays) * 100, 100)}%`,
                          backgroundColor: '#10B981',
                        },
                      ]}
                    />
                  </View>
                  <Text style={styles.progressMetricSubtext}>
                    {progressMetrics.fullyCompletedDays === 0
                      ? 'Start tracking to see your perfect days!'
                      : `${((progressMetrics.fullyCompletedDays / progressMetrics.totalDays) * 100).toFixed(0)}% of days with all habits completed`}
                  </Text>
                </View>
              </View>
            )}
          </View>

        {/* Chat Access Card */}
        <TouchableOpacity style={styles.chatCard} onPress={onNavigateToChat}>
          <View style={styles.chatCardContent}>
            <View style={styles.chatIcon}>
              <Text style={styles.chatIconText}>💬</Text>
            </View>
            <View style={styles.chatTextContainer}>
              <Text style={styles.chatTitle}> Expert chat</Text>
              <Text style={styles.chatDescription}>
                Get personalized science-based answers based on your profile and progress
              </Text>
            </View>
            <Text style={styles.chatArrow}>→</Text>
          </View>
        </TouchableOpacity>

        {/* Current Status Overview */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Text style={styles.cardTitle}>Your Current Intervention</Text>
            {currentIntervention && (
              <TouchableOpacity 
                style={styles.changeInterventionButtonTop}
                onPress={() => {
                  // Navigate to change intervention screen using navigation prop
                  // We'll pass a callback to handle this in DiaryStack
                  if (onNavigateToChangeIntervention) {
                    onNavigateToChangeIntervention();
                  }
                }}
              >
                <Text style={styles.changeInterventionButtonText}>Change your intervention</Text>
              </TouchableOpacity>
            )}
          </View>

          {/* Current Intervention */}
          {currentIntervention && (
            <View style={styles.statusItem}>
              <View style={styles.statusHeader}>
                <View style={[styles.statusDot, { backgroundColor: colors.primary }]} />
                <Text style={styles.statusLabel}>Active Intervention</Text>
              </View>
              <View style={styles.interventionNameRow}>
                <Text style={styles.statusValue}>{currentIntervention.name}</Text>
                <TouchableOpacity 
                  style={styles.infoButton}
                  onPress={() => setShowInterventionModal(true)}
                >
                  <Ionicons name="information-circle" size={20} color={colors.primary} />
                </TouchableOpacity>
              </View>
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
    </>
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
  cardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1f2937',
    flex: 1,
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
    marginBottom: 12,
  },
  interventionNameRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  infoButton: {
    padding: 4,
    marginLeft: 6,
  },
  changeInterventionButton: {
    marginTop: 8,
    paddingVertical: 10,
    paddingHorizontal: 16,
    backgroundColor: colors.primary,
    borderRadius: 8,
    alignSelf: 'flex-start',
  },
  changeInterventionButtonTop: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: colors.primary,
    borderRadius: 8,
    marginLeft: 12,
  },
  changeInterventionButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  // Intervention Modal Styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    width: '90%',
    maxHeight: '80%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 8,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1F2937',
    flex: 1,
  },
  modalCloseButton: {
    padding: 4,
  },
  modalScrollView: {
    maxHeight: 400,
  },
  modalSection: {
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  modalSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  modalSectionText: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 22,
  },
  modalHabitItem: {
    flexDirection: 'row',
    marginBottom: 8,
    alignItems: 'flex-start',
  },
  modalHabitNumber: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.primary,
    marginRight: 8,
    minWidth: 24,
  },
  modalHabitText: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 22,
    flex: 1,
  },
  modalFooter: {
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  modalCloseButtonLarge: {
    backgroundColor: colors.primary,
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
  },
  modalCloseButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
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
  // Progress metrics styles
  progressLoadingContainer: {
    paddingVertical: 40,
    alignItems: 'center',
  },
  progressLoadingText: {
    fontSize: 14,
    color: '#6b7280',
  },
  progressEmptyContainer: {
    paddingVertical: 40,
    alignItems: 'center',
    justifyContent: 'center',
  },
  progressEmptyText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1f2937',
    marginTop: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  progressEmptySubtext: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    paddingHorizontal: 20,
  },
  progressMetricsContainer: {
    gap: 20,
  },
  progressMetric: {
    marginBottom: 8,
  },
  progressMetricHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  progressMetricLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6b7280',
    marginLeft: 8,
  },
  progressMetricValue: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1f2937',
    marginBottom: 8,
  },
  progressMetricSubtext: {
    fontSize: 12,
    color: '#6b7280',
    marginTop: 4,
  },
  moodBarContainer: {
    height: 8,
    backgroundColor: '#f3f4f6',
    borderRadius: 4,
    overflow: 'hidden',
    marginTop: 4,
  },
  moodBarFill: {
    height: '100%',
    borderRadius: 4,
  },
  progressBarContainer: {
    height: 8,
    backgroundColor: '#f3f4f6',
    borderRadius: 4,
    overflow: 'hidden',
    marginTop: 4,
  },
  progressBarFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 4,
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
