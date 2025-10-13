import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  TextInput,
  Modal,
} from 'react-native';
import { useFocusEffect } from '@react-navigation/native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';
import { RouteProp } from '@react-navigation/native';
import { SYMPTOM_OPTIONS } from '../types/StoryIntake';

// Mood tracking symptoms - only symptoms women can experience, not diagnoses
const MOOD_SYMPTOM_OPTIONS = [
  "Heavy period", "Painful period", 
  "Weight gain", "Hair loss", "Acne", "Mood swings", 
  "Anxiety", "Depression", "Fatigue", "Sleep issues", "Brain fog", 
  "Joint pain", "Digestive issues", "Food cravings", "Blood sugar issues", 
  "Hot flashes", "Night sweats", "Headache", "Cravings: Sweet", "Backache",
  "Tender breasts", "Dry skin", "Bloating", "Sensitive", "Cramps", "Irritable",
  "Breast tenderness", "Water retention", "Constipation", "Diarrhea",
  "Nausea", "Dizziness", "Low energy", "Memory problems", "Concentration issues",
  "Irritability", "Sadness", "Worry", "Restlessness", "Trouble sleeping",
  "Early waking", "Difficulty falling asleep", "Vivid dreams",
  "Muscle aches", "Stiffness", "Swelling", "Gas",
  "Stomach pain", "Heartburn", "Food sensitivities", "Sugar cravings",
  "Salt cravings", "Chocolate cravings", "Carb cravings", "Appetite changes",
  "Loss of appetite", "Increased appetite", "Temperature sensitivity"
];
import { CyclePhaseService, CyclePhaseInfo } from '../services/cyclePhaseService';
import { getPhaseAwareHabits } from '../services/phaseHabitsApi';
import { DailyProgressAPI, HabitProgress as APIHabitProgress, MoodEntry as APIMoodEntry } from '../services/dailyProgressApi';
import { apiService } from '../services/apiService';
import { useToast } from '../contexts/ToastContext';

