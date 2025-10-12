import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TextInput,
  TouchableOpacity,
  ScrollView,
  Alert,
  KeyboardAvoidingView,
  Platform,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';

interface Habit {
  number: number;
  description: string;
}

interface SubmitInterventionScreenProps {
  onBack: () => void;
  onSubmit: (intervention: {
    name: string;
    description: string;
    profile_match: string;
    scientific_source?: string;
    habits: Habit[];
  }) => void;
}

export default function SubmitInterventionScreen({
  onBack,
  onSubmit,
}: SubmitInterventionScreenProps) {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [profileMatch, setProfileMatch] = useState('');
  const [scientificSource, setScientificSource] = useState('');
  const [habits, setHabits] = useState<Habit[]>([
    { number: 1, description: '' },
    { number: 2, description: '' },
    { number: 3, description: '' },
    { number: 4, description: '' },
    { number: 5, description: '' },
  ]);

  const updateHabit = (index: number, description: string) => {
    const newHabits = [...habits];
    newHabits[index] = { ...newHabits[index], description };
    setHabits(newHabits);
  };

  const handleSubmit = () => {
    // Validation
    if (!name.trim()) {
      Alert.alert('Error', 'Please enter an intervention name');
      return;
    }
    if (!description.trim()) {
      Alert.alert('Error', 'Please enter a description');
      return;
    }
    if (!profileMatch.trim()) {
      Alert.alert('Error', 'Please describe who this intervention is for');
      return;
    }
    
    const validHabits = habits.filter(habit => habit.description.trim());
    if (validHabits.length < 3) {
      Alert.alert('Error', 'Please provide at least 3 habits');
      return;
    }

    // Submit intervention
    onSubmit({
      name: name.trim(),
      description: description.trim(),
      profile_match: profileMatch.trim(),
      scientific_source: scientificSource.trim() || undefined,
      habits: validHabits,
    });
  };

  return (
    <KeyboardAvoidingView 
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView style={styles.scrollView}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity onPress={onBack} style={styles.backButton}>
            <Ionicons name="arrow-back" size={24} color={colors.primary} />
          </TouchableOpacity>
          <Text style={styles.headerTitle}>Share Your Intervention</Text>
          <View style={styles.placeholder} />
        </View>

        {/* Form */}
        <View style={styles.form}>
          {/* Intervention Name */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Intervention Name *</Text>
            <TextInput
              style={styles.input}
              value={name}
              onChangeText={setName}
              placeholder="e.g., Intermittent Fasting for PCOS"
              placeholderTextColor="#9CA3AF"
            />
          </View>

          {/* Description */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Description *</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              value={description}
              onChangeText={setDescription}
              placeholder="Brief description of what this intervention involves..."
              placeholderTextColor="#9CA3AF"
              multiline
              numberOfLines={3}
            />
          </View>

          {/* Profile Match */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Who is this for? *</Text>
            <TextInput
              style={[styles.input, styles.textArea]}
              value={profileMatch}
              onChangeText={setProfileMatch}
              placeholder="Describe the type of person who would benefit from this intervention..."
              placeholderTextColor="#9CA3AF"
              multiline
              numberOfLines={4}
            />
          </View>

          {/* Scientific Source */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Scientific Source (Optional)</Text>
            <TextInput
              style={styles.input}
              value={scientificSource}
              onChangeText={setScientificSource}
              placeholder="e.g., https://pubmed.ncbi.nlm.nih.gov/12345678/"
              placeholderTextColor="#9CA3AF"
            />
          </View>

          {/* Habits */}
          <View style={styles.inputGroup}>
            <Text style={styles.label}>Habits (at least 3) *</Text>
            {habits.map((habit, index) => (
              <View key={index} style={styles.habitInput}>
                <Text style={styles.habitNumber}>{habit.number}.</Text>
                <TextInput
                  style={[styles.input, styles.habitTextInput]}
                  value={habit.description}
                  onChangeText={(text) => updateHabit(index, text)}
                  placeholder={`Habit ${habit.number} description...`}
                  placeholderTextColor="#9CA3AF"
                />
              </View>
            ))}
          </View>
        </View>

        {/* Submit Button */}
        <TouchableOpacity style={styles.submitButton} onPress={handleSubmit}>
          <Text style={styles.submitButtonText}>Submit for Review</Text>
          <Ionicons name="send" size={20} color="white" />
        </TouchableOpacity>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  scrollView: {
    flex: 1,
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
  form: {
    padding: 20,
  },
  inputGroup: {
    marginBottom: 24,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'white',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    color: '#1F2937',
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  habitInput: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  habitNumber: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
    marginRight: 8,
    marginTop: 12,
    minWidth: 20,
  },
  habitTextInput: {
    flex: 1,
  },
  submitButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.primary,
    margin: 20,
    padding: 16,
    borderRadius: 12,
    gap: 8,
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: 'white',
  },
});
