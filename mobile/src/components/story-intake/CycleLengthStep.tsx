import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  TouchableOpacity,
  TextInput,
  KeyboardAvoidingView,
  TouchableWithoutFeedback,
  Keyboard,
  Platform,
} from 'react-native';
import { StoryIntakeData } from '../../types/StoryIntake';
import { colors } from '../../constants/colors';

interface CycleLengthStepProps {
  data: StoryIntakeData;
  onUpdate: (data: Partial<StoryIntakeData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export const CycleLengthStep: React.FC<CycleLengthStepProps> = ({
  data,
  onUpdate,
  onNext,
  onBack,
}) => {
  const [cycleLength, setCycleLength] = useState(data.lastPeriod?.cycleLength?.toString() || '');

  const handleNext = () => {
    onUpdate({
      lastPeriod: {
        ...data.lastPeriod,
        cycleLength: cycleLength ? parseInt(cycleLength, 10) : undefined,
      },
    });
    onNext();
  };

  const progress = 3; // Current step index (0-based)
  const totalSteps = 8; // Updated to 8 steps

  return (
    <SafeAreaView style={styles.container}>
      <KeyboardAvoidingView 
        style={styles.keyboardAvoidingView}
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={Platform.OS === 'ios' ? 0 : 20}
      >
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={styles.contentWrapper}>
            {/* Header */}
            <View style={styles.header}>
              <TouchableOpacity onPress={onBack} style={styles.backButton}>
                <Text style={styles.backButtonText}>←</Text>
              </TouchableOpacity>
              <View style={styles.progressContainer}>
                {Array.from({ length: totalSteps }).map((_, index) => (
                  <View
                    key={index}
                    style={[
                      styles.progressDot,
                      index === progress && styles.progressDotActive,
                    ]}
                  />
                ))}
              </View>
            </View>

            {/* Content */}
            <View style={styles.content}>
              <Text style={styles.title}>What's your average cycle length?</Text>
              <Text style={styles.subtitle}>
                Number of days from the start of one period to the start of the next
              </Text>

              <View style={styles.inputContainer}>
                <TextInput
                  style={styles.input}
                  value={cycleLength}
                  onChangeText={setCycleLength}
                  placeholder="28"
                  keyboardType="numeric"
                  maxLength={3}
                  placeholderTextColor="#999"
                  returnKeyType="done"
                  onSubmitEditing={handleNext}
                />
                <Text style={styles.unit}>days</Text>
              </View>

              <Text style={styles.helperText}>
                Most women have cycles between 21-35 days. If you're not sure, 28 days is a good average to start with.
              </Text>
            </View>

            {/* Footer */}
            <View style={styles.footer}>
              <TouchableOpacity style={styles.nextButton} onPress={handleNext}>
                <Text style={styles.nextButtonText}>Next</Text>
              </TouchableOpacity>
            </View>
          </View>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  keyboardAvoidingView: {
    flex: 1,
  },
  contentWrapper: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 20,
    paddingTop: 10,
    paddingBottom: 20,
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    fontSize: 24,
    color: '#1F2937',
    fontWeight: '600',
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  progressDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E5E7EB',
    marginHorizontal: 4,
  },
  progressDotActive: {
    backgroundColor: colors.primary,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
    justifyContent: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 40,
    lineHeight: 24,
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
  input: {
    fontSize: 48,
    fontWeight: 'bold',
    color: colors.textPrimary,
    textAlign: 'center',
    borderBottomWidth: 2,
    borderBottomColor: colors.primary,
    paddingBottom: 8,
    minWidth: 80,
  },
  unit: {
    fontSize: 24,
    color: '#6B7280',
    marginLeft: 12,
    fontWeight: '500',
  },
  helperText: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
    lineHeight: 20,
  },
  footer: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  nextButton: {
    backgroundColor: colors.primary,
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 12,
  },
  nextButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
  },
});