// Detailed phase information function
const getDetailedPhaseInfo = (phase: string) => {
  const phaseData = {
    follicular: {
      title: "Follicular Phase",
      duration: "Days 6-13",
      description: "Your body is preparing for ovulation. Estrogen levels are rising, energy is building, and your body is naturally detoxifying.",
      whatHappens: [
        "Estrogen levels gradually increase",
        "Follicles in ovaries begin to mature",
        "Cervical mucus becomes more fertile",
        "Energy and mood typically improve",
        "Body temperature remains lower"
      ],
      nutrition: [
        "Focus on liver-supporting foods (leafy greens, beets, artichokes)",
        "Include iron-rich foods to replenish from menstruation",
        "Add cruciferous vegetables for hormone balance",
        "Increase protein for tissue building",
        "Include healthy fats for hormone production"
      ],
      lifestyle: [
        "Great time to start new habits or projects",
        "Ideal for social activities and networking",
        "Perfect for challenging workouts",
        "Focus on creativity and planning",
        "Good time for important conversations"
      ],
      symptoms: [
        "Increasing energy levels",
        "Improved mood and motivation",
        "Better sleep quality",
        "Clearer skin",
        "Increased libido"
      ],
      tips: [
        "Use this energy boost to tackle challenging tasks",
        "Plan your month ahead while motivation is high",
        "Focus on building new healthy habits",
        "Take advantage of natural confidence boost"
      ]
    },
    ovulatory: {
      title: "Ovulatory Phase",
      duration: "Days 14-16",
      description: "Peak fertility and energy. Estrogen reaches its highest point, triggering ovulation. This is your most energetic and confident phase.",
      whatHappens: [
        "Estrogen peaks, triggering LH surge",
        "Ovulation occurs (egg is released)",
        "Cervical mucus becomes most fertile",
        "Body temperature rises slightly",
        "Testosterone levels also peak"
      ],
      nutrition: [
        "Focus on antioxidant-rich foods (berries, dark chocolate)",
        "Include zinc-rich foods (pumpkin seeds, oysters)",
        "Add omega-3 fatty acids for hormone production",
        "Increase colorful vegetables for phytonutrients",
        "Include magnesium-rich foods for muscle function"
      ],
      lifestyle: [
        "Perfect time for important meetings and presentations",
        "Ideal for challenging physical activities",
        "Great for social events and dating",
        "Best time for creative projects",
        "Excellent for networking and relationship building"
      ],
      symptoms: [
        "Peak energy and stamina",
        "Highest confidence and assertiveness",
        "Best skin and hair condition",
        "Increased social drive",
        "Enhanced cognitive function"
      ],
      tips: [
        "Schedule important tasks and meetings",
        "Take on challenging projects",
        "Use natural confidence for difficult conversations",
        "Plan social activities and date nights"
      ]
    },
    luteal: {
      title: "Luteal Phase",
      duration: "Days 17-28",
      description: "Progesterone rises while estrogen drops. Energy may decline, and you may crave comfort foods. Focus on stress management and self-care.",
      whatHappens: [
        "Progesterone levels rise significantly",
        "Estrogen levels drop after ovulation",
        "Uterine lining thickens for potential pregnancy",
        "Body temperature remains elevated",
        "Cervical mucus becomes thicker and less fertile"
      ],
      nutrition: [
        "Focus on complex carbohydrates for mood stability",
        "Include tryptophan-rich foods (turkey, bananas, oats)",
        "Add magnesium for muscle relaxation and sleep",
        "Include B-vitamins for energy and mood",
        "Consume comfort foods mindfully and nutritiously"
      ],
      lifestyle: [
        "Focus on stress management techniques",
        "Prioritize rest and recovery",
        "Engage in gentle, restorative activities",
        "Plan quiet, introspective time",
        "Prepare for menstruation with self-care"
      ],
      symptoms: [
        "Energy levels may decline",
        "Possible mood changes or irritability",
        "Breast tenderness or swelling",
        "Bloating and water retention",
        "Food cravings, especially for sweets"
      ],
      tips: [
        "Listen to your body's need for rest",
        "Practice stress-reduction techniques",
        "Plan lighter workouts and activities",
        "Prepare nutritious comfort foods",
        "Focus on self-care and relaxation"
      ]
    },
    menstrual: {
      title: "Menstrual Phase",
      duration: "Days 1-5",
      description: "Your period is active. Energy is at its lowest, and your body needs extra care. Focus on rest, iron-rich foods, and gentle movement.",
      whatHappens: [
        "Uterine lining sheds (menstruation)",
        "Estrogen and progesterone levels are lowest",
        "Body temperature drops to baseline",
        "Iron levels may decrease",
        "Inflammation may be higher"
      ],
      nutrition: [
        "Focus on iron-rich foods (red meat, spinach, lentils)",
        "Include anti-inflammatory foods (ginger, turmeric, berries)",
        "Add vitamin C to enhance iron absorption",
        "Include magnesium for muscle relaxation",
        "Stay well-hydrated to support blood volume"
      ],
      lifestyle: [
        "Prioritize rest and recovery",
        "Engage in gentle movement (yoga, walking)",
        "Focus on self-care and relaxation",
        "Avoid over-scheduling or stressful activities",
        "Listen to your body's signals"
      ],
      symptoms: [
        "Lowest energy levels",
        "Possible cramps and discomfort",
        "Mood may be more sensitive",
        "Need for extra rest and sleep",
        "Possible digestive changes"
      ],
      tips: [
        "Honor your need for rest",
        "Use heating pads for cramps",
        "Practice gentle self-massage",
        "Focus on nourishing, warm foods",
        "Be patient and kind with yourself"
      ]
    }
  };

  const currentPhase = phaseData[phase as keyof typeof phaseData];
  if (!currentPhase) return null;

  return (
    <View style={styles.detailedPhaseInfo}>
      <Text style={styles.phaseSectionTitle}>{currentPhase.title}</Text>
      <Text style={styles.phaseDuration}>{currentPhase.duration}</Text>
      
      <View style={styles.phaseSection}>
        <Text style={styles.phaseSectionHeader}>What's Happening</Text>
        {currentPhase.whatHappens.map((item, index) => (
          <Text key={index} style={styles.phaseListItem}>• {item}</Text>
        ))}
      </View>

      <View style={styles.phaseSection}>
        <Text style={styles.phaseSectionHeader}>Nutrition Focus</Text>
        {currentPhase.nutrition.map((item, index) => (
          <Text key={index} style={styles.phaseListItem}>• {item}</Text>
        ))}
      </View>

      <View style={styles.phaseSection}>
        <Text style={styles.phaseSectionHeader}>Lifestyle Recommendations</Text>
        {currentPhase.lifestyle.map((item, index) => (
          <Text key={index} style={styles.phaseListItem}>• {item}</Text>
        ))}
      </View>

      <View style={styles.phaseSection}>
        <Text style={styles.phaseSectionHeader}>Common Symptoms</Text>
        {currentPhase.symptoms.map((item, index) => (
          <Text key={index} style={styles.phaseListItem}>• {item}</Text>
        ))}
      </View>

      <View style={styles.phaseSection}>
        <Text style={styles.phaseSectionHeader}>Pro Tips</Text>
        {currentPhase.tips.map((item, index) => (
          <Text key={index} style={styles.phaseListItem}>• {item}</Text>
        ))}
      </View>
    </View>
  );
};

interface DailyHabitsScreenProps {
  route?: RouteProp<{ params: { selectedHabits: string[]; intakeData?: any } }, 'params'>;
}

interface HabitProgress {
  habit: string;
  completed: boolean;
  notes?: string;
}

