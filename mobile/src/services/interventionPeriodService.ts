/**
 * Intervention Period Service
 * Handles tracking of intervention periods and completion status
 */

import { api } from './api';

export interface InterventionPeriod {
  id: string;
  user_id: string;
  intake_id: string;
  intervention_name: string;
  intervention_id?: string;
  selected_habits: string[];
  start_date: string;
  planned_end_date?: string;
  actual_end_date?: string;
  status: 'active' | 'completed' | 'paused' | 'abandoned';
  cycle_phase_at_start?: string;
  completion_percentage: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface StartInterventionRequest {
  intake_id: string;
  intervention_name: string;
  selected_habits: string[];
  intervention_id?: string;
  planned_duration_days?: number;
  cycle_phase?: string;
}

export interface CompleteInterventionRequest {
  completion_percentage?: number;
  notes?: string;
}

export class InterventionPeriodService {
  private static instance: InterventionPeriodService;
  
  private constructor() {}
  
  static getInstance(): InterventionPeriodService {
    if (!InterventionPeriodService.instance) {
      InterventionPeriodService.instance = new InterventionPeriodService();
    }
    return InterventionPeriodService.instance;
  }

  /**
   * Start tracking a new intervention period
   */
  async startInterventionPeriod(
    request: StartInterventionRequest,
    accessToken: string
  ): Promise<{ success: boolean; period_id?: string; message?: string; error?: string }> {
    try {
      console.log('🌐 InterventionPeriodService: Making API call to /intervention-periods/start');
      console.log('📤 Request payload:', JSON.stringify(request, null, 2));
      console.log('🔐 Access token present:', !!accessToken);
      
      const response = await api.post('/intervention-periods/start', request, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('✅ InterventionPeriodService: API response status:', response.status);
      console.log('📥 Response data:', response.data);

      if (response.status === 200) {
        return {
          success: true,
          period_id: response.data.period_id,
          message: response.data.message
        };
      } else {
        return {
          success: false,
          error: response.data.detail || 'Failed to start intervention period'
        };
      }
    } catch (error: any) {
      console.error('Error starting intervention period:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to start intervention period'
      };
    }
  }

  /**
   * Get progress metrics for a specific intervention period
   */
  /**
   * Reset/change user's active intervention period
   */
  async resetInterventionPeriod(
    request: {
      intervention_id?: number;
      intervention_name: string;
      selected_habits: string[];
      planned_duration_days?: number;
      start_date?: string;
      cycle_phase?: string;
      intake_id?: string;
    },
    accessToken: string
  ): Promise<{ success: boolean; period_id?: string; message?: string; error?: string }> {
    try {
      console.log('🔄 InterventionPeriodService: Resetting intervention period');
      console.log('📤 Request payload:', JSON.stringify(request, null, 2));
      
      const response = await api.post('/intervention-periods/reset', request, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });
      
      console.log('✅ InterventionPeriodService: Reset response status:', response.status);
      console.log('📥 Response data:', response.data);

      if (response.status === 200 && response.data.success) {
        return {
          success: true,
          period_id: response.data.period_id,
          message: response.data.message
        };
      } else {
        return {
          success: false,
          error: response.data.detail || response.data.error || 'Failed to reset intervention period'
        };
      }
    } catch (error: any) {
      console.error('Error resetting intervention period:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.response?.data?.error || error.message || 'Failed to reset intervention period'
      };
    }
  }

  async getInterventionPeriodProgress(
    periodId: string,
    accessToken: string
  ): Promise<{ 
    success: boolean; 
    metrics?: {
      average_mood: number | null;
      days_passed: number;
      total_days: number;
      fully_completed_days: number;
      tracked_days: number;
      completion_rate: number;
    };
    error?: string;
  }> {
    try {
      const response = await api.get(`/intervention-periods/${periodId}/progress`, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 200 && response.data.success) {
        return {
          success: true,
          metrics: response.data.metrics
        };
      } else {
        return {
          success: false,
          error: response.data.detail || 'Failed to get progress metrics'
        };
      }
    } catch (error: any) {
      console.error('Error getting intervention period progress:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to get progress metrics'
      };
    }
  }

