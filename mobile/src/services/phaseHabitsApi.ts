/**
 * Phase-Aware Habits API Service
 * Handles API calls for cycle phase-specific habit recommendations
 */

import axios from 'axios';

import { getApiConfig } from '../config/environment';

const API_BASE_URL = getApiConfig().baseUrl;

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface PhaseAwareHabitsResponse {
  user_id: string;
  cycle_phase: string;
  intervention_name: string;
  habits: string[];
  phase_info: {
    name: string;
    description: string;
    duration: string;
    energy_level: string;
    hormonal_focus: string;
  };
  phase_context: string;
  cooking_methods: string[];
  recommended_foods: {
    grains: string[];
    vegetables: string[];
    fruits: string[];
    legumes: string[];
    nuts: string[];
  };
  inflo_enhanced: boolean;
}

/**
 * Get phase-aware habits for a specific cycle phase and intervention
 */
export const getPhaseAwareHabits = async (
  userId: string,
  cyclePhase: string,
  interventionName: string
): Promise<{
  success: boolean;
  data?: PhaseAwareHabitsResponse;
  error?: string;
}> => {
  try {
    const response = await api.get(`/user/${userId}/phase-habits`, {
      params: {
        cycle_phase: cyclePhase,
        intervention_name: interventionName
      }
    });
    
    console.log('✅ Phase-aware habits received:', response.status);
    return {
      success: true,
      data: response.data,
    };
  } catch (error: any) {
    console.error('❌ Phase habits API Error:', error.message);
    return {
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error occurred',
    };
  }
};