interface MoodEntry {
  mood: number;
  symptoms: string[];
  notes: string;
  date: string;
}

interface DailyEntry {
  id: string;
  date: string;
  habits: HabitProgress[];
  mood: MoodEntry | null;
  completedCount: number;
  totalHabits: number;
  progressPercentage: number;
}

export default function DailyHabitsScreen({ route }: DailyHabitsScreenProps) {
  const selectedHabits = route?.params?.selectedHabits || [];
  const [habitProgress, setHabitProgress] = useState<HabitProgress[]>(
    selectedHabits.map(habit => ({ habit, completed: false }))
  );
  const [moodEntry, setMoodEntry] = useState<MoodEntry | null>(null);
  const [showMoodModal, setShowMoodModal] = useState(false);
  const [tempMood, setTempMood] = useState<number>(3);
  const [tempSymptoms, setTempSymptoms] = useState<string[]>([]);
  const [tempNotes, setTempNotes] = useState<string>('');
  const [dailyEntries, setDailyEntries] = useState<DailyEntry[]>([
    // Empty for new user - will populate as they track daily habits
  ]);
  const [showHistory, setShowHistory] = useState(false);

  // Phase tracking state
  const [cyclePhase, setCyclePhase] = useState<CyclePhaseInfo | null>(null);
  const [showPhaseDetails, setShowPhaseDetails] = useState(false);
  const [phaseChangeNotification, setPhaseChangeNotification] = useState<{
    show: boolean;
    newPhase: CyclePhaseInfo | null;
    previousPhase: CyclePhaseInfo | null;
  }>({ show: false, newPhase: null, previousPhase: null });
  const [isUpdatingHabits, setIsUpdatingHabits] = useState(false);
  const [interventionName, setInterventionName] = useState<string>('Control your blood sugar'); // Default intervention
  const [isSavingProgress, setIsSavingProgress] = useState(false);
  const [saveTimeoutId, setSaveTimeoutId] = useState<NodeJS.Timeout | null>(null);
  const [currentStreak, setCurrentStreak] = useState<number>(0);
  const { showToast } = useToast();

  const cyclePhaseService = CyclePhaseService.getInstance();

  // Check for phase changes on component mount and when intake data changes
  useEffect(() => {
    checkForPhaseChange();
  }, [route?.params?.intakeData]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (saveTimeoutId) {
        clearTimeout(saveTimeoutId);
      }
    };
  }, [saveTimeoutId]);

  const loadCurrentStreak = async () => {
    try {
      console.log('🔄 Loading current streak...');
      const streakResponse = await apiService.getHabitStreak('demo-user-123');
      console.log('✅ Streak loaded:', streakResponse.current_streak);
      setCurrentStreak(streakResponse.current_streak);
    } catch (error) {
      console.error('❌ Error loading streak:', error);
      showToast('Failed to load streak data', 'error');
    }
  };

  // Load current streak on component mount
  useEffect(() => {
    loadCurrentStreak();
  }, []);

  // Refresh data when screen comes into focus
  useFocusEffect(
    React.useCallback(() => {
      console.log('🎯 DailyHabitsScreen: Screen focused, refreshing streak...');
      loadCurrentStreak();
    }, [])
  );

  const checkForPhaseChange = async () => {
    const intakeData = route?.params?.intakeData;
    if (!intakeData?.lastPeriod?.date || !intakeData?.lastPeriod?.cycleLength) {
      return;
    }

    try {
      const { hasChanged, newPhase, previousPhase } = await cyclePhaseService.checkPhaseChange(
        intakeData.lastPeriod.date,
        intakeData.lastPeriod.cycleLength
      );

      if (hasChanged && newPhase && previousPhase) {
        setCyclePhase(newPhase);
        setPhaseChangeNotification({
          show: true,
          newPhase,
          previousPhase
        });
      } else if (newPhase) {
        setCyclePhase(newPhase);
      }
    } catch (error) {
      console.error('Error checking phase change:', error);
    }
  };

  const updateHabitsForNewPhase = async () => {
    if (!cyclePhase || !route?.params?.intakeData) return;

    setIsUpdatingHabits(true);
    try {
      // Get new phase-aware habits from backend
      const result = await getPhaseAwareHabits(
        'user123', // This should be the actual user ID
        cyclePhase.phase,
        interventionName
      );
      
      if (result.success && result.data?.habits) {
        const newHabits = result.data.habits.map((habit: string) => ({ habit, completed: false }));
        setHabitProgress(newHabits);
      }
    } catch (error) {
      console.error('Error updating habits:', error);
    } finally {
      setIsUpdatingHabits(false);
    }
  };

  const handlePhaseChangeAccept = () => {
    updateHabitsForNewPhase();
    setPhaseChangeNotification({ show: false, newPhase: null, previousPhase: null });
  };

  const handlePhaseChangeDismiss = () => {
    setPhaseChangeNotification({ show: false, newPhase: null, previousPhase: null });
  };

  const saveProgressToAPI = async () => {
    if (isSavingProgress) return;
    
    setIsSavingProgress(true);
    try {
      const today = new Date().toISOString().split('T')[0];
      const apiHabits: APIHabitProgress[] = habitProgress.map(h => ({
        habit: h.habit,
        completed: h.completed,
        notes: h.notes || ''
      }));

      const apiMood: APIMoodEntry | undefined = moodEntry ? {
        mood: moodEntry.mood,
        symptoms: moodEntry.symptoms,
        notes: moodEntry.notes,
        date: moodEntry.date
      } : undefined;

      await apiService.saveDailyProgress({
        user_id: 'demo-user-123',
        entry_date: today,
        habits: apiHabits,
        mood: apiMood,
        cycle_phase: cyclePhase?.phase || 'follicular'
      });

      // Update streak after saving
      const streakResponse = await apiService.getHabitStreak('demo-user-123');
      setCurrentStreak(streakResponse.current_streak);
      showToast('Progress saved successfully!', 'success');

    } catch (error) {
      console.error('Error saving progress to API:', error);
      showToast(error instanceof Error ? error.message : 'Failed to save progress. Please try again.', 'error');
    } finally {
      setIsSavingProgress(false);
    }
  };

  const toggleHabit = (habit: string) => {
    console.log('🔄 Toggling habit:', habit);
    setHabitProgress(prev => {
      const updated = prev.map(h => 
        h.habit === habit 
          ? { ...h, completed: !h.completed }
          : h
      );
      console.log('📊 Updated habit progress:', updated);
      return updated;
    });
    
    // Clear existing timeout and set a new one to debounce saves
    if (saveTimeoutId) {
      clearTimeout(saveTimeoutId);
    }
    
    const newTimeoutId = setTimeout(() => {
      saveProgressToAPI();
    }, 1000); // Increased delay to 1 second for better debouncing
    
    setSaveTimeoutId(newTimeoutId);
  };

  const openMoodModal = () => {
    if (moodEntry) {
      setTempMood(moodEntry.mood);
      setTempSymptoms([...moodEntry.symptoms]);
      setTempNotes(moodEntry.notes);
    } else {
      setTempMood(3);
      setTempSymptoms([]);
      setTempNotes('');
    }
    setShowMoodModal(true);
  };

  const saveMoodEntry = () => {
    const newMoodEntry: MoodEntry = {
      mood: tempMood,
      symptoms: tempSymptoms,
      notes: tempNotes,
      date: new Date().toISOString().split('T')[0],
    };
    setMoodEntry(newMoodEntry);
    setShowMoodModal(false);
    
    // Save progress to API after mood entry
    setTimeout(() => {
      saveProgressToAPI();
    }, 500);
  };

  const saveDailyEntry = () => {
    const today = new Date().toISOString().split('T')[0];
    const completedCount = habitProgress.filter(h => h.completed).length;
    const totalHabits = habitProgress.length;
    const progressPercentage = totalHabits > 0 ? (completedCount / totalHabits) * 100 : 0;

    const newEntry: DailyEntry = {
      id: Date.now().toString(),
      date: today,
      habits: [...habitProgress],
      mood: moodEntry,
      completedCount,
      totalHabits,
      progressPercentage,
    };

    setDailyEntries(prev => [newEntry, ...prev]);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (dateString === today.toISOString().split('T')[0]) {
      return 'Today';
    } else if (dateString === yesterday.toISOString().split('T')[0]) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString('en-US', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  const toggleSymptom = (symptom: string) => {
    setTempSymptoms(prev => 
      prev.includes(symptom) 
        ? prev.filter(s => s !== symptom)
        : [...prev, symptom]
    );
  };

  const completedCount = habitProgress.filter(h => h.completed).length;
  const totalHabits = habitProgress.length;
  const progressPercentage = totalHabits > 0 ? (completedCount / totalHabits) * 100 : 0;
  
  console.log('📊 Progress calculation:', {
    completedCount,
    totalHabits,
    progressPercentage: Math.round(progressPercentage),
    habitProgress
  });

  const getMoodEmoji = (moodValue: number) => {
    const moods = ['😢', '😔', '😐', '😊', '😄'];
    return moods[moodValue - 1] || '😐';
  };

  const getMoodLabel = (moodValue: number) => {
    const labels = ['Very Bad', 'Bad', 'Okay', 'Good', 'Great'];
    return labels[moodValue - 1] || 'Okay';
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* Phase Change Notification */}
        {phaseChangeNotification.show && (
          <PhaseChangeNotification
            newPhase={phaseChangeNotification.newPhase}
            previousPhase={phaseChangeNotification.previousPhase}
            onAccept={handlePhaseChangeAccept}
            onDismiss={handlePhaseChangeDismiss}
            isUpdating={isUpdatingHabits}
          />
        )}

        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>Daily Habits</Text>
          <Text style={styles.subtitle}>
            Track your progress and mood today
          </Text>
        </View>

        {/* Enhanced Current Phase Info */}
        {cyclePhase && (
          <View style={styles.phaseInfoCard}>
            <Text style={styles.phaseTitle}>Current Cycle Phase</Text>
            <Text style={styles.phaseName}>{cyclePhase.phase}</Text>
            <Text style={styles.phaseDescription}>{cyclePhase.phaseDescription}</Text>
            <Text style={styles.phaseDetails}>
              Energy: {cyclePhase.energyLevel} | Focus: {cyclePhase.hormonalFocus}
            </Text>
            
            {/* Learn More Dropdown */}
            <TouchableOpacity 
              style={styles.learnMoreButton}
              onPress={() => setShowPhaseDetails(!showPhaseDetails)}
            >
              <Text style={styles.learnMoreText}>Learn more about my current phase</Text>
              <Ionicons 
                name={showPhaseDetails ? "chevron-up" : "chevron-down"} 
                size={20} 
                color={colors.primary} 
              />
            </TouchableOpacity>
            
            {/* Detailed Phase Information - Collapsible */}
            {showPhaseDetails && (
              <View style={styles.phaseDetailsSection}>
                {getDetailedPhaseInfo(cyclePhase.phase)}
              </View>
            )}
          </View>
        )}

        {/* Progress Overview */}
        <View style={styles.progressCard}>
          <View style={styles.progressHeader}>
            <Text style={styles.progressTitle}>Today's Progress</Text>
            <View style={styles.progressHeaderRight}>
              <Text 
                key={`count-${completedCount}-${totalHabits}`}
                style={styles.progressCount}
              >
                {completedCount}/{totalHabits} completed
              </Text>
              {isSavingProgress && (
                <Ionicons name="sync" size={16} color={colors.primary} style={styles.savingIcon} />
              )}
            </View>
          </View>
          <View style={styles.progressBar}>
            <View 
              key={`progress-${completedCount}-${totalHabits}`}
              style={[
                styles.progressFill, 
                { width: `${progressPercentage}%` }
              ]} 
            />
          </View>
          <Text 
            key={`percentage-${completedCount}-${totalHabits}`}
            style={styles.progressPercentage}
          >
            {Math.round(progressPercentage)}% complete
            {isSavingProgress && ' (Saving...)'}
          </Text>
        </View>

        {/* Habits List */}
        <View style={styles.habitsCard}>
          <Text style={styles.habitsTitle}>
            {cyclePhase ? `Your Habits for ${cyclePhase.phase} Phase` : 'Your Habits'}
          </Text>
          {cyclePhase && (
            <Text style={styles.phaseContext}>
              These habits are optimized for your current cycle phase
            </Text>
          )}
          {habitProgress.map((habit, index) => (
            <TouchableOpacity
              key={index}
              style={[
                styles.habitItem,
                habit.completed && styles.habitItemCompleted
              ]}
              onPress={() => toggleHabit(habit.habit)}
            >
              <View style={styles.habitContent}>
                <View style={[
                  styles.habitCheckbox,
                  habit.completed && styles.habitCheckboxCompleted
                ]}>
                  {habit.completed && (
                    <Ionicons name="checkmark" size={16} color="#FFFFFF" />
                  )}
                </View>
                <Text style={[
                  styles.habitText,
                  habit.completed && styles.habitTextCompleted
                ]}>
                  {habit.habit}
                </Text>
              </View>
            </TouchableOpacity>
          ))}
        </View>

        {/* Mood Tracker */}
        <View style={styles.moodCard}>
          <Text style={styles.moodTitle}>How are you feeling today?</Text>
          {moodEntry ? (
            <View style={styles.moodSelected}>
              <Text style={styles.moodEmoji}>{getMoodEmoji(moodEntry.mood)}</Text>
              <Text style={styles.moodLabel}>{getMoodLabel(moodEntry.mood)}</Text>
              {moodEntry.symptoms.length > 0 && (
                <View style={styles.symptomsPreview}>
                  <Text style={styles.symptomsPreviewText}>
                    {moodEntry.symptoms.slice(0, 2).join(', ')}
                    {moodEntry.symptoms.length > 2 && ` +${moodEntry.symptoms.length - 2} more`}
                  </Text>
                </View>
              )}
              <TouchableOpacity 
                style={styles.changeMoodButton}
                onPress={openMoodModal}
              >
                <Text style={styles.changeMoodText}>Update</Text>
              </TouchableOpacity>
            </View>
          ) : (
            <TouchableOpacity 
              style={styles.moodButton}
              onPress={openMoodModal}
            >
              <Ionicons name="happy-outline" size={24} color={colors.primary} />
              <Text style={styles.moodButtonText}>Track your mood</Text>
            </TouchableOpacity>
          )}
        </View>

        {/* Mood Tracking Modal */}
        <Modal
          visible={showMoodModal}
          animationType="slide"
          transparent={true}
          onRequestClose={() => setShowMoodModal(false)}
        >
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>How are you feeling today?</Text>
                <TouchableOpacity 
                  style={styles.closeButton}
                  onPress={() => setShowMoodModal(false)}
                >
                  <Ionicons name="close" size={24} color={colors.textSecondary} />
                </TouchableOpacity>
              </View>

              <ScrollView style={styles.modalBody} showsVerticalScrollIndicator={false}>
                {/* Mood Selection */}
                <View style={styles.moodSection}>
                  <Text style={styles.sectionTitle}>Mood</Text>
                  <View style={styles.moodOptions}>
                    {[1, 2, 3, 4, 5].map((moodValue) => (
                      <TouchableOpacity
                        key={moodValue}
                        style={[
                          styles.moodOption,
                          tempMood === moodValue && styles.moodOptionSelected
                        ]}
                        onPress={() => setTempMood(moodValue)}
                      >
                        <Text style={styles.moodOptionEmoji}>
                          {getMoodEmoji(moodValue)}
                        </Text>
                        <Text style={[
                          styles.moodOptionLabel,
                          tempMood === moodValue && styles.moodOptionLabelSelected
                        ]}>
                          {getMoodLabel(moodValue)}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>

                {/* Symptoms Selection */}
                <View style={styles.symptomsSection}>
                  <Text style={styles.sectionTitle}>Symptoms (optional)</Text>
                  <View style={styles.symptomsGrid}>
                    {MOOD_SYMPTOM_OPTIONS.slice(0, 20).map((symptom) => (
                      <TouchableOpacity
                        key={symptom}
                        style={[
                          styles.symptomChip,
                          tempSymptoms.includes(symptom) && styles.symptomChipSelected
                        ]}
                        onPress={() => toggleSymptom(symptom)}
                      >
                        <Text style={[
                          styles.symptomChipText,
                          tempSymptoms.includes(symptom) && styles.symptomChipTextSelected
                        ]}>
                          {symptom}
                        </Text>
                      </TouchableOpacity>
                    ))}
                  </View>
                </View>

                {/* Notes */}
                <View style={styles.notesSection}>
                  <Text style={styles.sectionTitle}>Notes (optional)</Text>
                  <TextInput
                    style={styles.notesInput}
                    value={tempNotes}
                    onChangeText={setTempNotes}
                    placeholder="How are you feeling? Any observations about your day?"
                    multiline
                    numberOfLines={4}
                    textAlignVertical="top"
                    placeholderTextColor={colors.textSecondary}
                  />
                </View>
              </ScrollView>

              <View style={styles.modalFooter}>
                <TouchableOpacity 
                  style={styles.cancelButton}
                  onPress={() => setShowMoodModal(false)}
                >
                  <Text style={styles.cancelButtonText}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={styles.saveButton}
                  onPress={saveMoodEntry}
                >
                  <Text style={styles.saveButtonText}>Save</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        </Modal>

        {/* Save Button */}
        <TouchableOpacity style={styles.saveButton} onPress={saveDailyEntry}>
          <Text style={styles.saveButtonText}>Save Today's Progress</Text>
        </TouchableOpacity>

        {/* History Toggle */}
        <TouchableOpacity 
          style={styles.historyToggle}
          onPress={() => setShowHistory(!showHistory)}
        >
          <Text style={styles.historyToggleText}>
            {showHistory ? 'Hide' : 'Show'} Previous Entries
          </Text>
          <Ionicons 
            name={showHistory ? "chevron-up" : "chevron-down"} 
            size={20} 
            color={colors.primary} 
          />
        </TouchableOpacity>

        {/* History Section */}
        {showHistory && (
          <View style={styles.historyCard}>
            <Text style={styles.historyTitle}>Previous Entries</Text>
            {dailyEntries.map((entry) => (
              <View key={entry.id} style={styles.historyEntry}>
                <View style={styles.historyHeader}>
                  <Text style={styles.historyDate}>{formatDate(entry.date)}</Text>
                  <Text style={styles.historyProgress}>
                    {entry.completedCount}/{entry.totalHabits} habits
                  </Text>
                </View>
                
                <View style={styles.historyProgressBar}>
                  <View 
                    style={[
                      styles.historyProgressFill, 
                      { width: `${entry.progressPercentage}%` }
                    ]} 
                  />
                </View>

                {/* Mood Summary */}
                {entry.mood && (
                  <View style={styles.historyMood}>
                    <Text style={styles.historyMoodEmoji}>
                      {getMoodEmoji(entry.mood.mood)}
                    </Text>
                    <Text style={styles.historyMoodLabel}>
                      {getMoodLabel(entry.mood.mood)}
                    </Text>
                    {entry.mood.symptoms.length > 0 && (
                      <Text style={styles.historySymptoms}>
                        {entry.mood.symptoms.slice(0, 3).join(', ')}
                        {entry.mood.symptoms.length > 3 && ` +${entry.mood.symptoms.length - 3}`}
                      </Text>
                    )}
                  </View>
                )}

                {/* Habits Summary */}
                <View style={styles.historyHabits}>
                  {entry.habits.map((habit, index) => (
                    <View key={index} style={styles.historyHabitItem}>
                      <Ionicons 
                        name={habit.completed ? "checkmark-circle" : "close-circle"} 
                        size={16} 
                        color={habit.completed ? colors.success : colors.error} 
                      />
                      <Text style={[
                        styles.historyHabitText,
                        !habit.completed && styles.historyHabitTextIncomplete
                      ]}>
                        {habit.habit}
                      </Text>
                    </View>
                  ))}
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F8FAFC',
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
    color: '#1F2937',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
  progressCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  progressHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  progressHeaderRight: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  savingIcon: {
    marginLeft: 8,
  },
  progressTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
  },
  progressCount: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
  },
  progressBar: {
    height: 8,
    backgroundColor: '#E5E7EB',
    borderRadius: 4,
    marginBottom: 8,
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 4,
  },
  progressPercentage: {
    fontSize: 14,
    color: '#6B7280',
    textAlign: 'center',
  },
  moodCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  moodTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16,
  },
  moodButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 20,
    backgroundColor: '#FFF7F5',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: colors.primary,
    borderStyle: 'dashed',
  },
  moodButtonText: {
    fontSize: 16,
    color: colors.primary,
    marginLeft: 8,
    fontWeight: '500',
  },
  moodSelected: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 12,
    paddingHorizontal: 16,
    backgroundColor: '#FFF7F5',
    borderRadius: 12,
  },
  moodEmoji: {
    fontSize: 24,
  },
  moodLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
    flex: 1,
    marginLeft: 12,
  },
  changeMoodButton: {
    paddingVertical: 6,
    paddingHorizontal: 12,
    backgroundColor: colors.primary,
    borderRadius: 6,
  },
  changeMoodText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '500',
  },
  symptomsPreview: {
    marginTop: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: colors.primaryLight,
    borderRadius: 12,
    alignSelf: 'flex-start',
  },
  symptomsPreviewText: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '500',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '80%',
    minHeight: '60%',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  closeButton: {
    padding: 4,
  },
  modalBody: {
    paddingHorizontal: 20,
    paddingVertical: 10,
    maxHeight: 400,
  },
  moodSection: {
    marginTop: 20,
    marginBottom: 24,
  },
  symptomsSection: {
    marginBottom: 24,
  },
  notesSection: {
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 12,
  },
  moodOptions: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  moodOption: {
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 8,
    borderRadius: 12,
    minWidth: 60,
  },
  moodOptionSelected: {
    backgroundColor: colors.primaryLight,
  },
  moodOptionEmoji: {
    fontSize: 32,
    marginBottom: 8,
  },
  moodOptionLabel: {
    fontSize: 12,
    color: colors.textSecondary,
    textAlign: 'center',
  },
  moodOptionLabelSelected: {
    color: colors.primary,
    fontWeight: '500',
  },
  symptomsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginHorizontal: -4,
  },
  symptomChip: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#F3F4F6',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    margin: 4,
  },
  symptomChipSelected: {
    backgroundColor: colors.primaryLight,
    borderColor: colors.primary,
  },
  symptomChipText: {
    fontSize: 14,
    color: colors.textSecondary,
    fontWeight: '500',
  },
  symptomChipTextSelected: {
    color: colors.primary,
  },
  notesInput: {
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    fontSize: 16,
    color: colors.textPrimary,
    backgroundColor: '#F9FAFB',
  },
  modalFooter: {
    flexDirection: 'row',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    gap: 12,
  },
  cancelButton: {
    flex: 1,
    paddingVertical: 14,
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    alignItems: 'center',
  },
  cancelButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textSecondary,
  },
  saveButton: {
    flex: 1,
    paddingVertical: 14,
    backgroundColor: colors.primary,
    borderRadius: 12,
    alignItems: 'center',
  },
  saveButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  habitsCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  habitsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 16,
  },
  habitItem: {
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  habitItemCompleted: {
    opacity: 0.7,
  },
  habitContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  habitCheckbox: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: '#D1D5DB',
    marginRight: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  habitCheckboxCompleted: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  habitText: {
    fontSize: 16,
    color: '#1F2937',
    flex: 1,
  },
  habitTextCompleted: {
    textDecorationLine: 'line-through',
    color: '#9CA3AF',
  },
  historyToggle: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: colors.primary,
  },
  historyToggleText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.primary,
  },
  historyCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  historyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 16,
  },
  historyEntry: {
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
    paddingBottom: 16,
    marginBottom: 16,
  },
  historyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  historyDate: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
  },
  historyProgress: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  historyProgressBar: {
    height: 6,
    backgroundColor: '#F3F4F6',
    borderRadius: 3,
    marginBottom: 12,
  },
  historyProgressFill: {
    height: '100%',
    backgroundColor: colors.primary,
    borderRadius: 3,
  },
  historyMood: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
  },
  historyMoodEmoji: {
    fontSize: 20,
    marginRight: 8,
  },
  historyMoodLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textPrimary,
    marginRight: 8,
  },
  historySymptoms: {
    fontSize: 12,
    color: colors.textSecondary,
    flex: 1,
  },
  historyHabits: {
    gap: 6,
  },
  historyHabitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 4,
  },
  historyHabitText: {
    fontSize: 14,
    color: colors.textPrimary,
    marginLeft: 8,
  },
  historyHabitTextIncomplete: {
    color: colors.textSecondary,
    textDecorationLine: 'line-through',
  },
  // Phase tracking styles
  phaseInfoCard: {
    backgroundColor: '#f0f9ff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: colors.primary,
  },
  phaseTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 4,
  },
  phaseName: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: 4,
  },
  phaseDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: 8,
  },
  phaseDetails: {
    fontSize: 12,
    color: colors.textSecondary,
    fontStyle: 'italic',
  },
  learnMoreButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginTop: 12,
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#F8FAFC',
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  learnMoreText: {
    fontSize: 14,
    color: colors.primary,
    fontWeight: '500',
  },
  phaseContext: {
    fontSize: 14,
    color: colors.textSecondary,
    fontStyle: 'italic',
    marginBottom: 16,
  },
  // Phase change notification styles
  notificationOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 1000,
  },
  notificationCard: {
    backgroundColor: colors.white,
    borderRadius: 16,
    padding: 24,
    margin: 20,
    maxWidth: 350,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 8,
  },
  notificationTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: 12,
    textAlign: 'center',
  },
  notificationText: {
    fontSize: 16,
    color: colors.textPrimary,
    lineHeight: 22,
    marginBottom: 12,
    textAlign: 'center',
  },
  phaseChangeText: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.primary,
    textAlign: 'center',
    marginBottom: 8,
  },
  notificationButtons: {
    flexDirection: 'row',
    gap: 12,
  },
  dismissButton: {
    flex: 1,
    backgroundColor: colors.gray200,
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  dismissButtonText: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.textPrimary,
  },
  acceptButton: {
    flex: 1,
    backgroundColor: colors.primary,
    borderRadius: 8,
    paddingVertical: 12,
    alignItems: 'center',
  },
  acceptButtonText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.white,
  },
  // New styles for detailed phase information
  phaseDetailsSection: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
  },
  detailedPhaseInfo: {
    marginTop: 12,
  },
  phaseSectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: colors.primary,
    marginBottom: 4,
  },
  phaseDuration: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: 16,
    fontStyle: 'italic',
  },
  phaseSection: {
    marginBottom: 16,
  },
  phaseSectionHeader: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: 8,
  },
  phaseListItem: {
    fontSize: 14,
    color: colors.textSecondary,
    lineHeight: 20,
    marginBottom: 4,
    paddingLeft: 8,
  },
});

