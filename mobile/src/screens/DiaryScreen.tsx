import React, { useState, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Dimensions,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';
import { RouteProp } from '@react-navigation/native';

interface DiaryScreenProps {
  route?: RouteProp<{ params: { intakeData?: any } }, 'params'>;
}

interface AnalyticsData {
  moodTrend: { date: string; mood: number }[];
  habitStreaks: { habit: string; currentStreak: number; longestStreak: number }[];
  symptomFrequency: { symptom: string; count: number; percentage: number }[];
  weeklyProgress: { week: string; averageMood: number; habitCompletion: number }[];
  insights: string[];
  achievements: { title: string; description: string; unlocked: boolean }[];
}

export default function DiaryScreen({ route }: DiaryScreenProps) {
  const intakeData = route?.params?.intakeData;
  const [selectedTimeframe, setSelectedTimeframe] = useState<'week' | 'month' | 'all'>('week');
  
  // Sample analytics data for a new user - in a real app, this would come from the backend
  const analyticsData: AnalyticsData = useMemo(() => ({
    moodTrend: [
      // Empty for new user - will populate as they track
    ],
    habitStreaks: [
      { habit: 'Eat with your cycle', currentStreak: 0, longestStreak: 0 },
      { habit: 'Control your blood sugar', currentStreak: 0, longestStreak: 0 },
      { habit: 'Mediterranean Diet', currentStreak: 0, longestStreak: 0 },
    ],
    symptomFrequency: [
      // Empty for new user - will populate as they track symptoms
    ],
    weeklyProgress: [
      // Empty for new user - will populate as they track progress
    ],
    insights: [
      "Start by tracking your daily mood and symptoms to build insights",
      "Complete your first habit to begin building streaks",
      "The app will learn your patterns as you use it more",
      "Check back here for personalized insights as you progress",
    ],
    achievements: [
      { title: "First Steps", description: "Complete your first habit", unlocked: false },
      { title: "Mood Tracker", description: "Log your mood for 3 days", unlocked: false },
      { title: "Habit Builder", description: "Complete habits for 7 days in a row", unlocked: false },
      { title: "Streak Champion", description: "Maintain a 14-day habit streak", unlocked: false },
    ],
  }), []);

  const getMoodEmoji = (mood: number) => {
    const moods = ['😢', '😔', '😐', '😊', '😄'];
    return moods[mood - 1] || '😐';
  };

  const getMoodLabel = (mood: number) => {
    const labels = ['Very Bad', 'Bad', 'Okay', 'Good', 'Great'];
    return labels[mood - 1] || 'Okay';
  };

  const getMoodColor = (mood: number) => {
    const colors = ['#EF4444', '#F59E0B', '#6B7280', '#10B981', '#059669'];
    return colors[mood - 1] || '#6B7280';
  };

  const screenWidth = Dimensions.get('window').width;

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Analytics & Insights</Text>
          <Text style={styles.subtitle}>
            Track your progress and discover patterns
          </Text>
        </View>

        {/* Timeframe Selector */}
        <View style={styles.timeframeSelector}>
          {(['week', 'month', 'all'] as const).map((timeframe) => (
            <TouchableOpacity
              key={timeframe}
              style={[
                styles.timeframeButton,
                selectedTimeframe === timeframe && styles.timeframeButtonSelected
              ]}
              onPress={() => setSelectedTimeframe(timeframe)}
            >
              <Text style={[
                styles.timeframeButtonText,
                selectedTimeframe === timeframe && styles.timeframeButtonTextSelected
              ]}>
                {timeframe.charAt(0).toUpperCase() + timeframe.slice(1)}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Mood Trend Chart */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Mood Trend</Text>
          <View style={styles.moodChart}>
            {analyticsData.moodTrend.map((data, index) => (
              <View key={index} style={styles.moodBar}>
                <View
                  style={[
                    styles.moodBarFill,
                    {
                      height: (data.mood / 5) * 60,
                      backgroundColor: getMoodColor(data.mood),
                    }
                  ]}
                />
                <Text style={styles.moodBarLabel}>
                  {new Date(data.date).getDate()}
                </Text>
                <Text style={styles.moodBarEmoji}>
                  {getMoodEmoji(data.mood)}
                </Text>
              </View>
            ))}
          </View>
        </View>

        {/* Habit Streaks */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Habit Streaks</Text>
          {analyticsData.habitStreaks.map((streak, index) => (
            <View key={index} style={styles.streakItem}>
              <View style={styles.streakInfo}>
                <Text style={styles.streakHabit}>{streak.habit}</Text>
                <Text style={styles.streakStats}>
                  Current: {streak.currentStreak} days | Best: {streak.longestStreak} days
                </Text>
              </View>
              <View style={styles.streakProgress}>
                <View style={styles.streakProgressBar}>
                  <View
                    style={[
                      styles.streakProgressFill,
                      { width: `${(streak.currentStreak / Math.max(streak.longestStreak, 1)) * 100}%` }
                    ]}
                  />
                </View>
              </View>
            </View>
          ))}
        </View>

        {/* Symptom Analysis */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Symptom Frequency</Text>
          {analyticsData.symptomFrequency.map((symptom, index) => (
            <View key={index} style={styles.symptomItem}>
              <View style={styles.symptomInfo}>
                <Text style={styles.symptomName}>{symptom.symptom}</Text>
                <Text style={styles.symptomCount}>{symptom.count} times</Text>
              </View>
              <View style={styles.symptomBar}>
                <View
                  style={[
                    styles.symptomBarFill,
                    { width: `${symptom.percentage}%` }
                  ]}
                />
              </View>
              <Text style={styles.symptomPercentage}>{symptom.percentage}%</Text>
            </View>
          ))}
        </View>

        {/* Weekly Progress */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Weekly Progress</Text>
          {analyticsData.weeklyProgress.map((week, index) => (
            <View key={index} style={styles.weekItem}>
              <Text style={styles.weekName}>{week.week}</Text>
              <View style={styles.weekStats}>
                <View style={styles.weekStat}>
                  <Text style={styles.weekStatLabel}>Avg Mood</Text>
                  <Text style={styles.weekStatValue}>
                    {getMoodEmoji(Math.round(week.averageMood))} {week.averageMood.toFixed(1)}
                  </Text>
                </View>
                <View style={styles.weekStat}>
                  <Text style={styles.weekStatLabel}>Habits</Text>
                  <Text style={styles.weekStatValue}>{week.habitCompletion}%</Text>
                </View>
              </View>
            </View>
          ))}
        </View>

        {/* AI Insights */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>AI Insights</Text>
          {analyticsData.insights.map((insight, index) => (
            <View key={index} style={styles.insightItem}>
              <Ionicons name="bulb" size={20} color={colors.primary} />
              <Text style={styles.insightText}>{insight}</Text>
            </View>
          ))}
        </View>

        {/* Achievements */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Achievements</Text>
          <View style={styles.achievementsGrid}>
            {analyticsData.achievements.map((achievement, index) => (
              <View
                key={index}
                style={[
                  styles.achievementItem,
                  !achievement.unlocked && styles.achievementItemLocked
                ]}
              >
                <Ionicons
                  name={achievement.unlocked ? "trophy" : "lock-closed"}
                  size={24}
                  color={achievement.unlocked ? colors.primary : colors.textSecondary}
                />
                <Text style={[
                  styles.achievementTitle,
                  !achievement.unlocked && styles.achievementTitleLocked
                ]}>
                  {achievement.title}
                </Text>
                <Text style={[
                  styles.achievementDescription,
                  !achievement.unlocked && styles.achievementDescriptionLocked
                ]}>
                  {achievement.description}
                </Text>
              </View>
            ))}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  header: {
    paddingVertical: 20,
    alignItems: 'center',
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: colors.textPrimary,
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  timeframeSelector: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 4,
    marginBottom: 20,
  },
  timeframeButton: {
    flex: 1,
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  timeframeButtonSelected: {
    backgroundColor: colors.primary,
  },
  timeframeButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textSecondary,
  },
  timeframeButtonTextSelected: {
    color: colors.white,
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 16,
  },
  moodChart: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 100,
    paddingHorizontal: 10,
  },
  moodBar: {
    alignItems: 'center',
    flex: 1,
  },
  moodBarFill: {
    width: 20,
    borderRadius: 10,
    marginBottom: 8,
  },
  moodBarLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  moodBarEmoji: {
    fontSize: 16,
  },
  streakItem: {
    marginBottom: 16,
  },
  streakInfo: {
    marginBottom: 8,
  },
  streakHabit: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 4,
  },
  streakStats: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  streakProgress: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  streakProgressBar: {
    flex: 1,
    height: 6,
    backgroundColor: colors.border,
    borderRadius: 3,
    marginRight: 12,
  },
  streakProgressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 3,
  },
  symptomItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
  },
  symptomInfo: {
    flex: 1,
    marginRight: 12,
  },
  symptomName: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textPrimary,
    marginBottom: 2,
  },
  symptomCount: {
    fontSize: 12,
    color: colors.textSecondary,
  },
  symptomBar: {
    flex: 2,
    height: 8,
    backgroundColor: colors.border,
    borderRadius: 4,
    marginRight: 8,
  },
  symptomBarFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 4,
  },
  symptomPercentage: {
    fontSize: 12,
    fontWeight: '600',
    color: colors.textPrimary,
    minWidth: 30,
    textAlign: 'right',
  },
  weekItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  weekName: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  weekStats: {
    flexDirection: 'row',
    gap: 20,
  },
  weekStat: {
    alignItems: 'center',
  },
  weekStatLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    marginBottom: 4,
  },
  weekStatValue: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  insightItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: colors.background,
    borderRadius: 8,
  },
  insightText: {
    flex: 1,
    fontSize: 14,
    color: colors.textPrimary,
    marginLeft: 8,
    lineHeight: 20,
  },
  achievementsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  achievementItem: {
    width: '48%',
    backgroundColor: colors.background,
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: colors.primary,
  },
  achievementItemLocked: {
    borderColor: colors.border,
    opacity: 0.6,
  },
  achievementTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
    marginTop: 8,
    marginBottom: 4,
    textAlign: 'center',
  },
  achievementTitleLocked: {
    color: colors.textSecondary,
  },
  achievementDescription: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
    lineHeight: 16,
  },
  achievementDescriptionLocked: {
    color: colors.textLight,
  },
});