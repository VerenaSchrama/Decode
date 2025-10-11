import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  SafeAreaView,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import RenderHtml from 'react-native-render-html';
import { getRecommendations } from '../services/api';
import { StoryIntakeData } from '../types/StoryIntake';
import InterventionPeriodScreen from './InterventionPeriodScreen';

interface RecommendationsScreenProps {
  intakeData: StoryIntakeData;
  onBack: () => void;
  onHabitsSelected?: (selectedHabits: string[]) => void;
  onInterventionSelected?: (intervention: Intervention, periodData: {
    durationDays: number;
    startDate: string;
    endDate: string;
  }) => void;
}

interface Intervention {
  id: number;
  name: string;
  profile_match: string;
  similarity_score: number;
  scientific_source: string;
  habits: Array<{
    number: number;
    description: string;
  }>;
}

interface RecommendationData {
  intake_summary: string;
  interventions: Intervention[];
  total_found: number;
  min_similarity_used: number;
  additional_inflo_context?: string;
  data_collection?: {
    user_id: string;
    intake_id: string;
    message: string;
  };
  // InFlo phase-aware data
  cycle_phase?: string;
  phase_info?: {
    name: string;
    description: string;
    duration: string;
    energy_level: string;
    hormonal_focus: string;
  };
  phase_context?: string;
  cooking_methods?: string[];
  recommended_foods?: {
    grains: string[];
    vegetables: string[];
    fruits: string[];
    legumes: string[];
    nuts: string[];
  };
  inflo_enhanced?: boolean;
}

