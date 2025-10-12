import { API_BASE_URL } from './api';

export interface InterventionHabit {
  number: number;
  description: string;
}

export interface UserInterventionRequest {
  name: string;
  description: string;
  profile_match: string;
  scientific_source?: string;
  habits: InterventionHabit[];
}

export interface UserInterventionResponse {
  id: string;
  user_id: string;
  name: string;
  description: string;
  profile_match: string;
  scientific_source?: string;
  habits: InterventionHabit[];
  status: string;
  helpful_count: number;
  total_tries: number;
  created_at: string;
  updated_at: string;
}

export interface InterventionFeedbackRequest {
  intervention_id: string;
  helpful: boolean;
  feedback_text?: string;
}

export class UserInterventionsAPI {
  private static baseUrl = `${API_BASE_URL}/interventions`;

  static async submitIntervention(
    intervention: UserInterventionRequest,
    userId: string = 'demo-user'
  ): Promise<UserInterventionResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/submit?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(intervention),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error submitting intervention:', error);
      throw error;
    }
  }

  static async getUserInterventions(userId: string): Promise<UserInterventionResponse[]> {
    try {
      const response = await fetch(`${this.baseUrl}/user/${userId}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting user interventions:', error);
      throw error;
    }
  }

  static async getApprovedInterventions(): Promise<UserInterventionResponse[]> {
    try {
      const response = await fetch(`${this.baseUrl}/approved`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting approved interventions:', error);
      throw error;
    }
  }

  static async submitFeedback(
    interventionId: string,
    feedback: InterventionFeedbackRequest,
    userId: string = 'demo-user'
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/${interventionId}/feedback?user_id=${userId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(feedback),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error submitting feedback:', error);
      throw error;
    }
  }
}
