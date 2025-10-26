import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  SafeAreaView,
  Alert,
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../constants/colors';
import { useAuth } from '../contexts/AuthContext';
import { interventionPeriodService } from '../services/interventionPeriodService';
import { RouteProp } from '@react-navigation/native';

interface ProfileScreenProps {
  route?: RouteProp<{ params: { intakeData?: any } }, 'params'>;
}

export default function ProfileScreen({ route }: ProfileScreenProps) {
  const { user, logout, session, refreshUser } = useAuth();
  const intakeData = route?.params?.intakeData;
  const [interventionPeriods, setInterventionPeriods] = useState<any[]>([]);
  const [loadingInterventions, setLoadingInterventions] = useState(true);

  useEffect(() => {
    loadInterventionPeriods();
  }, [user, session]);
  
  // Refresh session if available
  useEffect(() => {
    if (user && session) {
      refreshUser().catch(err => console.error('Failed to refresh user:', err));
    }
  }, []);

  const loadInterventionPeriods = async () => {
    if (!user?.id || !session?.access_token) {
      console.error('No user or session found');
      setLoadingInterventions(false);
      return;
    }

    try {
      setLoadingInterventions(true);
      console.log('Loading intervention periods with access token:', session.access_token.substring(0, 20) + '...');
      
      const result = await interventionPeriodService.getUserInterventionPeriods(session.access_token);
      
      if (result.success) {
        console.log('✅ Successfully loaded intervention periods:', result.periods?.length || 0);
        setInterventionPeriods(result.periods || []);
      } else {
        console.error('❌ Failed to load intervention periods:', result.error);
        setInterventionPeriods([]);
      }
    } catch (error: any) {
      console.error('❌ Error loading intervention periods:', error);
      console.error('Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status
      });
      setInterventionPeriods([]);
    } finally {
      setLoadingInterventions(false);
    }
  };

  const handleLogout = () => {
    logout().then(() => {
      console.log('✅ Logout completed successfully');
    }).catch((error) => {
      console.error('❌ Logout error:', error);
    });
  };
  const profileData = intakeData || {
    profile: { name: 'User', dateOfBirth: '1990-01-01' },
    symptoms: { selected: ['PCOS'], additional: '' },
    interventions: { selected: [], additional: '' },
    dietaryPreferences: { selected: ['Vegetarian'], additional: '' },
    lastPeriod: { date: '2024-12-01', hasPeriod: true, cycleLength: 28 },
  };

  const getCyclePhase = () => {
    if (!profileData.lastPeriod?.date || !profileData.lastPeriod?.cycleLength) {
      return 'Not available';
    }
    
    const lastPeriod = new Date(profileData.lastPeriod.date);
    const today = new Date();
    const daysSince = Math.floor((today.getTime() - lastPeriod.getTime()) / (1000 * 60 * 60 * 24));
    const cycleLength = profileData.lastPeriod.cycleLength;
    
    if (daysSince <= 5) return 'Menstrual Phase';
    if (daysSince <= 13) return 'Follicular Phase';
    if (daysSince <= 16) return 'Ovulation Phase';
    if (daysSince <= cycleLength - 5) return 'Luteal Phase';
    return 'Pre-Menstrual Phase';
  };

  const getCyclePhaseColor = (phase: string) => {
    const colors: { [key: string]: string } = {
      'Menstrual Phase': '#EF4444',
      'Follicular Phase': '#10B981',
      'Ovulation Phase': '#3B82F6',
      'Luteal Phase': '#F59E0B',
      'Pre-Menstrual Phase': '#8B5CF6',
    };
    return colors[phase] || '#6B7280';
  };

  const cyclePhase = getCyclePhase();

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView 
        style={styles.content} 
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.scrollContent}
        keyboardShouldPersistTaps="handled"
        scrollEventThrottle={16}
      >
        {/* Header */}
        <View style={styles.header}>
          <View style={styles.avatarContainer}>
            <Ionicons name="person" size={40} color={colors.primary} />
          </View>
          <Text style={styles.name}>
            {user?.name || 'User'}
          </Text>
          <Text style={styles.subtitle}>Health Journey Profile</Text>
        </View>

        {/* Cycle Phase Card */}
        {profileData.lastPeriod?.hasPeriod && (
          <View style={styles.card}>
            <View style={styles.cardHeader}>
              <Ionicons name="calendar" size={20} color={colors.primary} />
              <Text style={styles.cardTitle}>Current Cycle Phase</Text>
            </View>
            <View style={styles.cyclePhaseContainer}>
              <View style={[
                styles.cyclePhaseIndicator,
                { backgroundColor: getCyclePhaseColor(cyclePhase) }
              ]} />
              <Text style={styles.cyclePhaseText}>{cyclePhase}</Text>
            </View>
            {profileData.lastPeriod?.cycleLength && (
              <Text style={styles.cycleLengthText}>
                {profileData.lastPeriod.cycleLength}-day cycle
              </Text>
            )}
          </View>
        )}

        {/* Symptoms Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="medical" size={20} color={colors.primary} />
            <Text style={styles.cardTitle}>Symptoms & Conditions</Text>
          </View>
          {profileData.symptoms?.selected?.length > 0 ? (
            <View style={styles.tagsContainer}>
              {profileData.symptoms.selected.map((symptom: string, index: number) => (
                <View key={index} style={styles.tag}>
                  <Text style={styles.tagText}>{symptom}</Text>
                </View>
              ))}
            </View>
          ) : (
            <Text style={styles.emptyText}>No symptoms recorded</Text>
          )}
          {profileData.symptoms?.additional && (
            <Text style={styles.additionalText}>
              Additional: {profileData.symptoms.additional}
            </Text>
          )}
        </View>

        {/* Interventions Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="flask" size={20} color={colors.primary} />
            <Text style={styles.cardTitle}>Tried Interventions</Text>
          </View>
          {loadingInterventions ? (
            <Text style={styles.emptyText}>Loading interventions...</Text>
          ) : interventionPeriods.length > 0 ? (
            <View style={styles.interventionsList}>
              {interventionPeriods.map((period: any, index: number) => (
                <View key={period.id || index} style={styles.interventionItem}>
                  <Text style={styles.interventionName}>
                    {period.intervention_name}
                  </Text>
                  <View style={styles.interventionDetails}>
                    <Text style={styles.interventionStatus}>
                      Status: {period.status}
                    </Text>
                    <Text style={styles.interventionProgress}>
                      Progress: {period.completion_percentage}%
                    </Text>
                    <Text style={styles.interventionDate}>
                      Started: {new Date(period.start_date).toLocaleDateString()}
                    </Text>
                  </View>
                </View>
              ))}
            </View>
          ) : (
            <Text style={styles.emptyText}>No interventions tried yet</Text>
          )}
        </View>

        {/* Dietary Preferences Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="restaurant" size={20} color={colors.primary} />
            <Text style={styles.cardTitle}>Dietary Preferences</Text>
          </View>
          {profileData.dietaryPreferences?.selected?.length > 0 ? (
            <View style={styles.tagsContainer}>
              {profileData.dietaryPreferences.selected.map((preference: string, index: number) => (
                <View key={index} style={[styles.tag, styles.dietaryTag]}>
                  <Text style={[styles.tagText, styles.dietaryTagText]}>{preference}</Text>
                </View>
              ))}
            </View>
          ) : (
            <Text style={styles.emptyText}>No dietary preferences set</Text>
          )}
          {profileData.dietaryPreferences?.additional && (
            <Text style={styles.additionalText}>
              Additional: {profileData.dietaryPreferences.additional}
            </Text>
          )}
        </View>

        {/* Settings Card */}
        <View style={styles.card}>
          <View style={styles.cardHeader}>
            <Ionicons name="settings" size={20} color={colors.primary} />
            <Text style={styles.cardTitle}>Settings</Text>
          </View>
          <TouchableOpacity style={styles.settingItem}>
            <Ionicons name="notifications" size={20} color="#6B7280" />
            <Text style={styles.settingText}>Notifications</Text>
            <Ionicons name="chevron-forward" size={20} color="#D1D5DB" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Ionicons name="shield-checkmark" size={20} color="#6B7280" />
            <Text style={styles.settingText}>Privacy & Security</Text>
            <Ionicons name="chevron-forward" size={20} color="#D1D5DB" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Ionicons name="help-circle" size={20} color="#6B7280" />
            <Text style={styles.settingText}>Help & Support</Text>
            <Ionicons name="chevron-forward" size={20} color="#D1D5DB" />
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Ionicons name="information-circle" size={20} color="#6B7280" />
            <Text style={styles.settingText}>About</Text>
            <Ionicons name="chevron-forward" size={20} color="#D1D5DB" />
          </TouchableOpacity>
        </View>

        {/* Sign Out Button */}
        <TouchableOpacity 
          style={styles.logoutButton} 
          onPress={handleLogout}
          activeOpacity={0.7}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        >
          <Ionicons name="log-out" size={20} color="#EF4444" />
          <Text style={styles.logoutText}>Sign Out</Text>
        </TouchableOpacity>
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
  },
  scrollContent: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 30,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFF7F5',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 16,
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 4,
  },
  subtitle: {
    fontSize: 16,
    color: '#6B7280',
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1F2937',
    marginLeft: 8,
  },
  cyclePhaseContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  cyclePhaseIndicator: {
    width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: 8,
  },
  cyclePhaseText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#1F2937',
  },
  cycleLengthText: {
    fontSize: 14,
    color: '#6B7280',
  },
  tagsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  tag: {
    backgroundColor: '#F3F4F6',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
  },
  tagText: {
    fontSize: 14,
    color: '#374151',
  },
  dietaryTag: {
    backgroundColor: '#E0F2FE',
  },
  dietaryTagText: {
    color: '#0369A1',
  },
  emptyText: {
    fontSize: 14,
    color: '#9CA3AF',
    fontStyle: 'italic',
  },
  additionalText: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 8,
    fontStyle: 'italic',
  },
  interventionsList: {
    gap: 12,
  },
  interventionItem: {
    paddingVertical: 8,
    paddingHorizontal: 12,
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    marginBottom: 8,
  },
  interventionName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  interventionDetails: {
    marginTop: 4,
  },
  interventionStatus: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 2,
  },
  interventionProgress: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 2,
  },
  interventionDate: {
    fontSize: 14,
    color: '#6B7280',
  },
  helpfulnessTag: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  helpfulTag: {
    backgroundColor: '#D1FAE5',
  },
  notHelpfulTag: {
    backgroundColor: '#FEE2E2',
  },
  helpfulnessText: {
    fontSize: 12,
    fontWeight: '500',
  },
  helpfulText: {
    color: '#065F46',
  },
  notHelpfulText: {
    color: '#991B1B',
  },
  settingItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  settingText: {
    fontSize: 16,
    color: '#374151',
    marginLeft: 12,
    flex: 1,
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingVertical: 16,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: '#FEE2E2',
  },
  logoutText: {
    fontSize: 16,
    color: '#EF4444',
    marginLeft: 8,
    fontWeight: '500',
  },
});