export default function RecommendationsScreen({ intakeData, onBack, onHabitsSelected, onInterventionSelected }: RecommendationsScreenProps) {
  const [recommendations, setRecommendations] = useState<RecommendationData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedIntervention, setSelectedIntervention] = useState<Intervention | null>(null);
  const [expandedInterventions, setExpandedInterventions] = useState<Set<number>>(new Set());
  const [showPeriodSelection, setShowPeriodSelection] = useState(false);

  useEffect(() => {
    console.log('🔄 RecommendationsScreen useEffect triggered with intakeData:', intakeData);
    if (intakeData) {
      fetchRecommendations();
    } else {
      console.warn('⚠️ No intakeData provided to RecommendationsScreen');
      setError('No intake data available. Please complete the intake process first.');
      setLoading(false);
    }
  }, [intakeData]);

  const fetchRecommendations = async () => {
    try {
      console.log('🚀 Starting fetchRecommendations with intakeData:', intakeData);
      setLoading(true);
      setError(null);
      console.log('📡 Calling getRecommendations API...');
      const result = await getRecommendations(intakeData);
      console.log('📡 API result:', result);
      
      if (result.success) {
        // Handle both old and new API response formats
        const data = result.data;
        console.log('📊 API Response data:', JSON.stringify(data, null, 2));
        
        // Check if it's the new format (multiple interventions)
        if (data.interventions && Array.isArray(data.interventions)) {
          // Transform the API response to match the expected format
          const transformedData: RecommendationData = {
            ...data,
            interventions: data.interventions.map((intervention: any) => ({
              id: intervention.intervention_id,
              name: intervention.intervention_name,
              profile_match: intervention.intervention_profile,
              what_will_you_be_doing: intervention.what_will_you_be_doing,
              why_recommended: intervention.why_recommended,
              similarity_score: intervention.similarity_score,
              scientific_source: intervention.scientific_source,
              habits: (intervention.habits || []).map((habit: string, index: number) => ({
                number: index + 1,
                description: habit
              }))
            }))
          };
          console.log('🔄 Transformed data:', JSON.stringify(transformedData, null, 2));
          console.log('🔄 Setting recommendations state...');
          setRecommendations(transformedData);
          console.log('✅ Recommendations state set successfully');
        } else {
          // Convert old format to new format
          const convertedData: RecommendationData = {
            intake_summary: data.intake_summary || '',
            interventions: [{
              id: data.intervention_id || 0,
              name: data.recommended_intervention || '',
              profile_match: data.reasoning || '',
              similarity_score: data.similarity_score || 0,
              scientific_source: data.scientific_reference || '',
              habits: (data.habits || []).map((habit: string, index: number) => ({
                number: index + 1,
                description: habit
              }))
            }],
            total_found: 1,
            min_similarity_used: 0.5,
            additional_inflo_context: data.additional_inflo_context,
            data_collection: data.data_collection,
            cycle_phase: data.cycle_phase,
            phase_info: data.phase_info
          };
          setRecommendations(convertedData);
        }
      } else {
        console.log('❌ API call failed:', result.error);
        setError(result.error || 'Unknown error occurred');
      }
    } catch (err) {
      console.error('Recommendation fetch error:', err);
      setError('Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  const toggleInterventionExpansion = (interventionId: number) => {
    setExpandedInterventions(prev => {
      const newSet = new Set(prev);
      if (newSet.has(interventionId)) {
        newSet.delete(interventionId);
      } else {
        newSet.add(interventionId);
      }
      return newSet;
    });
  };

  const handlePeriodSelected = (periodData: {
    intervention: Intervention;
    durationDays: number;
    startDate: string;
    endDate: string;
  }) => {
    setShowPeriodSelection(false);
    if (onInterventionSelected) {
      onInterventionSelected(periodData.intervention, {
        durationDays: periodData.durationDays,
        startDate: periodData.startDate,
        endDate: periodData.endDate,
      });
    }
  };

  const handleBackFromPeriod = () => {
    setShowPeriodSelection(false);
  };


  if (loading) {
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#3b82f6" />
          <Text style={styles.loadingText}>Generating your personalized recommendations...</Text>
        </View>
      </SafeAreaView>
    );
  }

  if (error) {
    console.log('❌ Error state:', error);
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>Oops! Something went wrong</Text>
          <Text style={styles.errorText}>
            {typeof error === 'string' ? error : JSON.stringify(error)}
          </Text>
          <TouchableOpacity style={styles.retryButton} onPress={fetchRecommendations}>
            <Text style={styles.retryButtonText}>Try Again</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  if (!recommendations) {
    console.log('❌ No recommendations available, state:', { recommendations, loading, error });
    return (
      <SafeAreaView style={styles.container}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorTitle}>No recommendations available</Text>
          <Text style={styles.errorText}>Debug: {JSON.stringify({ recommendations, loading, error })}</Text>
          <TouchableOpacity style={styles.retryButton} onPress={onBack}>
            <Text style={styles.retryButtonText}>Go Back</Text>
          </TouchableOpacity>
        </View>
      </SafeAreaView>
    );
  }

  // Show period selection screen if intervention is selected
  if (showPeriodSelection && selectedIntervention) {
    return (
      <InterventionPeriodScreen
        intervention={selectedIntervention}
        onPeriodSelected={handlePeriodSelected}
        onBack={handleBackFromPeriod}
      />
    );
  }

  console.log('🎯 Rendering recommendations screen with:', { 
    recommendations: recommendations ? {
      total_found: recommendations.total_found,
      interventions_count: recommendations.interventions?.length,
      first_intervention: recommendations.interventions?.[0]?.name
    } : null,
    loading,
    error
  });

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* Header */}
        <View style={styles.header}>
          <TouchableOpacity style={styles.backButton} onPress={onBack}>
            <Text style={styles.backButtonText}>← Back</Text>
          </TouchableOpacity>
          <Text style={styles.title}>Your Recommendations</Text>
          <Text style={styles.subtitle}>Personalized for your unique profile</Text>
        </View>


        {/* Multiple Intervention Options */}
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Choose Your Intervention</Text>
          <Text style={styles.interventionSubtitle}>
            We found {recommendations.total_found} intervention{recommendations.total_found !== 1 ? 's' : ''} that match your profile (similarity ≥ {Math.round(recommendations.min_similarity_used * 100)}%)
          </Text>
          <Text style={styles.encouragementText}>
            Let's get started with 1 intervention to get you going
          </Text>
          
          {recommendations.interventions.map((intervention, index) => {
            const isExpanded = expandedInterventions.has(intervention.id);
            const shouldTruncate = intervention.profile_match.length > 150;
            const displayText = isExpanded || !shouldTruncate 
              ? intervention.profile_match 
              : intervention.profile_match.substring(0, 150) + '...';

            return (
              <View key={intervention.id} style={styles.interventionCard}>
                <TouchableOpacity
                  style={[
                    styles.interventionOption,
                    selectedIntervention?.id === intervention.id && styles.interventionOptionSelected
                  ]}
                  onPress={() => {
                    setSelectedIntervention(intervention);
                  }}
                >
                  <View style={styles.interventionHeader}>
                    <Text style={[
                      styles.interventionName,
                      selectedIntervention?.id === intervention.id && styles.interventionNameSelected
                    ]}>
                      {intervention.name}
                    </Text>
                    <Text style={styles.similarityScore}>
                      {Math.round(intervention.similarity_score * 100)}% match
                    </Text>
                  </View>
                  
                  <Text style={styles.profileMatch}>
                    {displayText}
                  </Text>
                  
                  {/* Why recommended section */}
                  {intervention.why_recommended && (
                    <View style={styles.whyRecommendedSection}>
                      <Text style={styles.whyRecommendedTitle}>Why this is perfect for you:</Text>
                      <Text style={styles.whyRecommendedText}>
                        {intervention.why_recommended}
                      </Text>
                    </View>
                  )}
                  
                  {/* Show "What will you be doing?" when expanded */}
                  {isExpanded && intervention.what_will_you_be_doing && (
                    <View style={styles.whatWillYouBeDoingSection}>
                      <Text style={styles.whatWillYouBeDoingTitle}>What will you be doing?</Text>
                      <Text style={styles.whatWillYouBeDoingText}>
                        {intervention.what_will_you_be_doing}
                      </Text>
                    </View>
                  )}
                  
                  
                  {/* Show habits when expanded */}
                  {isExpanded && intervention.habits && intervention.habits.length > 0 && (
                    <View style={styles.habitsSection}>
                      <Text style={styles.habitsTitle}>Habits to implement:</Text>
                      {intervention.habits.map((habit, index) => (
                        <View key={index} style={styles.habitItem}>
                          <Text style={styles.habitNumber}>{index + 1}.</Text>
                          <Text style={styles.habitDescription}>{typeof habit === 'string' ? habit : habit.description || habit}</Text>
                        </View>
                      ))}
                    </View>
                  )}
                  
                  {shouldTruncate && (
                    <TouchableOpacity
                      style={styles.readMoreButton}
                      onPress={(e) => {
                        e.stopPropagation(); // Prevent triggering the parent TouchableOpacity
                        toggleInterventionExpansion(intervention.id);
                      }}
                    >
                      <Text style={styles.readMoreText}>
                        {isExpanded ? 'Read Less' : 'Read More'}
                      </Text>
                    </TouchableOpacity>
                  )}
                </TouchableOpacity>
              </View>
            );
          })}
        </View>

        {/* Start Intervention Button */}
        {selectedIntervention && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Ready to Start?</Text>
            <Text style={styles.startInterventionText}>
              You've selected: <Text style={styles.selectedInterventionName}>{selectedIntervention.name}</Text>
            </Text>
            <TouchableOpacity 
              style={styles.startInterventionButton}
              onPress={() => setShowPeriodSelection(true)}
            >
              <Text style={styles.startInterventionButtonText}>Start with this intervention</Text>
            </TouchableOpacity>
          </View>
        )}


        {/* Phase-Optimized Foods */}
        {recommendations.recommended_foods && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Phase-Optimized Foods</Text>
            <Text style={styles.foodContext}>
              These foods are specifically beneficial during your {recommendations.phase_info?.name}
            </Text>
            <View style={styles.foodCategories}>
              <View style={styles.foodCategory}>
                <Text style={styles.foodCategoryTitle}>Grains</Text>
                <Text style={styles.foodList}>{recommendations.recommended_foods.grains.join(', ')}</Text>
              </View>
              <View style={styles.foodCategory}>
                <Text style={styles.foodCategoryTitle}>Vegetables</Text>
                <Text style={styles.foodList}>{recommendations.recommended_foods.vegetables.slice(0, 5).join(', ')}</Text>
              </View>
              <View style={styles.foodCategory}>
                <Text style={styles.foodCategoryTitle}>Fruits</Text>
                <Text style={styles.foodList}>{recommendations.recommended_foods.fruits.slice(0, 5).join(', ')}</Text>
              </View>
            </View>
          </View>
        )}



        {/* Additional Context */}
        {recommendations.additional_inflo_context && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Additional Insights</Text>
            <Text style={styles.contextText}>{recommendations.additional_inflo_context}</Text>
          </View>
        )}

        {/* Data Collection Status */}
        {recommendations.data_collection && (
          <View style={styles.card}>
            <Text style={styles.cardTitle}>Data Saved</Text>
            <Text style={styles.dataText}>
              ✅ Your story has been saved and will help other women with similar challenges
            </Text>
          </View>
        )}

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
    paddingHorizontal: 24,
    paddingBottom: 40,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  loadingText: {
    fontSize: 16,
    color: '#64748b',
    marginTop: 16,
    textAlign: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 24,
  },
  errorTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: '#ef4444',
    marginBottom: 8,
  },
  errorText: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
    marginBottom: 24,
  },
  retryButton: {
    backgroundColor: '#3b82f6',
    borderRadius: 8,
    paddingHorizontal: 24,
    paddingVertical: 12,
  },
  retryButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#ffffff',
  },
  header: {
    paddingVertical: 24,
    alignItems: 'center',
  },
  backButton: {
    alignSelf: 'flex-start',
    marginBottom: 16,
  },
  backButtonText: {
    fontSize: 16,
    color: '#3b82f6',
    fontWeight: '500',
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1e293b',
    textAlign: 'center',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    textAlign: 'center',
  },
  card: {
    backgroundColor: '#ffffff',
    borderRadius: 16,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.05,
    shadowRadius: 8,
    elevation: 2,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 12,
  },
  summaryText: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 24,
  },
  interventionNameOld: {
    fontSize: 20,
    fontWeight: '600',
    color: '#3b82f6',
    marginBottom: 8,
  },
  similarityScoreOld: {
    fontSize: 14,
    color: '#10b981',
    fontWeight: '500',
    marginBottom: 12,
  },
  reasoning: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 22,
  },
  habitItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 12,
    padding: 12,
    backgroundColor: '#f9fafb',
    borderRadius: 8,
  },
  habitNumber: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#3b82f6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
    marginTop: 2,
  },
  habitNumberText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#ffffff',
  },
  habitText: {
    flex: 1,
    fontSize: 16,
    color: '#374151',
    lineHeight: 22,
  },
  referenceText: {
    fontSize: 14,
    color: '#3b82f6',
    textDecorationLine: 'underline',
  },
  contextText: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 22,
    fontStyle: 'italic',
  },
  dataText: {
    fontSize: 16,
    color: '#10b981',
    fontWeight: '500',
  },
  // InFlo Phase-Aware Styles
  phaseCard: {
    backgroundColor: '#f0f9ff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
    borderLeftWidth: 4,
    borderLeftColor: '#3b82f6',
  },
  phaseTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 8,
  },
  phaseName: {
    fontSize: 20,
    fontWeight: '700',
    color: '#3b82f6',
    marginBottom: 8,
  },
  phaseDescription: {
    fontSize: 16,
    color: '#374151',
    lineHeight: 22,
    marginBottom: 12,
  },
  phaseDetails: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
  },
  phaseDetail: {
    fontSize: 14,
    color: '#6b7280',
    backgroundColor: '#ffffff',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
  },
  phaseContext: {
    fontSize: 14,
    color: '#6b7280',
    fontStyle: 'italic',
    marginBottom: 16,
  },
  cookingMethods: {
    marginTop: 16,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#e5e7eb',
  },
  cookingTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  cookingText: {
    fontSize: 14,
    color: '#6b7280',
  },
  foodContext: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 16,
  },
  foodCategories: {
    gap: 12,
  },
  foodCategory: {
    backgroundColor: '#f9fafb',
    borderRadius: 8,
    padding: 12,
  },
  foodCategoryTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 4,
  },
  foodList: {
    fontSize: 14,
    color: '#6b7280',
    lineHeight: 20,
  },
  // New styles for enhanced profile summary
  // New styles for multiple interventions
  interventionSubtitle: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
    textAlign: 'center',
  },
  encouragementText: {
    fontSize: 14,
    color: '#6b7280',
    textAlign: 'center',
    marginBottom: 16,
  },
  interventionOption: {
    borderWidth: 1,
    borderColor: '#e5e7eb',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    backgroundColor: '#ffffff',
  },
  interventionOptionSelected: {
    borderColor: '#3b82f6',
    backgroundColor: '#f0f9ff',
  },
  interventionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  interventionName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1e293b',
    flex: 1,
    marginRight: 12,
  },
  interventionNameSelected: {
    color: '#3b82f6',
  },
  similarityScore: {
    fontSize: 14,
    color: '#10b981',
    fontWeight: '500',
  },
  profileMatch: {
    fontSize: 14,
    color: '#6b7280',
    marginBottom: 8,
    lineHeight: 20,
  },
  scientificSource: {
    fontSize: 12,
    color: '#3b82f6',
    textDecorationLine: 'underline',
  },
  selectedInterventionTitle: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '500',
    marginBottom: 4,
    textAlign: 'center',
  },
  habitsSelectionNote: {
    fontSize: 13,
    color: '#6b7280',
    fontStyle: 'italic',
    marginBottom: 12,
    textAlign: 'center',
  },
  // New styles for Read More functionality
  interventionCard: {
    marginBottom: 12,
  },
  readMoreButton: {
    paddingVertical: 6,
    paddingHorizontal: 10,
    alignSelf: 'flex-end',
    marginTop: 8,
    backgroundColor: '#f8fafc',
    borderRadius: 6,
    borderWidth: 1,
    borderColor: '#e2e8f0',
  },
  readMoreText: {
    fontSize: 14,
    color: '#3b82f6',
    fontWeight: '500',
  },
  // Habits preview styles
  habitsPreview: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#3b82f6',
  },
  habitsPreviewTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 8,
  },
  habitPreviewItem: {
    fontSize: 13,
    color: '#6b7280',
    marginBottom: 4,
    lineHeight: 18,
  },
  habitsPreviewNote: {
    fontSize: 12,
    color: '#9ca3af',
    fontStyle: 'italic',
    marginTop: 4,
  },
  // Start intervention button styles
  startInterventionText: {
    fontSize: 16,
    color: '#374151',
    marginBottom: 16,
    textAlign: 'center',
  },
  selectedInterventionName: {
    fontWeight: '600',
    color: '#1f2937',
  },
  startInterventionButton: {
    backgroundColor: '#10b981',
    paddingVertical: 14,
    paddingHorizontal: 24,
    borderRadius: 12,
    alignItems: 'center',
  },
  startInterventionButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  // "What will you be doing?" section styles
  whatWillYouBeDoingSection: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f0f9ff',
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#3b82f6',
  },
  whatWillYouBeDoingTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 8,
  },
  whatWillYouBeDoingText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  // Habits section styles
  habitsSection: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#f8fafc',
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#10b981',
  },
  habitsTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 8,
  },
  habitItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    marginBottom: 8,
  },
  habitNumber: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10b981',
    marginRight: 8,
    minWidth: 20,
  },
  habitDescription: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  // "Why recommended" section styles
  whyRecommendedSection: {
    marginTop: 12,
    padding: 12,
    backgroundColor: '#F3F4F6',
    borderRadius: 8,
    borderLeftWidth: 3,
    borderLeftColor: '#8B5CF6',
  },
  whyRecommendedTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1e293b',
    marginBottom: 8,
  },
  whyRecommendedText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
});
