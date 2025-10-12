import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';
import CalendarPicker from 'react-native-calendar-picker';

interface Intervention {
  id: number;
  name: string;
  profile_match: string;
  similarity_score: number;
  scientific_source: string;
  habits: Array<{
    number: number;
    description: string;
  }>;
}

interface InterventionPeriodScreenProps {
  intervention: Intervention;
  onPeriodSelected: (periodData: {
    intervention: Intervention;
    durationDays: number;
    startDate: string;
    endDate: string;
  }) => void;
  onBack: () => void;
}

const DURATION_OPTIONS = [
  { days: 7, label: '1 Week', description: 'Perfect for trying out' },
  { days: 14, label: '2 Weeks', description: 'Good for initial results' },
  { days: 30, label: '1 Month', description: 'Recommended duration' },
  { days: 60, label: '2 Months', description: 'For deeper changes' },
  { days: 90, label: '3 Months', description: 'Long-term commitment' },
];

export default function InterventionPeriodScreen({
  intervention,
  onPeriodSelected,
  onBack,
}: InterventionPeriodScreenProps) {
  const [selectedDuration, setSelectedDuration] = useState<number>(30);
  const [selectedDate, setSelectedDate] = useState<Date | null>(null);
  const [showCalendar, setShowCalendar] = useState(false);

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

  const handleContinue = () => {
    if (!selectedDate) {
      Alert.alert('Select Start Date', 'Please choose when you want to start this intervention.');
      return;
    }

    const endDate = calculateEndDate(selectedDate, selectedDuration);
    
    onPeriodSelected({
      intervention,
      durationDays: selectedDuration,
      startDate: selectedDate.toISOString().split('T')[0],
      endDate: endDate.toISOString().split('T')[0],
    });
  };

  const getDurationDescription = (days: number): string => {
    const option = DURATION_OPTIONS.find(opt => opt.days === days);
    return option?.description || '';
  };

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Ionicons name="arrow-back" size={24} color={colors.primary} />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Set Your Timeline</Text>
        <View style={styles.placeholder} />
      </View>

      {/* Intervention Summary */}
      <View style={styles.interventionCard}>
        <Text style={styles.interventionName}>{intervention.name}</Text>
        <Text style={styles.interventionDescription}>
          {intervention.profile_match.length > 150 
            ? `${intervention.profile_match.substring(0, 150)}...`
            : intervention.profile_match
          }
        </Text>
        <View style={styles.matchScore}>
          <Ionicons name="checkmark-circle" size={16} color="#10B981" />
          <Text style={styles.matchText}>
            {Math.round(intervention.similarity_score * 100)}% match
          </Text>
        </View>
      </View>

      {/* Duration Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>How long do you want to follow this intervention?</Text>
        <Text style={styles.sectionSubtitle}>
          Choose a duration that feels manageable for you
        </Text>
        
        <View style={styles.durationOptions}>
          {DURATION_OPTIONS.map((option) => (
            <TouchableOpacity
              key={option.days}
              style={[
                styles.durationOption,
                selectedDuration === option.days && styles.durationOptionSelected,
              ]}
              onPress={() => setSelectedDuration(option.days)}
            >
              <View style={styles.durationContent}>
                <Text style={[
                  styles.durationLabel,
                  selectedDuration === option.days && styles.durationLabelSelected,
                ]}>
                  {option.label}
                </Text>
                <Text style={[
                  styles.durationDescription,
                  selectedDuration === option.days && styles.durationDescriptionSelected,
                ]}>
                  {option.description}
                </Text>
              </View>
              {selectedDuration === option.days && (
                <Ionicons name="checkmark-circle" size={24} color={colors.primary} />
              )}
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* Start Date Selection */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>When do you want to start?</Text>
        <Text style={styles.sectionSubtitle}>
          Choose your start date to begin tracking your progress
        </Text>
        
        <TouchableOpacity
          style={styles.dateSelector}
          onPress={() => setShowCalendar(!showCalendar)}
        >
          <Ionicons name="calendar-outline" size={24} color={colors.primary} />
          <View style={styles.dateContent}>
            <Text style={styles.dateLabel}>
              {selectedDate ? formatDate(selectedDate) : 'Select start date'}
            </Text>
            {selectedDate && (
              <Text style={styles.endDateText}>
                Ends: {formatDate(calculateEndDate(selectedDate, selectedDuration))}
              </Text>
            )}
          </View>
          <Ionicons name="chevron-down" size={20} color="#6B7280" />
        </TouchableOpacity>

        {showCalendar && (
          <View style={styles.calendarContainer}>
            <CalendarPicker
              onDateChange={(date: Date) => {
                setSelectedDate(date);
                setShowCalendar(false);
              }}
              selectedDayColor={colors.primary}
              selectedDayTextColor="white"
              minDate={new Date()}
              maxDate={new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)} // 30 days from now
              textStyle={styles.calendarText}
              customDatesStyles={[
                {
                  date: new Date(),
                  style: {
                    backgroundColor: '#E5E7EB',
                    borderRadius: 16,
                  },
                  textStyle: {
                    color: '#6B7280',
                    fontWeight: 'bold',
                  },
                },
              ]}
            />
          </View>
        )}
      </View>

      {/* Summary */}
      {selectedDate && (
        <View style={styles.summaryCard}>
          <Text style={styles.summaryTitle}>Your Plan</Text>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Intervention:</Text>
            <Text style={styles.summaryValue}>{intervention.name}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Duration:</Text>
            <Text style={styles.summaryValue}>{selectedDuration} days</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>Start Date:</Text>
            <Text style={styles.summaryValue}>{formatDate(selectedDate)}</Text>
          </View>
          <View style={styles.summaryRow}>
            <Text style={styles.summaryLabel}>End Date:</Text>
            <Text style={styles.summaryValue}>
              {formatDate(calculateEndDate(selectedDate, selectedDuration))}
            </Text>
          </View>
        </View>
      )}

      {/* Continue Button */}
      <TouchableOpacity
        style={[
          styles.continueButton,
          !selectedDate && styles.continueButtonDisabled,
        ]}
        onPress={handleContinue}
        disabled={!selectedDate}
      >
        <Text style={[
          styles.continueButtonText,
          !selectedDate && styles.continueButtonTextDisabled,
        ]}>
          Start My Journey
        </Text>
        <Ionicons 
          name="arrow-forward" 
          size={20} 
          color={selectedDate ? "white" : "#9CA3AF"} 
        />
      </TouchableOpacity>
    </ScrollView>
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
    paddingTop: 60,
    paddingBottom: 20,
    backgroundColor: 'white',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  backButton: {
    padding: 8,
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  placeholder: {
    width: 40,
  },
  interventionCard: {
    backgroundColor: 'white',
    margin: 20,
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  interventionName: {
    fontSize: 20,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  interventionDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
    marginBottom: 12,
  },
  matchScore: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  matchText: {
    fontSize: 14,
    color: '#10B981',
    fontWeight: '500',
    marginLeft: 4,
  },
  section: {
    backgroundColor: 'white',
    marginHorizontal: 20,
    marginBottom: 20,
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 16,
  },
  durationOptions: {
    gap: 12,
  },
  durationOption: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  durationOptionSelected: {
    borderColor: colors.primary,
    backgroundColor: '#EFF6FF',
  },
  durationContent: {
    flex: 1,
  },
  durationLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
    marginBottom: 2,
  },
  durationLabelSelected: {
    color: colors.primary,
  },
  durationDescription: {
    fontSize: 14,
    color: '#6B7280',
  },
  durationDescriptionSelected: {
    color: colors.primary,
  },
  dateSelector: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    backgroundColor: '#F9FAFB',
  },
  dateContent: {
    flex: 1,
    marginLeft: 12,
  },
  dateLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
  },
  endDateText: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  calendarContainer: {
    marginTop: 16,
    backgroundColor: 'white',
    borderRadius: 8,
    padding: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  calendarText: {
    fontSize: 14,
    color: '#1F2937',
  },
  summaryCard: {
    backgroundColor: '#F0F9FF',
    margin: 20,
    padding: 20,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#BAE6FD',
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1E40AF',
    marginBottom: 16,
  },
  summaryRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  summaryLabel: {
    fontSize: 14,
    color: '#6B7280',
  },
  summaryValue: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1F2937',
  },
  continueButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    margin: 20,
    padding: 16,
    borderRadius: 12,
    gap: 8,
  },
  continueButtonDisabled: {
    backgroundColor: '#E5E7EB',
  },
  continueButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
  continueButtonTextDisabled: {
    color: '#9CA3AF',
  },
});
