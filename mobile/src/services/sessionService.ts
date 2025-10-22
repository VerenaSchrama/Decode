/**
 * Session Service
 * Handles user session data restoration and management
 */

import { getApiConfig } from '../config/environment';

export interface SessionData {
  user_id: string;
  intake_data: {
    id: string;
    profile: any;
    lastPeriod: any;
    symptoms: any;
    interventions: any;
    habits: any;
    dietaryPreferences: any;
    created_at: string;
  } | null;
  current_intervention: {
    id: string;
    name: string;
    start_date: string;
    planned_end_date: string;
    cycle_phase_at_start: string;
    completion_percentage: number;
  } | null;
  selected_habits: string[];
  daily_progress: any[];
  intervention_periods: any[];
}

export interface SessionResponse {
  success: boolean;
  session_data: SessionData;
}

export class SessionService {
  private static get baseUrl(): string {
    return getApiConfig().baseUrl;
  }

  /**
   * Get complete user session data for app restoration
   */
  static async getUserSessionData(userId: string): Promise<SessionResponse> {
    try {
      console.log('🔄 SessionService: Loading user session data for:', userId);
      
      const response = await fetch(`${this.baseUrl}/user/${userId}/session-data`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('✅ SessionService: Session data loaded:', data);
      
      return data;
    } catch (error) {
      console.error('❌ SessionService: Error loading session data:', error);
      throw error;
    }
  }

  /**
   * Check if user has existing session data
   */
  static async hasExistingSession(userId: string): Promise<boolean> {
    try {
      const sessionData = await this.getUserSessionData(userId);
      return sessionData.success && (
        sessionData.session_data.intake_data !== null ||
        sessionData.session_data.current_intervention !== null ||
        sessionData.session_data.intervention_periods.length > 0
      );
    } catch (error) {
      console.error('❌ SessionService: Error checking existing session:', error);
      return false;
    }
  }

  /**
   * Restore user session from stored data
   */
  static async restoreUserSession(userId: string): Promise<SessionData | null> {
    try {
      const response = await this.getUserSessionData(userId);
      
      if (response.success) {
        console.log('✅ SessionService: User session restored successfully');
        return response.session_data;
      } else {
        console.log('⚠️ SessionService: No session data found');
        return null;
      }
    } catch (error) {
      console.error('❌ SessionService: Error restoring user session:', error);
      return null;
    }
  }
}

export default SessionService;
