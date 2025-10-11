import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
} from 'react-native';
import { SelectedHabit, HabitSelectionData } from '../types/StoryIntake';

interface HabitSelectionScreenProps {
  recommendedHabits: string[];
  onHabitsSelected: (selectedHabits: string[]) => void;
  onBack: () => void;
}

export default function HabitSelectionScreen({ 
  recommendedHabits, 
  onHabitsSelected, 
  onBack 
}: HabitSelectionScreenProps) {
  const [selectedHabits, setSelectedHabits] = useState<SelectedHabit[]>(
    recommendedHabits.map(habit => ({ habit, selected: false }))
  );

  const handleHabitToggle = (index: number) => {
    const updatedHabits = [...selectedHabits];
    updatedHabits[index].selected = !updatedHabits[index].selected;
    setSelectedHabits(updatedHabits);
  };

  const handleStartTracking = () => {
    const selectedHabitNames = selectedHabits
      .filter(habit => habit.selected)
      .map(habit => habit.habit);
    
    onHabitsSelected(selectedHabitNames);
  };

  const selectedCount = selectedHabits.filter(habit => habit.selected).length;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={onBack}>
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Choose Your Habits</Text>
          <Text style={styles.subtitle}>Select which habits you'd like to track daily</Text>
        </View>

        {/* Selection Info */}
        <View style={styles.infoCard}>
          <Text style={styles.infoTitle}>🎯 Personalize Your Journey</Text>
          <Text style={styles.infoText}>
            We've recommended {recommendedHabits.length} habits based on your profile. 
            Choose the ones you want to focus on and track daily.
          </Text>
          <Text style={styles.selectionCount}>
            {selectedCount} of {recommendedHabits.length} selected
          </Text>
        </View>

        {/* Habits List */}
        <View style={styles.habitsContainer}>
          {selectedHabits.map((habitItem, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.habitCard,
                habitItem.selected && styles.habitCardSelected
              ]}
              onPress={() => handleHabitToggle(index)}
            >
              <View style={styles.habitContent}>
                <View style={styles.habitHeader}>
                  <View style={styles.habitNumber}>
                    <Text style={styles.habitNumberText}>{index + 1}</Text>
                  </View>
                  <View style={styles.checkbox}>
                    {habitItem.selected && (
                      <Text style={styles.checkmark}>✓</Text>
                    )}
                  </View>
                </View>
                <Text style={[
                  styles.habitText,
                  habitItem.selected && styles.habitTextSelected
                ]}>
                  {habitItem.habit}
                </Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Action Buttons */}
        <View style={styles.actionsContainer}>
          <TouchableOpacity 
            style={[
              styles.primaryButton,
              selectedCount === 0 && styles.primaryButtonDisabled
            ]}
            onPress={handleStartTracking}
            disabled={selectedCount === 0}
          >
            <Text style={[
              styles.primaryButtonText,
              selectedCount === 0 && styles.primaryButtonTextDisabled
            ]}>
              {selectedCount === 0 
                ? 'Select at least one habit' 
                : `Start Tracking ${selectedCount} Habit${selectedCount > 1 ? 's' : ''}`
              }
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.secondaryButton} onPress={onBack}>
            <Text style={styles.secondaryButtonText}>Back to Recommendations</Text>
          </TouchableOpacity>
        </View>
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
    padding: 20,
    paddingBottom: 40,
  },
  header: {
    marginBottom: 24,
  },
  backButton: {
    alignSelf: 'flex-start',
    marginBottom: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: '#3b82f6',
    fontWeight: '500',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1f2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6b7280',
    lineHeight: 24,
  },
  infoCard: {
    backgroundColor: '#dbeafe',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
  },
  infoTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e40af',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#1e40af',
    lineHeight: 20,
    marginBottom: 12,
  },
  selectionCount: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e40af',
  },
  habitsContainer: {
    marginBottom: 32,
  },
  habitCard: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#e5e7eb',
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 1,
    },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 1,
  },
  habitCardSelected: {
    borderColor: '#3b82f6',
    backgroundColor: '#eff6ff',
  },
  habitContent: {
    flex: 1,
  },
  habitHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  habitNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#f3f4f6',
    justifyContent: 'center',
    alignItems: 'center',
  },
  habitNumberText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6b7280',
  },
  checkbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#d1d5db',
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  checkmark: {
    fontSize: 16,
    color: '#3b82f6',
    fontWeight: 'bold',
  },
  habitText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  habitTextSelected: {
    color: '#1e40af',
    fontWeight: '500',
  },
  actionsContainer: {
    gap: 12,
  },
  primaryButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
  },
  primaryButtonDisabled: {
    backgroundColor: '#d1d5db',
  },
  primaryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  primaryButtonTextDisabled: {
    color: '#9ca3af',
  },
  secondaryButton: {
    backgroundColor: 'transparent',
    borderRadius: 12,
    paddingVertical: 16,
    paddingHorizontal: 24,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#d1d5db',
  },
  secondaryButtonText: {
    color: '#6b7280',
    fontSize: 16,
    fontWeight: '500',
  },
});
