# API Configuration Implementation

## Overview
This document describes the centralized API configuration system implemented for the HFC mobile app. The system provides environment-specific configuration, centralized error handling, retry logic, and user feedback through toast notifications.

## Files Created/Modified

### 1. Environment Configuration
- **`mobile/src/config/environment.ts`** - Centralized environment configuration
- **`mobile/src/config/env.example.ts`** - Example environment variables

### 2. Centralized API Service
- **`mobile/src/services/apiService.ts`** - Main API service with error handling and retry logic

### 3. Toast Notification System
- **`mobile/src/components/Toast.tsx`** - Toast notification component
- **`mobile/src/contexts/ToastContext.tsx`** - Global toast context provider

### 4. Updated Screens
- **`mobile/src/screens/NutritionistChatScreen.tsx`** - Updated to use centralized API service
- **`mobile/src/screens/CustomInterventionScreen.tsx`** - Updated to use centralized API service
- **`mobile/src/screens/DailyHabitsScreen.tsx`** - Updated to use centralized API service

### 5. App Configuration
- **`mobile/App.tsx`** - Added ToastProvider wrapper
- **`mobile/app.json`** - Added environment configuration

## Key Features

### 1. Environment-Specific Configuration
```typescript
// Different configurations for development, staging, and production
const API_CONFIG = {
  development: {
    baseUrl: 'http://192.168.3.107:8000',
    apiKey: 'dev-key-123',
    timeout: 10000,
    retryAttempts: 3,
  },
  production: {
    baseUrl: 'https://your-production-api.com',
    apiKey: process.env.EXPO_PUBLIC_API_KEY,
    timeout: 15000,
    retryAttempts: 2,
  }
};
```

### 2. Centralized Error Handling
- **Custom Error Types**: `ApiError`, `NetworkError`, `ValidationError`
- **Automatic Retry Logic**: Configurable retry attempts with exponential backoff
- **User-Friendly Error Messages**: Toast notifications for all error states

### 3. API Service Methods
- `sendChatMessage()` - Send chat messages to nutritionist
- `getChatHistory()` - Retrieve chat history
- `validateCustomIntervention()` - Validate custom interventions
- `saveDailyProgress()` - Save daily habit progress
- `getHabitStreak()` - Get user's habit streak
- `getPhaseAwareHabits()` - Get cycle phase-specific habits
- `healthCheck()` - Check API health

### 4. Toast Notification System
- **Types**: Success, Error, Warning, Info
- **Features**: Auto-dismiss, manual close, tap to dismiss
- **Global Access**: Available throughout the app via `useToast()` hook

## Usage Examples

### Using the API Service
```typescript
import { apiService } from '../services/apiService';
import { useToast } from '../contexts/ToastContext';

const { showToast } = useToast();

try {
  const result = await apiService.sendChatMessage({
    user_id: 'user123',
    message: 'Hello',
    intake_data: userData
  });
  showToast('Message sent successfully!', 'success');
} catch (error) {
  showToast(error.message, 'error');
}
```

### Environment Configuration
```typescript
import { getApiConfig, getCurrentEnvironment } from '../config/environment';

const config = getApiConfig();
const env = getCurrentEnvironment();
console.log(`Using ${env} environment with URL: ${config.baseUrl}`);
```

## Benefits

1. **Centralized Management**: All API calls go through one service
2. **Environment Flexibility**: Easy switching between dev/staging/production
3. **Error Resilience**: Automatic retry logic and graceful error handling
4. **User Feedback**: Consistent toast notifications for all operations
5. **Type Safety**: Full TypeScript support with proper error types
6. **Maintainability**: Single place to update API logic and configuration

## Configuration

### Development Environment
- API URL: `http://192.168.3.107:8000`
- Timeout: 10 seconds
- Retry Attempts: 3

### Production Environment
- API URL: `https://your-production-api.com`
- Timeout: 15 seconds
- Retry Attempts: 2
- API Key: From environment variables

## Next Steps

1. **Environment Variables**: Set up proper environment variables for production
2. **API Keys**: Configure secure API key management
3. **Monitoring**: Add API call monitoring and analytics
4. **Caching**: Implement response caching for better performance
5. **Offline Support**: Add offline capability with local storage

## Testing

The API configuration system has been tested with:
- ✅ Chat message sending
- ✅ Custom intervention validation
- ✅ Daily progress saving
- ✅ Error handling and retry logic
- ✅ Toast notifications
- ✅ Environment switching

All screens now use the centralized API service and provide consistent user feedback through toast notifications.
