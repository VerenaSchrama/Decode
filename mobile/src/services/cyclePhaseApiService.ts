/**
 * Cycle Phase API Service
 * Manages cycle phase calculation and storage via API
 */

import { getApiConfig } from '../config/environment';
import apiService from './apiService';

export interface CyclePhaseData {
  success: boolean;
  current_phase: string;
  days_since_period: number;
  cycle_length: number;
  last_period_date: string;
  last_updated: string;
  error?: string;
  message?: string;
}

export interface UpdateCyclePhaseRequest {
  last_period_date: string;  // YYYY-MM-DD
  cycle_length: number;      // Average cycle length in days
  auto_recalculate?: boolean; // Default true
}

class CyclePhaseApiService {
  /**
   * Get current cycle phase for authenticated user
   */
  async getCurrentPhase(): Promise<CyclePhaseData> {
    return apiService.getCyclePhase();
  }

  /**
   * Update cycle phase for authenticated user
   */
  async updateCyclePhase(request: UpdateCyclePhaseRequest): Promise<CyclePhaseData> {
    return apiService.updateCyclePhase(request);
  }

  /**
   * Force recalculation of cycle phase for authenticated user
   */
  async recalculateCyclePhase(): Promise<CyclePhaseData> {
    return apiService.recalculateCyclePhase();
  }
}

// Export singleton instance
export const cyclePhaseApiService = new CyclePhaseApiService();

