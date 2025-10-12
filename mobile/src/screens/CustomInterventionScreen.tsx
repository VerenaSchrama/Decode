import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  SafeAreaView,
  Alert,
  KeyboardAvoidingView,
  Platform,
  TouchableWithoutFeedback,
  Keyboard,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';
import { apiService } from '../services/apiService';
import { useToast } from '../contexts/ToastContext';
import DateTimePicker from '@react-native-community/datetimepicker';

interface CustomInterventionScreenProps {
  onBack: () => void;
  onValidate: (intervention: CustomIntervention) => void;
  userContext?: any;
}

interface CustomIntervention {
  name: string;
  description: string;
  habits: string[];
  startDate: Date;
  trialPeriodDays: number;
  endDate: Date;
}

export default function CustomInterventionScreen({ 
  onBack, 
  onValidate, 
  userContext 
}: CustomInterventionScreenProps) {
  const [intervention, setIntervention] = useState<CustomIntervention>({
    name: '',
    description: '',
    habits: [''],
    startDate: new Date(),
    trialPeriodDays: 30,
    endDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000),
  });
  const [showDatePicker, setShowDatePicker] = useState(false);
  const { showToast } = useToast();
  const [isValidating, setIsValidating] = useState(false);

  const addHabit = () => {
    setIntervention(prev => ({
      ...prev,
      habits: [...prev.habits, '']
    }));
  };

  const removeHabit = (index: number) => {
    if (intervention.habits.length > 1) {
      setIntervention(prev => ({
        ...prev,
        habits: prev.habits.filter((_, i) => i !== index)
      }));
    }
  };

  const updateHabit = (index: number, value: string) => {
    setIntervention(prev => ({
      ...prev,
      habits: prev.habits.map((habit, i) => i === index ? value : habit)
    }));
  };

  const updateTrialPeriod = (days: number) => {
    const newEndDate = new Date(intervention.startDate);
    newEndDate.setDate(newEndDate.getDate() + days);
    
    setIntervention(prev => ({
      ...prev,
      trialPeriodDays: days,
      endDate: newEndDate
    }));
  };

  const onDateChange = (event: any, selectedDate?: Date) => {
    setShowDatePicker(false);
    if (selectedDate) {
      const newEndDate = new Date(selectedDate);
      newEndDate.setDate(newEndDate.getDate() + intervention.trialPeriodDays);
      
      setIntervention(prev => ({
        ...prev,
        startDate: selectedDate,
        endDate: newEndDate
      }));
    }
  };

  const validateIntervention = async () => {
    // Validate required fields
    if (!intervention.name.trim()) {
      showToast('Please enter an intervention name', 'warning');
      return;
    }
    
    if (!intervention.description.trim()) {
      showToast('Please enter a description', 'warning');
      return;
    }
    
    const validHabits = intervention.habits.filter(habit => habit.trim());
    if (validHabits.length === 0) {
      showToast('Please add at least one habit', 'warning');
      return;
    }

    setIsValidating(true);
    
    try {
      // Call RAG validation endpoint using centralized API service
      const validationResult = await apiService.validateCustomIntervention({
        intervention: {
          name: intervention.name.trim(),
          description: intervention.description.trim(),
          habits: validHabits,
          start_date: intervention.startDate.toISOString().split('T')[0],
          trial_period_days: intervention.trialPeriodDays,
        },
        user_context: userContext
      });
      
      // Show validation results
      Alert.alert(
        'Validation Complete',
        `Scientific Assessment: ${validationResult.assessment}\n\nRecommendations: ${validationResult.recommendations}`,
        [
          {
            text: 'Modify',
            style: 'cancel',
          },
          {
            text: 'Start Intervention',
            onPress: () => {
              onValidate({
                ...intervention,
                habits: validHabits
              });
              showToast('Custom intervention created successfully!', 'success');
            },
          },
        ]
      );
    } catch (error) {
      console.error('Validation error:', error);
      showToast(error instanceof Error ? error.message : 'Failed to validate intervention. Please try again.', 'error');
    } finally {
      setIsValidating(false);
    }
  };

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      >
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={styles.content}>
            {/* Header */}
            <View style={styles.header}>
              <TouchableOpacity onPress={onBack} style={styles.backButton}>
                <Ionicons name="arrow-back" size={24} color={colors.primary} />
              </TouchableOpacity>
              <Text style={styles.title}>Create Custom Intervention</Text>
              <View style={styles.placeholder} />
            </View>

            <ScrollView style={styles.scrollView} showsVerticalScrollIndicator={false}>
              {/* Intervention Name */}
              <View style={styles.section}>
                <Text style={styles.label}>Intervention Name *</Text>
                <TextInput
                  style={styles.input}
                  value={intervention.name}
                  onChangeText={(text) => setIntervention(prev => ({ ...prev, name: text }))}
                  placeholder="e.g., Mediterranean Diet Trial"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>

              {/* Description */}
              <View style={styles.section}>
                <Text style={styles.label}>Description *</Text>
                <TextInput
                  style={[styles.input, styles.textArea]}
                  value={intervention.description}
                  onChangeText={(text) => setIntervention(prev => ({ ...prev, description: text }))}
                  placeholder="Describe what this intervention aims to achieve..."
                  multiline
                  numberOfLines={4}
                  textAlignVertical="top"
                  placeholderTextColor={colors.textSecondary}
                />
              </View>

              {/* Start Date */}
              <View style={styles.section}>
                <Text style={styles.label}>Start Date *</Text>
                <TouchableOpacity 
                  style={styles.dateButton}
                  onPress={() => setShowDatePicker(true)}
                >
                  <Text style={styles.dateText}>
                    {intervention.startDate.toLocaleDateString()}
                  </Text>
                  <Ionicons name="calendar" size={20} color={colors.primary} />
                </TouchableOpacity>
              </View>

              {/* Trial Period */}
              <View style={styles.section}>
                <Text style={styles.label}>Trial Period (Days) *</Text>
                <View style={styles.trialPeriodContainer}>
                  {[14, 21, 30, 60, 90].map((days) => (
                    <TouchableOpacity
                      key={days}
                      style={[
                        styles.trialPeriodButton,
                        intervention.trialPeriodDays === days && styles.trialPeriodButtonSelected
                      ]}
                      onPress={() => updateTrialPeriod(days)}
                    >
                      <Text style={[
                        styles.trialPeriodText,
                        intervention.trialPeriodDays === days && styles.trialPeriodTextSelected
                      ]}>
                        {days}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
                <Text style={styles.trialPeriodInfo}>
                  Ends: {intervention.endDate.toLocaleDateString()}
                </Text>
              </View>

              {/* Habits */}
              <View style={styles.section}>
                <View style={styles.habitsHeader}>
                  <Text style={styles.label}>Habits to Track *</Text>
                  <TouchableOpacity style={styles.addHabitButton} onPress={addHabit}>
                    <Ionicons name="add" size={20} color={colors.primary} />
                    <Text style={styles.addHabitText}>Add Habit</Text>
                  </TouchableOpacity>
                </View>
                
                {intervention.habits.map((habit, index) => (
                  <View key={index} style={styles.habitRow}>
                    <TextInput
                      style={[styles.input, styles.habitInput]}
                      value={habit}
                      onChangeText={(text) => updateHabit(index, text)}
                      placeholder={`Habit ${index + 1}`}
                      placeholderTextColor={colors.textSecondary}
                    />
                    {intervention.habits.length > 1 && (
                      <TouchableOpacity 
                        style={styles.removeHabitButton}
                        onPress={() => removeHabit(index)}
                      >
                        <Ionicons name="close-circle" size={24} color={colors.error} />
                      </TouchableOpacity>
                    )}
                  </View>
                ))}
              </View>

              {/* Validation Button */}
              <TouchableOpacity 
                style={[styles.validateButton, isValidating && styles.validateButtonDisabled]}
                onPress={validateIntervention}
                disabled={isValidating}
              >
                <Ionicons 
                  name={isValidating ? "sync" : "checkmark-circle"} 
                  size={24} 
                  color="#FFFFFF" 
                  style={isValidating ? styles.spinning : undefined}
                />
                <Text style={styles.validateButtonText}>
                  {isValidating ? 'Validating...' : 'Validate with Expert'}
                </Text>
              </TouchableOpacity>
            </ScrollView>
          </View>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>

      {/* Date Picker Modal */}
      {showDatePicker && (
        <DateTimePicker
          value={intervention.startDate}
          mode="date"
          display="default"
          onChange={onDateChange}
          minimumDate={new Date()}
        />
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  content: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    padding: 8,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
  },
  placeholder: {
    width: 40,
  },
  scrollView: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    marginVertical: 16,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  input: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1F2937',
    backgroundColor: '#FFFFFF',
  },
  textArea: {
    minHeight: 100,
    textAlignVertical: 'top',
  },
  dateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#FFFFFF',
  },
  dateText: {
    fontSize: 16,
    color: '#1F2937',
  },
  trialPeriodContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 8,
  },
  trialPeriodButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
  },
  trialPeriodButtonSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  trialPeriodText: {
    fontSize: 14,
    color: '#6B7280',
    fontWeight: '500',
  },
  trialPeriodTextSelected: {
    color: '#FFFFFF',
  },
  trialPeriodInfo: {
    fontSize: 14,
    color: '#6B7280',
    fontStyle: 'italic',
  },
  habitsHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  addHabitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.primary,
    backgroundColor: '#F0F9FF',
  },
  addHabitText: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '500',
    marginLeft: 4,
  },
  habitRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  habitInput: {
    flex: 1,
    marginRight: 8,
  },
  removeHabitButton: {
    padding: 4,
  },
  validateButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    marginVertical: 24,
    gap: 8,
  },
  validateButtonDisabled: {
    backgroundColor: '#9CA3AF',
  },
  validateButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  spinning: {
    transform: [{ rotate: '360deg' }],
  },
});
