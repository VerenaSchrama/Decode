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
  id: string;
  user_id: string;
  message: string;
  is_user: boolean;
  timestamp: string;
  context_used?: any;
}

export interface ChatRequest {
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
  private authToken: string | null = null;

  /**
   * Set authentication token for subsequent requests
   */
  setAuthToken(token: string | null) {
    this.authToken = token;
  }

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
    
    // Include Authorization header if auth token is available
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers as Record<string, string>,
    };
    
    if (this.authToken) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.authToken}`;
    }
    
    const requestOptions: RequestInit = {
      ...options,
      headers,
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
  async sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
    // Include Authorization header for authenticated requests
    return this.makeRequest<ChatResponse>('/chat/message', {
      method: 'POST',
      body: JSON.stringify(request),
      // Authorization header should be added by makeRequest if available
    });
  }

  /**
   * Stream chat message response (SSE or chunked text)
   */
  async sendChatMessageStream(
    request: ChatRequest,
    onChunk: (text: string) => void
  ): Promise<void> {
    const url = `${this.config.baseUrl}/chat/stream`;

    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (this.authToken) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${this.authToken}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), Math.max(this.config.timeout, 120000));

    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers,
        body: JSON.stringify(request),
        signal: controller.signal,
      });

      if (!resp.ok || !resp.body) {
        throw new ApiError(`HTTP ${resp.status}: ${resp.statusText}`, resp.status);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buffer += decoder.decode(value, { stream: true });

        // If SSE, split on double newlines and parse lines starting with 'data:'
        const parts = buffer.split('\n\n');
        buffer = parts.pop() || '';
        for (const part of parts) {
          const lines = part.split('\n');
          for (const line of lines) {
            if (line.startsWith('data:')) {
              const text = line.slice(5); // preserve leading spaces from tokens
              if (text && text.trim() !== '[DONE]') onChunk(text);
            }
          }
        }
      }
      // Flush any remaining plain text (non-SSE)
      if (buffer) onChunk(buffer);
    } finally {
      clearTimeout(timeoutId);
    }
  }

  /**
   * Get chat history for authenticated user
   */
  async getChatHistory(): Promise<{ messages: ChatMessage[] }> {
    // Endpoint now uses authentication instead of user_id parameter
    return this.makeRequest<{ messages: ChatMessage[] }>('/chat/history');
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
   * Get user's active habits
   */
  async getActiveHabits(userId: string): Promise<{ habits: Array<{ habit_name: string }>; count: number }> {
    return this.makeRequest<{ habits: Array<{ habit_name: string }>; count: number }>(`/user/${userId}/active-habits`);
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

  // ===== CYCLE PHASE MANAGEMENT =====

  /**
   * Get current cycle phase
   */
  async getCyclePhase(): Promise<any> {
    return this.makeRequest<any>('/user/cycle-phase');
  }

  /**
   * Update cycle phase
   */
  async updateCyclePhase(request: { last_period_date: string; cycle_length: number; auto_recalculate?: boolean }): Promise<any> {
    return this.makeRequest<any>('/user/cycle-phase', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  /**
   * Recalculate cycle phase
   */
  async recalculateCyclePhase(): Promise<any> {
    return this.makeRequest<any>('/user/cycle-phase/recalculate', {
      method: 'POST',
    });
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
