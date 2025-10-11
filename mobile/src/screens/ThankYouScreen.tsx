import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  SafeAreaView,
  ScrollView,
} from 'react-native';
import RenderHtml from 'react-native-render-html';
import { StoryIntakeData } from '../types/StoryIntake';
import { colors } from '../constants/colors';

interface ThankYouScreenProps {
  onViewRecommendations: () => void;
  intakeData?: StoryIntakeData;
}

export default function ThankYouScreen({ onViewRecommendations, intakeData }: ThankYouScreenProps) {
  // Build welcoming profile summary like a nutritional coach
  const buildProfileSummary = () => {
    if (!intakeData) return "Hi there! I'm glad you've taken this step towards better health.";
    
    const name = intakeData.profile?.name || "there";
    const summaryParts = [`Hi ${name}! I'm glad you've taken this step towards better health.`];
    
    // Acknowledge their challenges with empathy
    if (intakeData.symptoms?.selected?.length > 0) {
      const symptomList = intakeData.symptoms.selected.map(symptom => `<b>${symptom}</b>`).join(', ');
      summaryParts.push(`I can see you're navigating ${symptomList} - I know these can feel overwhelming, but you're not alone in this journey.`);
    }
    if (intakeData.symptoms?.additional) {
      summaryParts.push(`I also understand you're dealing with ${intakeData.symptoms.additional} - every challenge you face is valid and important.`);
    }
    
    // Acknowledge their efforts if they've tried interventions
    if (intakeData.interventions?.selected?.length > 0) {
      const interventionNames = intakeData.interventions.selected.map(item => {
        const intervention = typeof item === 'string' ? item : item.intervention;
        return `<b>${intervention}</b>`;
      });
      summaryParts.push(`I appreciate that you've already explored ${interventionNames.join(', ')} - every step you've taken matters.`);
    }
    
    // Acknowledge their dietary preferences with encouragement
    if (intakeData.dietaryPreferences?.selected?.length > 0) {
      const dietaryPrefs = intakeData.dietaryPreferences.selected.map(pref => `<b>${pref}</b>`).join(', ');
      summaryParts.push(`Your ${dietaryPrefs} approach shows real commitment to nourishing your body well.`);
    }
    if (intakeData.dietaryPreferences?.additional) {
      summaryParts.push(`Your additional dietary notes about ${intakeData.dietaryPreferences.additional} show thoughtful consideration of your unique needs.`);
    }
    
    // Add cycle awareness if applicable
    if (intakeData.lastPeriod) {
      if (!intakeData.lastPeriod.hasPeriod) {
        summaryParts.push("I understand that menstrual cycles aren't part of your experience, and that's completely valid - we'll focus on optimizing your overall hormonal health.");
      } else if (intakeData.lastPeriod.date && intakeData.lastPeriod.cycleLength) {
        // Calculate cycle phase (simplified)
        const lastPeriodDate = new Date(intakeData.lastPeriod.date);
        const today = new Date();
        const daysSince = Math.floor((today.getTime() - lastPeriodDate.getTime()) / (1000 * 60 * 60 * 24));
        const currentDay = (daysSince % intakeData.lastPeriod.cycleLength) + 1;
        const daysUntilNext = intakeData.lastPeriod.cycleLength - currentDay + 1;
        
        let phase = "unknown phase";
        if (currentDay <= 5) phase = "menstrual phase";
        else if (currentDay <= 13) phase = "follicular phase";
        else if (currentDay <= 16) phase = "ovulatory phase";
        else if (currentDay <= intakeData.lastPeriod.cycleLength - 5) phase = "luteal phase";
        else phase = "pre-menstrual phase";
        
        const phaseBold = `<b>${phase}</b>`;
        summaryParts.push(`Based on your cycle timing, you're currently in the ${phaseBold} - this gives us valuable insight into your current hormonal landscape.`);
      }
    }
    
    // End with encouragement
    summaryParts.push("Together, we'll create a personalized approach that honors your unique needs and helps you feel your absolute best.");
    
    return summaryParts.join(' ');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        <View style={styles.iconContainer}>
          <Text style={styles.icon}>🌱</Text>
        </View>
        
        <Text style={styles.title}>Thank You!</Text>
        
        {/* Profile Summary */}
        <View style={styles.summaryContainer}>
          <Text style={styles.summaryTitle}>Your Profile Summary</Text>
          <RenderHtml
            contentWidth={300}
            source={{ html: buildProfileSummary() }}
            tagsStyles={{
              b: {
                fontWeight: 'bold',
                color: '#1f2937',
              }
            }}
            baseStyle={{
              fontSize: 16,
              lineHeight: 24,
              color: '#6b7280',
              fontStyle: 'italic',
            }}
          />
        </View>
        
        <View style={styles.messageContainer}>
          <Text style={styles.message}>
            Thank you for your contribution on behalf of all women with similar struggles! 
            Please press the button below to find the recommendations that best match your profile.
          </Text>
        </View>

        <View style={styles.benefitsContainer}>
          <Text style={styles.benefitsTitle}>Your contribution helps:</Text>
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>👥</Text>
            <Text style={styles.benefitText}>Other women find personalized solutions</Text>
          </View>
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>🔬</Text>
            <Text style={styles.benefitText}>Improve our AI recommendations</Text>
          </View>
          <View style={styles.benefitItem}>
            <Text style={styles.benefitIcon}>💪</Text>
            <Text style={styles.benefitText}>Advance women's health research</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.recommendationsButton} onPress={onViewRecommendations}>
          <Text style={styles.recommendationsButtonText}>
            View My Recommendations
          </Text>
        </TouchableOpacity>
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
    flexGrow: 1,
    paddingHorizontal: 24,
    paddingVertical: 40,
    alignItems: 'center',
  },
  iconContainer: {
    width: 120,
    height: 120,
    borderRadius: 60,
    backgroundColor: '#ffffff',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 32,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 4,
  },
  icon: {
    fontSize: 48,
  },
  title: {
    fontSize: 32,
    fontWeight: '700',
    color: '#1e293b',
    textAlign: 'center',
    marginBottom: 24,
  },
  messageContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 24,
    marginBottom: 32,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  message: {
    fontSize: 18,
    lineHeight: 28,
    color: '#374151',
    textAlign: 'center',
    fontWeight: '500',
  },
  benefitsContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 24,
    marginBottom: 32,
    width: '100%',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  benefitsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 16,
    textAlign: 'center',
  },
  benefitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  benefitIcon: {
    fontSize: 20,
    marginRight: 12,
    width: 24,
  },
  benefitText: {
    fontSize: 16,
    color: '#374151',
    flex: 1,
  },
  summaryContainer: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 24,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
  },
  summaryTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 12,
    textAlign: 'center',
  },
  summaryText: {
    fontSize: 16,
    lineHeight: 24,
    color: colors.textSecondary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  recommendationsButton: {
    backgroundColor: colors.primary,
    borderRadius: 16,
    paddingVertical: 18,
    paddingHorizontal: 32,
    shadowColor: colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4,
  },
  recommendationsButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: '#ffffff',
    textAlign: 'center',
  },
});

