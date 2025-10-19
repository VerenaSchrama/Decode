import { API_BASE_URL } from './api';

export interface HabitProgress {
  habit: string;
  completed: boolean;
  notes?: string;
}

export interface MoodEntry {
  mood: number;
  symptoms: string[];
  notes: string;
  date: string;
}

export interface DailyProgressRequest {
  user_id: string;
  entry_date: string;
  habits: HabitProgress[];
  mood?: MoodEntry;
  cycle_phase?: string;
}

export interface DailyProgressResponse {
  success: boolean;
  entry_id: string;
  completion_percentage: number;
  completed_habits: number;
  total_habits: number;
}

export interface DailyProgressEntry {
  id: string;
  user_id: string;
  entry_date: string;
  completed_habits: HabitProgress[];
  mood_rating?: number;
  symptoms: string[];
  notes: string;
  total_habits: number;
  completion_percentage: number;
  created_at: string;
  updated_at: string;
}

export interface StreakResponse {
  success: boolean;
  user_id: string;
  current_streak: number;
  last_updated: string;
}

export class DailyProgressAPI {
  private static baseUrl = `${API_BASE_URL}`;

  static async saveDailyProgress(
    progressData: DailyProgressRequest
  ): Promise<DailyProgressResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/daily-progress`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(progressData),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error saving daily progress:', error);
      throw error;
    }
  }

  static async getDailyProgress(
    userId: string,
    days: number = 7
  ): Promise<{ success: boolean; entries: DailyProgressEntry[] }> {
    try {
      const response = await fetch(`${this.baseUrl}/user/${userId}/daily-progress?days=${days}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting daily progress:', error);
      throw error;
    }
  }

  static async getHabitStreak(userId: string): Promise<StreakResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/user/${userId}/streak`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting habit streak:', error);
      throw error;
    }
  }

  static async getDailyHabitsHistory(
    userId: string,
    days: number = 30
  ): Promise<{ success: boolean; entries: DailyHabitsHistoryEntry[]; total_entries: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/user/${userId}/daily-habits-history?days=${days}`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error getting daily habits history:', error);
      throw error;
    }
  }
}

export interface DailyHabitsHistoryEntry {
  id: string;
  date: string;
  total_habits: number;
  completed_habits: number;
  completion_percentage: number;
  mood: {
    mood: number;
    symptoms: string[];
    notes: string;
    date: string;
  } | null;
  habits: Array<{
    habit_name: string;
    completed: boolean;
    mood?: number;
    notes?: string;
  }>;
  created_at: string;
  updated_at: string;
}
