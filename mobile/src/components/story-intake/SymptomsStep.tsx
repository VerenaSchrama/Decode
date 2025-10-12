import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  TextInput,
  ScrollView,
  KeyboardAvoidingView,
  TouchableWithoutFeedback,
  Keyboard,
  Platform,
} from 'react-native';
import { StoryIntakeData, SYMPTOM_OPTIONS } from '../../types/StoryIntake';
import { colors } from '../../constants/colors';

interface SymptomsStepProps {
  data: StoryIntakeData;
  onUpdate: (data: Partial<StoryIntakeData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export const SymptomsStep: React.FC<SymptomsStepProps> = ({
  data,
  onUpdate,
  onNext,
  onBack,
}) => {
  const [selectedSymptoms, setSelectedSymptoms] = useState<string[]>(
    data.symptoms.selected || []
  );
  const [additionalSymptoms, setAdditionalSymptoms] = useState(
    data.symptoms.additional || ''
  );

  const handleSymptomToggle = (symptom: string) => {
    setSelectedSymptoms(prev => {
      if (prev.includes(symptom)) {
        return prev.filter(s => s !== symptom);
      } else {
        return [...prev, symptom];
      }
    });
  };

  const handleNext = () => {
    onUpdate({
      symptoms: {
        selected: selectedSymptoms,
        additional: additionalSymptoms,
      },
    });
    onNext();
  };

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
                <View style={styles.progressDot} />
                <View style={styles.progressDot} />
                <View style={styles.progressDot} />
                <View style={styles.progressDot} />
                <View style={[styles.progressDot, styles.progressDotActive]} />
                <View style={styles.progressDot} />
                <View style={styles.progressDot} />
                <View style={styles.progressDot} />
              </View>
            </View>

            {/* Content - Scrollable */}
            <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
              <Text style={styles.title}>Have you ever experienced any of the following symptoms?</Text>
              <Text style={styles.subtitle}>
                {selectedSymptoms.length > 0 
                  ? `${selectedSymptoms.length} symptom${selectedSymptoms.length === 1 ? '' : 's'} selected` 
                  : 'You can select more symptoms later.'
                }
              </Text>

              {/* Symptoms Grid */}
              <View style={styles.symptomsContainer}>
                <View style={styles.symptomsGrid}>
                  {SYMPTOM_OPTIONS.map((symptom) => (
                    <TouchableOpacity
                      key={symptom}
                      style={[
                        styles.symptomButton,
                        selectedSymptoms.includes(symptom) && styles.symptomButtonSelected,
                      ]}
                      onPress={() => handleSymptomToggle(symptom)}
                    >
                      <Text
                        style={[
                          styles.symptomButtonText,
                          selectedSymptoms.includes(symptom) && styles.symptomButtonTextSelected,
                        ]}
                      >
                        {symptom}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>

              {/* Additional Symptoms */}
              <View style={styles.additionalContainer}>
                <Text style={styles.additionalLabel}>Other symptoms (optional)</Text>
                <TextInput
                  style={styles.additionalInput}
                  placeholder="Describe any other symptoms..."
                  value={additionalSymptoms}
                  onChangeText={setAdditionalSymptoms}
                  multiline
                  numberOfLines={2}
                  returnKeyType="done"
                />
              </View>
            </ScrollView>

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
    backgroundColor: '#FFFFFF',
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
    paddingBottom: 20,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 12,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  symptomsContainer: {
    marginBottom: 20,
  },
  symptomsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingBottom: 20,
  },
  symptomButton: {
    width: '48%',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    backgroundColor: '#F9F9F9',
    marginBottom: 8,
    alignItems: 'center',
    minHeight: 44,
    justifyContent: 'center',
  },
  symptomButtonSelected: {
    backgroundColor: '#FFE4D6',
    borderColor: colors.primary,
  },
  symptomButtonText: {
    fontSize: 13,
    color: '#666',
    fontWeight: '500',
    textAlign: 'center',
    lineHeight: 16,
  },
  symptomButtonTextSelected: {
    color: colors.primary,
    fontWeight: '600',
  },
  additionalContainer: {
    marginBottom: 20,
  },
  additionalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  additionalInput: {
    borderWidth: 1,
    borderColor: '#E0E0E0',
    borderRadius: 8,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#F9F9F9',
    minHeight: 80,
    textAlignVertical: 'top',
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
});