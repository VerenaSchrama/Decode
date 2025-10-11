import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  ScrollView,
} from 'react-native';
import { StoryIntakeData, DIETARY_PREFERENCE_OPTIONS } from '../../types/StoryIntake';
import { colors } from '../../constants/colors';

interface DietaryStepProps {
  data: StoryIntakeData;
  onUpdate: (data: Partial<StoryIntakeData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export function DietaryStep({ data, onUpdate, onNext, onBack }: DietaryStepProps) {
  const [selectedPreferences, setSelectedPreferences] = useState<string[]>(
    data.dietaryPreferences?.selected || []
  );
  const [additionalPreferences, setAdditionalPreferences] = useState(
    data.dietaryPreferences?.additional || ''
  );
  const [searchText, setSearchText] = useState('');

  const filteredPreferences = useMemo(() => {
    if (!searchText) return DIETARY_PREFERENCE_OPTIONS;
    return DIETARY_PREFERENCE_OPTIONS.filter(preference =>
      preference.toLowerCase().includes(searchText.toLowerCase())
    );
  }, [searchText]);

  const handlePreferenceToggle = (preference: string) => {
    setSelectedPreferences(prev => {
      if (prev.includes(preference)) {
        return prev.filter(p => p !== preference);
      } else {
        return [...prev, preference];
      }
    });
  };

  const handleNext = () => {
    onUpdate({
      dietaryPreferences: {
        selected: selectedPreferences,
        additional: additionalPreferences,
      },
    });
    onNext();
  };

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <TouchableOpacity onPress={onBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>Dietary Preferences</Text>
        <Text style={styles.subtitle}>
          {selectedPreferences.length > 0 
            ? `${selectedPreferences.length} preference${selectedPreferences.length === 1 ? '' : 's'} selected` 
            : 'Tell us about your dietary preferences and restrictions.'
          }
        </Text>
      </View>

      {/* Progress Dots */}
        <View style={styles.progressContainer}>
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={[styles.progressDot, styles.progressDotActive]} />
          <View style={styles.progressDot} />
        </View>

      {/* Content - Scrollable */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Search Input */}
        <View style={styles.searchContainer}>
          <TextInput
            style={styles.searchInput}
            placeholder="Search preferences..."
            value={searchText}
            onChangeText={setSearchText}
            placeholderTextColor="#999"
          />
        </View>

        {/* Preferences Grid */}
        <View style={styles.preferencesContainer}>
          <View style={styles.preferencesGrid}>
            {filteredPreferences.map((preference) => {
              const isSelected = selectedPreferences.includes(preference);
              
              return (
                <TouchableOpacity
                  key={preference}
                  style={[
                    styles.preferenceButton,
                    isSelected && styles.preferenceButtonSelected,
                  ]}
                  onPress={() => handlePreferenceToggle(preference)}
                >
                  <Text
                    style={[
                      styles.preferenceButtonText,
                      isSelected && styles.preferenceButtonTextSelected,
                    ]}
                  >
                    {preference}
                  </Text>
                </TouchableOpacity>
              );
            })}
          </View>
        </View>

        {/* Additional Preferences */}
        <View style={styles.additionalContainer}>
          <Text style={styles.additionalLabel}>Other dietary preferences (optional)</Text>
          <TextInput
            style={styles.additionalInput}
            placeholder="Describe any other dietary preferences or restrictions..."
            value={additionalPreferences}
            onChangeText={setAdditionalPreferences}
            multiline
            numberOfLines={3}
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
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 20,
    paddingBottom: 16,
    alignItems: 'center',
  },
  backButton: {
    alignSelf: 'flex-start',
    paddingVertical: 10,
    paddingHorizontal: 5,
    marginBottom: 10,
  },
  backButtonText: {
    fontSize: 16,
    color: '#6B7280',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#1F2937',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
    marginBottom: 16,
  },
  progressContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingBottom: 20,
    gap: 8,
  },
  progressDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: '#E5E7EB',
  },
  progressDotActive: {
    backgroundColor: colors.primary,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  searchContainer: {
    marginBottom: 20,
  },
  searchInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  preferencesContainer: {
    marginBottom: 24,
  },
  preferencesGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingBottom: 20,
  },
  preferenceButton: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    backgroundColor: '#F9F9F9',
    alignItems: 'center',
    minHeight: 44,
    justifyContent: 'center',
    width: '48%',
    marginBottom: 12,
  },
  preferenceButtonSelected: {
    backgroundColor: '#FFE4D6',
    borderColor: colors.primary,
  },
  preferenceButtonText: {
    fontSize: 13,
    color: '#666',
    fontWeight: '500',
    textAlign: 'center',
    lineHeight: 16,
  },
  preferenceButtonTextSelected: {
    color: colors.primary,
    fontWeight: '600',
  },
  additionalContainer: {
    marginBottom: 20,
  },
  additionalLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  additionalInput: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    textAlignVertical: 'top',
    minHeight: 80,
  },
  footer: {
    paddingHorizontal: 20,
    paddingVertical: 20,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  nextButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
  },
  nextButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
});