import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';
import { apiService } from '../services/apiService';
import { interventionPeriodService } from '../services/interventionPeriodService';
import { useAuth } from '../contexts/AuthContext';
import { useAppState } from '../contexts/AppStateContext';
import CalendarPicker from 'react-native-calendar-picker';

interface Intervention {
  id: number;
  name: string;
  profile?: string;
  scientific_source?: string;
  category?: string;
}

interface Habit {
  id: number;
  name: string;
  description?: string;
  why_it_works?: string;
  in_practice?: string;
}

interface ChangeInterventionScreenProps {
  onComplete?: () => void;
  onCancel?: () => void;
}

const DURATION_OPTIONS = [
  { days: 7, label: '1 Week' },
  { days: 14, label: '2 Weeks' },
  { days: 30, label: '1 Month' },
  { days: 60, label: '2 Months' },
  { days: 90, label: '3 Months' },
];

export default function ChangeInterventionScreen({ onComplete, onCancel }: ChangeInterventionScreenProps) {
  const { session } = useAuth();
  const { updateCurrentScreen } = useAppState();
  
  const [interventions, setInterventions] = useState<Intervention[]>([]);
  const [selectedIntervention, setSelectedIntervention] = useState<Intervention | null>(null);
  const [habits, setHabits] = useState<Habit[]>([]);
  const [selectedHabits, setSelectedHabits] = useState<string[]>([]);
  const [selectedDuration, setSelectedDuration] = useState<number>(30);
  const [selectedDate, setSelectedDate] = useState<Date>(new Date());
  const [showCalendar, setShowCalendar] = useState(false);
  
  const [loadingInterventions, setLoadingInterventions] = useState(true);
  const [loadingHabits, setLoadingHabits] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<'intervention' | 'habits' | 'period'>('intervention');

  useEffect(() => {
    loadInterventions();
  }, []);

  const loadInterventions = async () => {
    try {
      setLoadingInterventions(true);
      setError(null);
      const result = await apiService.getAllInterventions();
      
      if (result.success && result.interventions) {
        setInterventions(result.interventions);
      } else {
        setError(result.error || 'Failed to load interventions');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load interventions');
    } finally {
      setLoadingInterventions(false);
    }
  };

  const handleInterventionSelect = async (intervention: Intervention) => {
    setSelectedIntervention(intervention);
    setSelectedHabits([]);
    setLoadingHabits(true);
    setError(null);
    
    try {
      const result = await apiService.getHabitsForIntervention(intervention.id);
      
      if (result.success && result.habits) {
        setHabits(result.habits);
        setStep('habits');
      } else {
        setError(result.error || 'Failed to load habits');
        Alert.alert('Error', result.error || 'Failed to load habits for this intervention');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load habits');
      Alert.alert('Error', err.message || 'Failed to load habits');
    } finally {
      setLoadingHabits(false);
    }
  };

  const toggleHabit = (habitName: string) => {
    setSelectedHabits(prev => {
      if (prev.includes(habitName)) {
        return prev.filter(h => h !== habitName);
      } else {
        return [...prev, habitName];
      }
    });
  };

  const handleContinueFromHabits = () => {
    if (selectedHabits.length === 0) {
      Alert.alert('Select Habits', 'Please select at least one habit to track.');
      return;
    }
    setStep('period');
  };

  const handleSave = async () => {
    if (!selectedIntervention || selectedHabits.length === 0 || !session?.access_token) {
      Alert.alert('Error', 'Please complete all steps before saving.');
      return;
    }

    try {
      setSaving(true);
      setError(null);

      const startDateISO = selectedDate.toISOString().split('T')[0];
      
      const result = await interventionPeriodService.resetInterventionPeriod(
        {
          intervention_id: selectedIntervention.id,
          intervention_name: selectedIntervention.name,
          selected_habits: selectedHabits,
          planned_duration_days: selectedDuration,
          start_date: startDateISO,
        },
        session.access_token
      );

      if (result.success) {
        Alert.alert(
          'Success',
          'Your intervention has been changed successfully!',
          [
            {
              text: 'OK',
              onPress: () => {
                if (onComplete) {
                  onComplete();
                } else {
                  updateCurrentScreen('main-app');
                }
              }
            }
          ]
        );
      } else {
        setError(result.error || 'Failed to change intervention');
        Alert.alert('Error', result.error || 'Failed to change intervention');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to change intervention');
      Alert.alert('Error', err.message || 'Failed to change intervention');
    } finally {
      setSaving(false);
    }
  };

  const calculateEndDate = (startDate: Date, durationDays: number): Date => {
    const endDate = new Date(startDate);
    endDate.setDate(endDate.getDate() + durationDays - 1);
    return endDate;
  };

  const formatDate = (date: Date): string => {
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loadingInterventions) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color={colors.primary} />
          <Text style={styles.loadingText}>Loading interventions...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error && step === 'intervention') {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Ionicons name="alert-circle" size={48} color={colors.error} />
          <Text style={styles.errorText}>{error}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={loadInterventions}>
            <Text style={styles.retryButtonText}>Retry</Text>
          </TouchableOpacity>
          {onCancel && (
            <TouchableOpacity style={styles.cancelButton} onPress={onCancel}>
              <Text style={styles.cancelButtonText}>Cancel</Text>
            </TouchableOpacity>
          )}
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => {
            if (step === 'intervention') {
              if (onCancel) {
                onCancel();
              } else {
                updateCurrentScreen('main-app');
              }
            } else if (step === 'habits') {
              setStep('intervention');
              setSelectedIntervention(null);
              setHabits([]);
              setSelectedHabits([]);
            } else {
              setStep('habits');
            }
          }}
          style={styles.backButton}
        >
          <Ionicons name="arrow-back" size={24} color={colors.primary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>
          {step === 'intervention' ? 'Select Intervention' :
           step === 'habits' ? 'Select Habits' :
           'Set Timeline'}
        </Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Step Indicator */}
        <View style={styles.stepIndicator}>
          <View style={[styles.step, step === 'intervention' && styles.stepActive]}>
            <Text style={[styles.stepNumber, step === 'intervention' && styles.stepNumberActive]}>1</Text>
            <Text style={[styles.stepLabel, step === 'intervention' && styles.stepLabelActive]}>Intervention</Text>
          </View>
          <View style={[styles.stepLine, step !== 'intervention' && styles.stepLineActive]} />
          <View style={[styles.step, step === 'habits' && styles.stepActive]}>
            <Text style={[styles.stepNumber, step === 'habits' && styles.stepNumberActive]}>2</Text>
            <Text style={[styles.stepLabel, step === 'habits' && styles.stepLabelActive]}>Habits</Text>
          </View>
          <View style={[styles.stepLine, step === 'period' && styles.stepLineActive]} />
          <View style={[styles.step, step === 'period' && styles.stepActive]}>
            <Text style={[styles.stepNumber, step === 'period' && styles.stepNumberActive]}>3</Text>
            <Text style={[styles.stepLabel, step === 'period' && styles.stepLabelActive]}>Timeline</Text>
          </View>
        </View>

        {/* Step 1: Select Intervention */}
        {step === 'intervention' && (
          <View style={styles.stepContent}>
            <Text style={styles.sectionTitle}>Choose an intervention</Text>
            <Text style={styles.sectionSubtitle}>Select the intervention you want to start</Text>
            
            {interventions.map((intervention) => (
              <TouchableOpacity
                key={intervention.id}
                style={[
                  styles.interventionCard,
                  selectedIntervention?.id === intervention.id && styles.interventionCardSelected
                ]}
                onPress={() => handleInterventionSelect(intervention)}
              >
                <View style={styles.interventionCardContent}>
                  <View style={styles.interventionCardHeader}>
                    <Text style={[
                      styles.interventionName,
                      selectedIntervention?.id === intervention.id && styles.interventionNameSelected
                    ]}>
                      {intervention.name}
                    </Text>
                    {selectedIntervention?.id === intervention.id && (
                      <Ionicons name="checkmark-circle" size={24} color={colors.primary} />
                    )}
                  </View>
                  {intervention.profile && (
                    <Text style={styles.interventionProfile} numberOfLines={2}>
                      {intervention.profile}
                    </Text>
                  )}
                </View>
              </TouchableOpacity>
            ))}
          </View>
        )}

        {/* Step 2: Select Habits */}
        {step === 'habits' && (
          <View style={styles.stepContent}>
            <Text style={styles.sectionTitle}>Select Habits</Text>
            <Text style={styles.sectionSubtitle}>
              Choose which habits you want to track for "{selectedIntervention?.name}"
            </Text>
            
            {loadingHabits ? (
              <View style={styles.loadingContainer}>
                <ActivityIndicator size="large" color={colors.primary} />
                <Text style={styles.loadingText}>Loading habits...</Text>
              </View>
            ) : (
              <>
                {habits.map((habit) => (
                  <TouchableOpacity
                    key={habit.id}
                    style={[
                      styles.habitCard,
                      selectedHabits.includes(habit.name) && styles.habitCardSelected
                    ]}
                    onPress={() => toggleHabit(habit.name)}
                  >
                    <View style={styles.habitCardContent}>
                      <View style={[
                        styles.habitCheckbox,
                        selectedHabits.includes(habit.name) && styles.habitCheckboxSelected
                      ]}>
                        {selectedHabits.includes(habit.name) && (
                          <Ionicons name="checkmark" size={16} color="#FFFFFF" />
                        )}
                      </View>
                      <View style={styles.habitTextContainer}>
                        <Text style={[
                          styles.habitName,
                          selectedHabits.includes(habit.name) && styles.habitNameSelected
                        ]}>
                          {habit.name}
                        </Text>
                        {habit.description && (
                          <Text style={styles.habitDescription} numberOfLines={2}>
                            {habit.description}
                          </Text>
                        )}
                      </View>
                    </View>
                  </TouchableOpacity>
                ))}
                
                <TouchableOpacity
                  style={[styles.continueButton, selectedHabits.length === 0 && styles.continueButtonDisabled]}
                  onPress={handleContinueFromHabits}
                  disabled={selectedHabits.length === 0}
                >
                  <Text style={styles.continueButtonText}>
                    Continue ({selectedHabits.length} selected)
                  </Text>
                </TouchableOpacity>
              </>
            )}
          </View>
        )}

        {/* Step 3: Set Period */}
        {step === 'period' && (
          <View style={styles.stepContent}>
            <Text style={styles.sectionTitle}>Set Your Timeline</Text>
            <Text style={styles.sectionSubtitle}>Choose how long you want to track this intervention</Text>
            
            {/* Duration Selection */}
            <View style={styles.durationContainer}>
              {DURATION_OPTIONS.map((option) => (
                <TouchableOpacity
                  key={option.days}
                  style={[
                    styles.durationOption,
                    selectedDuration === option.days && styles.durationOptionSelected
                  ]}
                  onPress={() => setSelectedDuration(option.days)}
                >
                  <Text style={[
                    styles.durationLabel,
                    selectedDuration === option.days && styles.durationLabelSelected
                  ]}>
                    {option.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            {/* Start Date Selection */}
            <View style={styles.dateContainer}>
              <Text style={styles.dateLabel}>Start Date</Text>
              <TouchableOpacity
                style={styles.dateButton}
                onPress={() => setShowCalendar(!showCalendar)}
              >
                <Ionicons name="calendar-outline" size={24} color={colors.primary} />
                <Text style={styles.dateButtonText}>{formatDate(selectedDate)}</Text>
              </TouchableOpacity>
              
              {showCalendar && (
                <View style={styles.calendarContainer}>
                  <CalendarPicker
                    onDateChange={(date: Date) => {
                      setSelectedDate(date);
                      setShowCalendar(false);
                    }}
                    selectedStartDate={selectedDate}
                    selectedEndDate={selectedDate}
                    allowRangeSelection={false}
                    minDate={new Date()}
                    maxDate={new Date(Date.now() + 365 * 24 * 60 * 60 * 1000)}
                    todayBackgroundColor={colors.primary}
                    selectedDayColor={colors.primary}
                    selectedDayTextColor="#FFFFFF"
                    textStyle={styles.calendarText}
                  />
                </View>
              )}
              
              <Text style={styles.dateInfo}>
                End Date: {formatDate(calculateEndDate(selectedDate, selectedDuration))}
              </Text>
            </View>

            {/* Save Button */}
            <TouchableOpacity
              style={[styles.saveButton, saving && styles.saveButtonDisabled]}
              onPress={handleSave}
              disabled={saving}
            >
              {saving ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <Text style={styles.saveButtonText}>Change Intervention</Text>
              )}
            </TouchableOpacity>
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#FFFFFF',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    padding: 4,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  placeholder: {
    width: 32,
  },
  content: {
    flex: 1,
    padding: 20,
  },
  stepIndicator: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 32,
    paddingVertical: 20,
  },
  step: {
    alignItems: 'center',
  },
  stepActive: {
    // Active step styling
  },
  stepNumber: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#E5E7EB',
    color: '#6B7280',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
    lineHeight: 32,
    marginBottom: 4,
  },
  stepNumberActive: {
    backgroundColor: colors.primary,
    color: '#FFFFFF',
  },
  stepLabel: {
    fontSize: 12,
    color: '#6B7280',
    fontWeight: '500',
  },
  stepLabelActive: {
    color: colors.primary,
    fontWeight: '600',
  },
  stepLine: {
    width: 40,
    height: 2,
    backgroundColor: '#E5E7EB',
    marginHorizontal: 8,
    marginBottom: 20,
  },
  stepLineActive: {
    backgroundColor: colors.primary,
  },
  stepContent: {
    flex: 1,
  },
  sectionTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 8,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 24,
  },
  interventionCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#E5E7EB',
  },
  interventionCardSelected: {
    borderColor: colors.primary,
    backgroundColor: '#F0F9FF',
  },
  interventionCardContent: {
    flex: 1,
  },
  interventionCardHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  interventionName: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    flex: 1,
  },
  interventionNameSelected: {
    color: colors.primary,
  },
  interventionProfile: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  habitCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#E5E7EB',
  },
  habitCardSelected: {
    borderColor: colors.primary,
    backgroundColor: '#F0F9FF',
  },
  habitCardContent: {
    flexDirection: 'row',
    alignItems: 'flex-start',
  },
  habitCheckbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
  },
  habitCheckboxSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  habitTextContainer: {
    flex: 1,
  },
  habitName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  habitNameSelected: {
    color: colors.primary,
  },
  habitDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  durationContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 32,
  },
  durationOption: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#E5E7EB',
    minWidth: 100,
    alignItems: 'center',
  },
  durationOptionSelected: {
    borderColor: colors.primary,
    backgroundColor: '#F0F9FF',
  },
  durationLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
  },
  durationLabelSelected: {
    color: colors.primary,
    fontWeight: '600',
  },
  dateContainer: {
    marginBottom: 32,
  },
  dateLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 12,
  },
  dateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    borderWidth: 2,
    borderColor: '#E5E7EB',
    marginBottom: 12,
  },
  dateButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
    marginLeft: 12,
  },
  calendarContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  calendarText: {
    fontSize: 14,
    color: '#1F2937',
  },
  dateInfo: {
    fontSize: 14,
    color: '#6B7280',
    fontStyle: 'italic',
  },
  continueButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 24,
  },
  continueButtonDisabled: {
    backgroundColor: '#D1D5DB',
    opacity: 0.6,
  },
  continueButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  saveButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginTop: 24,
  },
  saveButtonDisabled: {
    opacity: 0.6,
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  loadingContainer: {
    padding: 40,
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 12,
  },
  errorContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 40,
  },
  errorText: {
    fontSize: 16,
    color: colors.error,
    textAlign: 'center',
    marginTop: 16,
    marginBottom: 24,
  },
  retryButton: {
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 24,
    marginBottom: 12,
  },
  retryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  cancelButton: {
    backgroundColor: '#E5E7EB',
    borderRadius: 8,
    paddingVertical: 12,
    paddingHorizontal: 24,
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
  },
});