// Phase Change Notification Component
const PhaseChangeNotification = ({ 
  newPhase, 
  previousPhase, 
  onAccept, 
  onDismiss, 
  isUpdating 
}: {
  newPhase: CyclePhaseInfo | null;
  previousPhase: CyclePhaseInfo | null;
  onAccept: () => void;
  onDismiss: () => void;
  isUpdating: boolean;
}) => (
  <View style={styles.notificationOverlay}>
    <View style={styles.notificationCard}>
      <Text style={styles.notificationTitle}>Cycle Phase Update! 🎉</Text>
      <Text style={styles.notificationText}>
        You've entered your {newPhase?.phase} phase! 
        Your habits have been updated to optimize your health during this phase.
      </Text>
      <Text style={styles.phaseChangeText}>
        {previousPhase?.phase} → {newPhase?.phase}
      </Text>
      <Text style={styles.phaseDescription}>{newPhase?.phaseDescription}</Text>
      
      <View style={styles.notificationButtons}>
        <TouchableOpacity 
          style={styles.dismissButton} 
          onPress={onDismiss}
        >
          <Text style={styles.dismissButtonText}>Keep Current Habits</Text>
        </TouchableOpacity>
        <TouchableOpacity 
          style={styles.acceptButton} 
          onPress={onAccept}
          disabled={isUpdating}
        >
          <Text style={styles.acceptButtonText}>
            {isUpdating ? 'Updating...' : 'Update Habits'}
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  </View>
);
