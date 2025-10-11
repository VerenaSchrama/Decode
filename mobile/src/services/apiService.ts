/**
 * Centralized API Service
 * Handles all API calls with error handling, retry logic, and consistent response format
 */

import { getApiConfig } from '../config/environment';

// Custom Error Types
export class ApiError extends Error {
  constructor(
    message: string,
    public status?: number,
    public code?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class NetworkError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}

export class ValidationError extends Error {
  constructor(message: string, public field?: string) {
    super(message);
    this.name = 'ValidationError';
  }
}

// API Response Types
export interface ApiResponse<T = any> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface ChatMessage {
  user_id: string;
  message: string;
  intake_data?: any;
  current_intervention?: any;
  selected_habits?: string[];
}

export interface ChatResponse {
  message: string;
  timestamp: string;
  context_used?: any;
}

export interface CustomInterventionRequest {
  intervention: {
    name: string;
    description: string;
    start_date: string;
    trial_period_days: number;
    habits: string[];
  };
  user_context: any;
}

export interface CustomInterventionResponse {
  assessment: string;
  recommendations: string;
  scientific_basis: string;
  safety_notes: string;
}

export interface DailyProgressRequest {
  user_id: string;
  entry_date: string;
  habits: Array<{
    habit: string;
    completed: boolean;
    notes?: string;
  }>;
  mood?: {
    mood: number;
    symptoms: string[];
    notes: string;
    date: string;
  };
  cycle_phase?: string;
}

export interface HabitStreakResponse {
  current_streak: number;
  longest_streak: number;
  total_days: number;
}

class ApiService {
  private config = getApiConfig();

  /**
   * Make HTTP request with retry logic
   */
  private async makeRequest<T>(
    endpoint: string,
    options: RequestInit = {},
    retryCount = 0
  ): Promise<T> {
    const url = `${this.config.baseUrl}${endpoint}`;
    
    // Create AbortController for timeout
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
    
    const requestOptions: RequestInit = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': this.config.apiKey,
        ...options.headers,
      },
      signal: controller.signal,
    };

    try {
      console.log(`🌐 API Request: ${options.method || 'GET'} ${url}`);
      
      const response = await fetch(url, requestOptions);
      clearTimeout(timeoutId);
      
      if (!response.ok) {
        const errorText = await response.text();
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
        
        try {
          const errorData = JSON.parse(errorText);
          errorMessage = errorData.detail || errorData.message || errorMessage;
        } catch {
          // Use default error message if JSON parsing fails
        }
        
        throw new ApiError(errorMessage, response.status);
      }

      const data = await response.json();
      console.log(`✅ API Response: ${options.method || 'GET'} ${url}`, data);
      
      return data;
    } catch (error) {
      clearTimeout(timeoutId);
      console.error(`❌ API Error: ${options.method || 'GET'} ${url}`, error);
      
      // Retry logic for network errors
      if (retryCount < this.config.retryAttempts && this.shouldRetry(error)) {
        console.log(`🔄 Retrying request (${retryCount + 1}/${this.config.retryAttempts})`);
        await this.delay(1000 * (retryCount + 1)); // Exponential backoff
        return this.makeRequest<T>(endpoint, options, retryCount + 1);
      }
      
      // Handle different error types
      if (error instanceof ApiError) {
        throw error;
      }
      
      if (error instanceof TypeError && error.message.includes('Network request failed')) {
        throw new NetworkError('Unable to connect to server. Please check your internet connection.');
      }
      
      if (error instanceof Error && error.name === 'AbortError') {
        throw new NetworkError('Request timed out. Please try again.');
      }
      
      throw new ApiError(
        error instanceof Error ? error.message : 'An unexpected error occurred',
        0,
        'UNKNOWN_ERROR'
      );
    }
  }

  /**
   * Check if error should trigger a retry
   */
  private shouldRetry(error: any): boolean {
    if (error instanceof ApiError) {
      // Retry on server errors (5xx) and some client errors
      return error.status ? error.status >= 500 || error.status === 429 : false;
    }
    
    // Retry on network errors
    return error instanceof TypeError && error.message.includes('Network request failed');
  }

  /**
   * Delay utility for retry logic
   */
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // ===== CHAT API METHODS =====

  /**
   * Send chat message
   */
  async sendChatMessage(request: ChatMessage): Promise<ChatResponse> {
    return this.makeRequest<ChatResponse>('/chat/message', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Get chat history
   */
  async getChatHistory(userId: string): Promise<{ messages: ChatMessage[] }> {
    return this.makeRequest<{ messages: ChatMessage[] }>(`/chat/history/${userId}`);
  }

  // ===== CUSTOM INTERVENTION API METHODS =====

  /**
   * Validate custom intervention
   */
  async validateCustomIntervention(request: CustomInterventionRequest): Promise<CustomInterventionResponse> {
    return this.makeRequest<CustomInterventionResponse>('/interventions/validate-custom', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  // ===== DAILY PROGRESS API METHODS =====

  /**
   * Save daily progress
   */
  async saveDailyProgress(request: DailyProgressRequest): Promise<{ success: boolean; message: string }> {
    return this.makeRequest<{ success: boolean; message: string }>('/daily-progress', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Get habit streak
   */
  async getHabitStreak(userId: string): Promise<HabitStreakResponse> {
    return this.makeRequest<HabitStreakResponse>(`/user/${userId}/streak`);
  }

  /**
   * Get daily progress history
   */
  async getDailyProgressHistory(userId: string, limit = 30): Promise<any[]> {
    return this.makeRequest<any[]>(`/daily-progress/history/${userId}?limit=${limit}`);
  }

  // ===== PHASE HABITS API METHODS =====

  /**
   * Get phase-aware habits
   */
  async getPhaseAwareHabits(
    userId: string,
    phase: string,
    interventionName: string
  ): Promise<{ success: boolean; data?: { habits: string[] } }> {
    return this.makeRequest<{ success: boolean; data?: { habits: string[] } }>(
      `/phase-habits/${userId}?phase=${phase}&intervention=${encodeURIComponent(interventionName)}`
    );
  }

  // ===== HEALTH CHECK =====

  /**
   * Check API health
   */
  async healthCheck(): Promise<{ status: string; timestamp: string }> {
    return this.makeRequest<{ status: string; timestamp: string }>('/health');
  }
}

// Export singleton instance
export const apiService = new ApiService();