  /**
   * Get all intervention periods for a user
   */
  async getUserInterventionPeriods(
    accessToken: string
  ): Promise<{ success: boolean; periods?: InterventionPeriod[]; count?: number; error?: string }> {
    try {
      const response = await api.get('/intervention-periods/history', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 200) {
        return {
          success: true,
          periods: response.data.periods || [],
          count: response.data.count || 0
        };
      } else {
        return {
          success: false,
          error: response.data.detail || 'Failed to get intervention periods'
        };
      }
    } catch (error: any) {
      console.error('Error getting user intervention periods:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to get intervention periods'
      };
    }
  }

  /**
   * Get the currently active intervention period
   */
  async getActiveInterventionPeriod(
    accessToken: string
  ): Promise<{ success: boolean; period?: InterventionPeriod; found?: boolean; error?: string }> {
    try {
      const response = await api.get('/intervention-periods/active', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 200) {
        return {
          success: true,
          period: response.data.period,
          found: response.data.found
        };
      } else {
        return {
          success: false,
          error: response.data.detail || 'Failed to get active intervention'
        };
      }
    } catch (error: any) {
      console.error('Error getting active intervention:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to get active intervention'
      };
    }
  }

  /**
   * Get all intervention periods for the user
   */
  async getInterventionPeriodsHistory(
    accessToken: string
  ): Promise<{ success: boolean; periods?: InterventionPeriod[]; count?: number; error?: string }> {
    try {
      const response = await api.get('/intervention-periods/history', {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 200) {
        return {
          success: true,
          periods: response.data.periods,
          count: response.data.count
        };
      } else {
        return {
          success: false,
          error: response.data.detail || 'Failed to get intervention history'
        };
      }
    } catch (error: any) {
      console.error('Error getting intervention history:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to get intervention history'
      };
    }
  }

  /**
   * Mark an intervention period as completed
   */
  async completeInterventionPeriod(
    periodId: string,
    request: CompleteInterventionRequest,
    accessToken: string
  ): Promise<{ success: boolean; message?: string; error?: string }> {
    try {
      const response = await api.put(`/intervention-periods/${periodId}/complete`, request, {
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.status === 200) {
        return {
          success: true,
          message: response.data.message
        };
      } else {
        return {
          success: false,
          error: response.data.detail || 'Failed to complete intervention'
        };
      }
    } catch (error: any) {
      console.error('Error completing intervention:', error);
      return {
        success: false,
        error: error.response?.data?.detail || error.message || 'Failed to complete intervention'
      };
    }
  }

  /**
   * Calculate days remaining in intervention period
   */
  calculateDaysRemaining(period: InterventionPeriod): number {
    if (!period.planned_end_date) return 0;
    
    const endDate = new Date(period.planned_end_date);
    const now = new Date();
    const diffTime = endDate.getTime() - now.getTime();
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    return Math.max(0, diffDays);
  }

  /**
   * Calculate progress percentage based on time elapsed
   */
  calculateTimeProgress(period: InterventionPeriod): number {
    if (!period.planned_end_date) return 0;
    
    const startDate = new Date(period.start_date);
    const endDate = new Date(period.planned_end_date);
    const now = new Date();
    
    const totalDuration = endDate.getTime() - startDate.getTime();
    const elapsed = now.getTime() - startDate.getTime();
    
    const progress = (elapsed / totalDuration) * 100;
    return Math.min(100, Math.max(0, progress));
  }

  /**
   * Get intervention status display text
   */
  getStatusDisplayText(status: string): string {
    switch (status) {
      case 'active':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      case 'paused':
        return 'Paused';
      case 'abandoned':
        return 'Abandoned';
      default:
        return 'Unknown';
    }
  }

  /**
   * Get status color for UI
   */
  getStatusColor(status: string): string {
    switch (status) {
      case 'active':
        return '#4CAF50'; // Green
      case 'completed':
        return '#2196F3'; // Blue
      case 'paused':
        return '#FF9800'; // Orange
      case 'abandoned':
        return '#F44336'; // Red
      default:
        return '#9E9E9E'; // Gray
    }
  }
}

// Export singleton instance
export const interventionPeriodService = InterventionPeriodService.getInstance();
