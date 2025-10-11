import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TextInput,
  Alert,
} from 'react-native';
import { StoryIntakeData } from '../../types/StoryIntake';
import { colors } from '../../constants/colors';

interface LastPeriodStepProps {
  data: StoryIntakeData;
  onUpdate: (data: Partial<StoryIntakeData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export const LastPeriodStep: React.FC<LastPeriodStepProps> = ({
  data,
  onUpdate,
  onNext,
  onBack,
}) => {
  const [selectedDate, setSelectedDate] = useState(data.lastPeriod?.date || '');
  const [hasPeriod, setHasPeriod] = useState(data.lastPeriod?.hasPeriod ?? true);
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [dateError, setDateError] = useState('');

  const daysInMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1, 0).getDate();
  const firstDayOfMonth = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), 1).getDay();
  const monthNames = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const generateCalendarDays = () => {
    const days = [];
    
    // Add empty cells for days before the first day of the month
    for (let i = 0; i < firstDayOfMonth; i++) {
      days.push(null);
    }
    
    // Add days of the month
    for (let day = 1; day <= daysInMonth; day++) {
      days.push(day);
    }
    
    return days;
  };

  const handleDateSelect = (day: number) => {
    const selectedDateObj = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
    const today = new Date();
    today.setHours(0, 0, 0, 0); // Reset time to start of day for accurate comparison
    
    // Check if the selected date is in the future
    if (selectedDateObj > today) {
      setDateError('Please select a past date. Your last period cannot be in the future.');
      Alert.alert(
        'Invalid Date',
        'Please select a past date. Your last period cannot be in the future.',
        [{ text: 'OK' }]
      );
      return;
    }
    
    const dateStr = `${currentMonth.getFullYear()}-${String(currentMonth.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
    setSelectedDate(dateStr);
    setHasPeriod(true); // Reset to true when selecting a date
    setDateError(''); // Clear any previous error
  };

  const handleNext = () => {
    onUpdate({
      lastPeriod: {
        date: selectedDate,
        hasPeriod,
        cycleLength: data.lastPeriod?.cycleLength, // Keep existing cycle length
      },
    });
    onNext();
  };

  const handleNoPeriod = () => {
    setHasPeriod(false);
    setSelectedDate('');
  };

  const navigateMonth = (direction: 'prev' | 'next') => {
    const newMonth = new Date(currentMonth);
    if (direction === 'prev') {
      newMonth.setMonth(newMonth.getMonth() - 1);
    } else {
      newMonth.setMonth(newMonth.getMonth() + 1);
    }
    setCurrentMonth(newMonth);
  };

  const calendarDays = generateCalendarDays();

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <View style={styles.progressContainer}>
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={[styles.progressDot, styles.progressDotActive]} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
        </View>
      </View>

      {/* Content */}
      <View style={styles.content}>
        <Text style={styles.title}>When did your last period begin?</Text>
        <View style={styles.infoContainer}>
          <View style={styles.infoIcon}>
            <Text style={styles.infoIconText}>i</Text>
          </View>
          <Text style={styles.infoText}>You can adjust this later.</Text>
        </View>

        {/* Calendar */}
        <View style={[
          styles.calendarContainer,
          !hasPeriod && styles.calendarContainerDisabled
        ]}>
          {/* Month Navigation */}
          <View style={styles.monthHeader}>
            <TouchableOpacity 
              onPress={() => navigateMonth('prev')}
              disabled={!hasPeriod}
            >
              <Text style={[
                styles.monthNavButton,
                !hasPeriod && styles.monthNavButtonDisabled
              ]}>←</Text>
            </TouchableOpacity>
            <Text style={[
              styles.monthTitle,
              !hasPeriod && styles.monthTitleDisabled
            ]}>
              {monthNames[currentMonth.getMonth()]} {currentMonth.getFullYear()}
            </Text>
            <TouchableOpacity 
              onPress={() => navigateMonth('next')}
              disabled={!hasPeriod}
            >
              <Text style={[
                styles.monthNavButton,
                !hasPeriod && styles.monthNavButtonDisabled
              ]}>→</Text>
            </TouchableOpacity>
          </View>

          {/* Days of Week */}
          <View style={styles.daysOfWeek}>
            {['M', 'T', 'W', 'T', 'F', 'S', 'S'].map((day, index) => (
              <Text key={index} style={styles.dayOfWeekText}>{day}</Text>
            ))}
          </View>

          {/* Calendar Grid */}
          <View style={styles.calendarGrid}>
            {calendarDays.map((day, index) => {
              if (day === null) {
                return <View key={index} style={styles.calendarDay} />;
              }
              
              const isSelected = selectedDate === `${currentMonth.getFullYear()}-${String(currentMonth.getMonth() + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
              const selectedDateObj = new Date(currentMonth.getFullYear(), currentMonth.getMonth(), day);
              const today = new Date();
              today.setHours(0, 0, 0, 0);
              const isPast = selectedDateObj <= today;
              const isFuture = selectedDateObj > today;
              
              return (
                <TouchableOpacity
                  key={index}
                  style={[
                    styles.calendarDay,
                    isSelected && styles.calendarDaySelected,
                    (!hasPeriod || isFuture) && styles.calendarDayDisabled,
                  ]}
                  onPress={() => handleDateSelect(day)}
                  disabled={!hasPeriod || isFuture}
                >
                  <Text style={[
                    styles.calendarDayText,
                    isSelected && styles.calendarDayTextSelected,
                    isFuture && styles.calendarDayTextDisabled,
                  ]}>
                    {day}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {/* Error Message */}
        {dateError ? (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>{dateError}</Text>
          </View>
        ) : null}

        {/* No Period Option */}
        <TouchableOpacity 
          style={[
            styles.noPeriodButton,
            !hasPeriod && styles.noPeriodButtonSelected
          ]} 
          onPress={handleNoPeriod}
        >
          <Text style={[
            styles.noPeriodText,
            !hasPeriod && styles.noPeriodTextSelected
          ]}>
            I don't have a period
          </Text>
        </TouchableOpacity>

      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <TouchableOpacity style={styles.nextButton} onPress={handleNext}>
          <Text style={styles.nextButtonText}>Next</Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 10,
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    fontSize: 24,
    color: '#333',
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#FFE4D6',
    marginHorizontal: 2,
  },
  progressDotActive: {
    backgroundColor: colors.primary,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 12,
  },
  infoContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 30,
  },
  infoIcon: {
    width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: '#333',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 8,
  },
  infoIconText: {
    color: '#FFFFFF',
    fontSize: 12,
    fontWeight: 'bold',
  },
  infoText: {
    fontSize: 14,
    color: '#666',
  },
  calendarContainer: {
    backgroundColor: '#F9F9F9',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
  },
  calendarContainerDisabled: {
    opacity: 0.5,
  },
  monthHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  monthNavButton: {
    fontSize: 20,
    color: '#333',
    padding: 8,
  },
  monthTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  monthTitleDisabled: {
    color: '#999',
  },
  monthNavButtonDisabled: {
    color: '#999',
  },
  daysOfWeek: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    marginBottom: 8,
  },
  dayOfWeekText: {
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    width: 40,
    textAlign: 'center',
  },
  calendarGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
  },
  calendarDay: {
    width: 40,
    height: 40,
    alignItems: 'center',
    justifyContent: 'center',
    margin: 2,
  },
  calendarDaySelected: {
    backgroundColor: colors.primary,
    borderRadius: 20,
  },
  calendarDayDisabled: {
    opacity: 0.3,
  },
  calendarDayText: {
    fontSize: 16,
    color: '#333',
  },
  calendarDayTextSelected: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  noPeriodButton: {
    alignItems: 'center',
    marginBottom: 20,
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  noPeriodButtonSelected: {
    backgroundColor: colors.primary,
  },
  noPeriodText: {
    fontSize: 16,
    color: colors.primary,
    fontWeight: '500',
  },
  noPeriodTextSelected: {
    color: '#FFFFFF',
    fontWeight: '600',
  },
  cycleLengthContainer: {
    marginTop: 20,
    paddingHorizontal: 20,
  },
  cycleLengthLabel: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
    textAlign: 'center',
  },
  cycleLengthSubtext: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 16,
    textAlign: 'center',
  },
  cycleLengthInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  cycleLengthInput: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    textAlign: 'center',
    minWidth: 60,
  },
  cycleLengthUnit: {
    fontSize: 16,
    color: '#6B7280',
    marginLeft: 8,
  },
  footer: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  nextButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  nextButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  errorContainer: {
    marginTop: 12,
    paddingHorizontal: 20,
  },
  errorText: {
    color: '#DC2626',
    fontSize: 14,
    textAlign: 'center',
    backgroundColor: '#FEF2F2',
    padding: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FECACA',
  },
  calendarDayTextDisabled: {
    color: '#D1D5DB',
  },
});
