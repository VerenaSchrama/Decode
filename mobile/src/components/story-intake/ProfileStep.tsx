import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  StyleSheet,
  Switch,
} from 'react-native';
import { Profile } from '../../types/StoryIntake';

interface ProfileStepProps {
  data: Profile;
  onComplete: (data: Profile) => void;
}

export default function ProfileStep({ data, onComplete }: ProfileStepProps) {
  const [name, setName] = useState(data.name);
  const [dateOfBirth, setDateOfBirth] = useState(data.dateOfBirth || '');
  const [anonymous, setAnonymous] = useState(false);

  const handleComplete = () => {
    const profileData: Profile = {
      name: anonymous ? '' : name,
      dateOfBirth: dateOfBirth,
    };
    onComplete(profileData);
  };

  return (
    <View style={styles.container}>
      <View style={styles.card}>
        <Text style={styles.label}>What should we call you?</Text>
        <TextInput
          style={[styles.input, anonymous && styles.disabledInput]}
          value={name}
          onChangeText={setName}
          placeholder="Your name (optional)"
          placeholderTextColor="#9ca3af"
          editable={!anonymous}
        />
      </View>

      <View style={styles.card}>
        <Text style={styles.label}>Date of Birth</Text>
        <TextInput
          style={styles.input}
          value={dateOfBirth}
          onChangeText={setDateOfBirth}
          placeholder="YYYY-MM-DD"
          placeholderTextColor="#9ca3af"
          keyboardType="numeric"
          maxLength={10}
        />
        <Text style={styles.helperText}>This helps us provide age-appropriate recommendations</Text>
      </View>

      <View style={styles.card}>
        <View style={styles.switchContainer}>
          <View style={styles.switchTextContainer}>
            <Text style={styles.switchLabel}>Stay anonymous</Text>
            <Text style={styles.switchDescription}>
              We won't store your name, but you can still get personalized recommendations
            </Text>
          </View>
          <Switch
            value={anonymous}
            onValueChange={setAnonymous}
            trackColor={{ false: '#e5e7eb', true: '#3b82f6' }}
            thumbColor={anonymous ? '#ffffff' : '#f3f4f6'}
          />
        </View>
      </View>

    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    paddingBottom: 20,
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  label: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 12,
  },
  input: {
    borderWidth: 1,
    borderColor: '#d1d5db',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: '#1e293b',
    backgroundColor: '#ffffff',
  },
  disabledInput: {
    backgroundColor: '#f9fafb',
    color: '#9ca3af',
  },
  helperText: {
    fontSize: 14,
    color: '#64748b',
    marginTop: 8,
  },
  switchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  switchTextContainer: {
    flex: 1,
    marginRight: 16,
  },
  switchLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 4,
  },
  switchDescription: {
    fontSize: 14,
    color: '#64748b',
    lineHeight: 20,
  },
});
