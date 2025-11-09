import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  TextInput,
  ScrollView,
} from 'react-native';
import { StoryIntakeData, INTERVENTION_OPTIONS, InterventionItem } from '../../types/StoryIntake';
import { colors } from '../../constants/colors';

interface InterventionsStepProps {
  data: StoryIntakeData;
  onUpdate: (data: Partial<StoryIntakeData>) => void;
  onNext: () => void;
  onBack: () => void;
}

export const InterventionsStep: React.FC<InterventionsStepProps> = ({
  data,
  onUpdate,
  onNext,
  onBack,
}) => {
  const [selectedInterventions, setSelectedInterventions] = useState<InterventionItem[]>(
    data.interventions.selected || []
  );
  const [additionalInterventions, setAdditionalInterventions] = useState(
    data.interventions.additional || ''
  );

  const handleInterventionToggle = (intervention: string) => {
    setSelectedInterventions(prev => {
      const existingIndex = prev.findIndex(item => item.intervention === intervention);
      if (existingIndex >= 0) {
        // Remove if already selected
        return prev.filter((_, index) => index !== existingIndex);
      } else {
        // Add with default helpful: false
        return [...prev, { intervention, helpful: false }];
      }
    });
  };

  const handleHelpfulnessToggle = (intervention: string, helpful: boolean) => {
    setSelectedInterventions(prev => 
      prev.map(item => 
        item.intervention === intervention 
          ? { ...item, helpful }
          : item
      )
    );
  };

  const isInterventionSelected = (intervention: string) => {
    return selectedInterventions.some(item => item.intervention === intervention);
  };

  const isInterventionHelpful = (intervention: string) => {
    const item = selectedInterventions.find(item => item.intervention === intervention);
    return item ? item.helpful : false;
  };

  const handleNext = () => {
    onUpdate({
      interventions: {
        selected: selectedInterventions,
        additional: additionalInterventions,
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
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={[styles.progressDot, styles.progressDotActive]} />
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
        </View>
      </View>

      {/* Content - Scrollable */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>What food interventions have you tried?</Text>
        <Text style={styles.subtitle}>
          {selectedInterventions.length > 0 
            ? `${selectedInterventions.length} intervention${selectedInterventions.length === 1 ? '' : 's'} selected` 
            : 'Select the dietary approaches you\'ve experimented with and tell us if they were helpful.'
          }
        </Text>

        {/* Interventions Grid */}
        <View style={styles.interventionsContainer}>
          <View style={styles.interventionsGrid}>
            {INTERVENTION_OPTIONS.map((intervention) => {
              const isSelected = isInterventionSelected(intervention);
              const isHelpful = isInterventionHelpful(intervention);
              
              return (
                <View key={intervention} style={styles.interventionItem}>
                  <TouchableOpacity
                    style={[
                      styles.interventionButton,
                      isSelected && styles.interventionButtonSelected,
                    ]}
                    onPress={() => handleInterventionToggle(intervention)}
                  >
                    <Text
                      style={[
                        styles.interventionButtonText,
                        isSelected && styles.interventionButtonTextSelected,
                      ]}
                    >
                      {intervention}
                    </Text>
                  </TouchableOpacity>
                  
                  {/* Helpfulness Toggle - only show if selected */}
                  {isSelected && (
                    <View style={styles.helpfulnessContainer}>
                      <Text style={styles.helpfulnessLabel}>Was this helpful?</Text>
                      <View style={styles.helpfulnessButtons}>
                        <TouchableOpacity
                          style={[
                            styles.helpfulnessButton,
                            isHelpful === true && styles.helpfulnessButtonActive,
                          ]}
                          onPress={() => handleHelpfulnessToggle(intervention, true)}
                        >
                          <Text
                            style={[
                              styles.helpfulnessButtonText,
                              isHelpful === true && styles.helpfulnessButtonTextActive,
                            ]}
                          >
                            Yes
                          </Text>
                        </TouchableOpacity>
                        <TouchableOpacity
                          style={[
                            styles.helpfulnessButton,
                            isHelpful === false && styles.helpfulnessButtonActive,
                          ]}
                          onPress={() => handleHelpfulnessToggle(intervention, false)}
                        >
                          <Text
                            style={[
                              styles.helpfulnessButtonText,
                              isHelpful === false && styles.helpfulnessButtonTextActive,
                            ]}
                          >
                            No
                          </Text>
                        </TouchableOpacity>
                      </View>
                    </View>
                  )}
                </View>
              );
            })}
          </View>
        </View>

        {/* Additional Interventions */}
        <View style={styles.additionalContainer}>
          <Text style={styles.additionalLabel}>Other interventions (optional)</Text>
          <Text style={styles.additionalHint}>
            Enter each intervention on a separate line
          </Text>
          <TextInput
            style={styles.additionalInput}
            placeholder="Enter each intervention on a separate line...&#10;&#10;Example:&#10;i tried hot water every morning&#10;i tried savoury breakfast instead of sweet breakfast"
            value={additionalInterventions}
            onChangeText={setAdditionalInterventions}
            multiline
            numberOfLines={5}
            textAlignVertical="top"
            placeholderTextColor="#9CA3AF"
          />
        </View>
      </ScrollView>

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
  interventionsContainer: {
    marginBottom: 20,
  },
  interventionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    paddingBottom: 20,
  },
  interventionItem: {
    width: '48%',
    marginBottom: 12,
  },
  interventionButton: {
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    backgroundColor: '#F9F9F9',
    alignItems: 'center',
    minHeight: 44,
    justifyContent: 'center',
  },
  interventionButtonSelected: {
    backgroundColor: '#FFE4D6',
    borderColor: colors.primary,
  },
  interventionButtonText: {
    fontSize: 13,
    color: '#666',
    fontWeight: '500',
    textAlign: 'center',
    lineHeight: 16,
  },
  interventionButtonTextSelected: {
    color: colors.primary,
    fontWeight: '600',
  },
  helpfulnessContainer: {
    marginTop: 8,
    paddingHorizontal: 4,
  },
  helpfulnessLabel: {
    fontSize: 12,
    color: '#666',
    marginBottom: 4,
    textAlign: 'center',
  },
  helpfulnessButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    gap: 8,
  },
  helpfulnessButton: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#E0E0E0',
    backgroundColor: '#F9F9F9',
    alignItems: 'center',
  },
  helpfulnessButtonActive: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  helpfulnessButtonText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  helpfulnessButtonTextActive: {
    color: '#FFFFFF',
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
  additionalHint: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
    fontStyle: 'italic',
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