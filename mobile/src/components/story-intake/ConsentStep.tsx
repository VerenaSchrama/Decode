import React, { useState } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  Switch,
  ScrollView,
} from 'react-native';
import { StoryIntakeData } from '../../types/StoryIntake';
import { colors } from '../../constants/colors';

interface ConsentStepProps {
  data: StoryIntakeData;
  onUpdate: (data: Partial<StoryIntakeData>) => void;
  onNext: () => void;
  onBack: () => void;
  onComplete: (data: StoryIntakeData) => void;
}

export const ConsentStep: React.FC<ConsentStepProps> = ({
  data,
  onUpdate,
  onNext,
  onBack,
  onComplete,
}) => {
  const [consent, setConsent] = useState(data.consent || false);
  // Anonymous functionality removed - all users are authenticated
  const [anonymous, setAnonymous] = useState(false); // Keep for compatibility but always false

  const handleComplete = () => {
    const updatedData = {
      ...data,
      consent,
      // anonymous field removed - all users are authenticated
    };
    onUpdate(updatedData);
    onComplete(updatedData);
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
          <View style={styles.progressDot} />
          <View style={styles.progressDot} />
          <View style={[styles.progressDot, styles.progressDotActive]} />
        </View>
      </View>

      {/* Content */}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        <Text style={styles.title}>Consent & Privacy</Text>
        <Text style={styles.subtitle}>Your data, your choice</Text>

        <View style={styles.card}>
          <Text style={styles.cardTitle}>Data Privacy & Consent</Text>
          <Text style={styles.cardDescription}>
            We respect your privacy and want you to understand how we use your information.
          </Text>
          
          <View style={styles.privacySection}>
            <Text style={styles.privacyTitle}>How we use your data:</Text>
            <Text style={styles.privacyText}>
              • Generate personalized health recommendations based on your unique profile
            </Text>
            <Text style={styles.privacyText}>
              • Improve our AI system to help other women with similar health challenges
            </Text>
            <Text style={styles.privacyText}>
              • Store your data securely in our encrypted database
            </Text>
            <Text style={styles.privacyText}>
              • Never share your personal information with third parties
            </Text>
          </View>

          <View style={styles.privacySection}>
            <Text style={styles.privacyTitle}>Your rights:</Text>
            <Text style={styles.privacyText}>
              • You can request to delete your data at any time
            </Text>
            {/* Anonymous option removed - all users are authenticated */}
          </View>
        </View>

        {/* Anonymous toggle removed - all users are authenticated */}

        <View style={styles.card}>
          <View style={styles.consentContainer}>
            <View style={styles.consentTextContainer}>
              <Text style={styles.consentLabel}>
                I consent to sharing my health data to help improve recommendations for women with similar challenges
              </Text>
            </View>
            <Switch
              value={consent}
              onValueChange={setConsent}
              trackColor={{ false: '#e5e7eb', true: '#10b981' }}
              thumbColor={consent ? '#ffffff' : '#f3f4f6'}
            />
          </View>
        </View>
      </ScrollView>

      {/* Footer */}
      <View style={styles.footer}>
        <TouchableOpacity 
          style={[
            styles.finishButton,
            !consent && styles.finishButtonDisabled
          ]} 
          onPress={handleComplete}
          disabled={!consent}
        >
          <Text style={styles.finishButtonText}>
            Complete Story Intake
          </Text>
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
  subtitle: {
    fontSize: 16,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  card: {
    backgroundColor: '#F9F9F9',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  cardDescription: {
    fontSize: 14,
    color: '#666',
    marginBottom: 16,
    lineHeight: 20,
  },
  privacySection: {
    marginBottom: 16,
  },
  privacyTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#333',
    marginBottom: 8,
  },
  privacyText: {
    fontSize: 13,
    color: '#666',
    lineHeight: 18,
    marginBottom: 4,
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
    color: '#333',
    marginBottom: 4,
  },
  switchDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 20,
  },
  consentContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  consentTextContainer: {
    flex: 1,
    marginRight: 16,
  },
  consentLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    lineHeight: 22,
  },
  footer: {
    paddingHorizontal: 20,
    paddingBottom: 40,
  },
  finishButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
  },
  finishButtonDisabled: {
    backgroundColor: '#E0E0E0',
  },
  finishButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
});