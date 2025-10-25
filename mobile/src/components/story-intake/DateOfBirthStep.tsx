import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
} from 'react-native';
import { StoryIntakeData } from '../../types/StoryIntake';
import { colors } from '../../constants/colors';

interface DateOfBirthStepProps {
  data: StoryIntakeData;
  onUpdate: (data: Partial<StoryIntakeData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export const DateOfBirthStep: React.FC<DateOfBirthStepProps> = ({
  data,
  onUpdate,
  onNext,
  onBack,
}) => {
  const [selectedAge, setSelectedAge] = useState(data.profile.age || 25);

  const ages = Array.from({ length: 87 }, (_, i) => i + 13); // Ages 13-99

  const handleNext = () => {
    onUpdate({
      profile: {
        ...data.profile,
        age: selectedAge,
      },
    });
    onNext();
  };

  return (
    <SafeAreaView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>←</Text>
        </TouchableOpacity>
        <View style={styles.progressContainer}>
          <View style={styles.progressDot} />
          <View style={[styles.progressDot, styles.progressDotActive]} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
        </View>
      </View>

      {/* Content */}
      <View style={styles.content}>
        <Text style={styles.title}>How old are you?</Text>
        <Text style={styles.subtitle}>This helps us provide age-appropriate recommendations</Text>

        <View style={styles.agePickerContainer}>
          <ScrollView style={styles.agePicker} showsVerticalScrollIndicator={false}>
            {ages.map((age) => (
              <TouchableOpacity
                key={age}
                style={[
                  styles.ageOption,
                  selectedAge === age && styles.ageOptionSelected,
                ]}
                onPress={() => setSelectedAge(age)}
              >
                <Text
                  style={[
                    styles.ageOptionText,
                    selectedAge === age && styles.ageOptionTextSelected,
                  ]}
                >
                  {age} years old
                </Text>
              </TouchableOpacity>
            ))}
          </ScrollView>
        </View>
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
    justifyContent: 'center',
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
    marginBottom: 40,
  },
  agePickerContainer: {
    height: 300,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    padding: 16,
  },
  agePicker: {
    flex: 1,
  },
  ageOption: {
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 8,
    marginVertical: 2,
    backgroundColor: '#FFFFFF',
  },
  ageOptionSelected: {
    backgroundColor: colors.primary,
  },
  ageOptionText: {
    fontSize: 18,
    color: '#333',
    textAlign: 'center',
  },
  ageOptionTextSelected: {
    color: '#FFFFFF',
    fontWeight: '600',
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
