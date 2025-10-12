# 🚀 Quick Start: Mobile App Development

## **Step 1: Install Prerequisites**

```bash
# Install Node.js (if not already installed)
# Download from https://nodejs.org/

# Install Expo CLI globally
npm install -g @expo/cli

# Install Expo Go app on your phone
# iOS: App Store
# Android: Google Play Store
```

## **Step 2: Create Mobile Project**

```bash
# Navigate to your project root
cd /Users/verena_werk/Documents/SW_projects/hfc_app_v2

# Create React Native project with Expo
npx create-expo-app@latest mobile --template blank-typescript

# Navigate to mobile directory
cd mobile
```

## **Step 3: Install Core Dependencies**

```bash
# Navigation
npm install @react-navigation/native @react-navigation/stack @react-navigation/bottom-tabs

# Navigation dependencies
npx expo install react-native-screens react-native-safe-area-context

# API and state management
npm install axios @tanstack/react-query zustand

# UI components
npm install native-base react-native-svg

# Icons
npx expo install @expo/vector-icons
```

## **Step 4: Basic Project Structure**

Create these directories in your `mobile/src` folder:

```
mobile/src/
├── components/     # Reusable UI components
├── screens/        # App screens
├── services/       # API calls and business logic
├── navigation/     # Navigation configuration
├── types/          # TypeScript type definitions
└── utils/          # Helper functions
```

## **Step 5: Test Your Setup**

```bash
# Start the development server
npx expo start

# Scan the QR code with Expo Go app on your phone
# Or press 'i' for iOS simulator, 'a' for Android emulator
```

## **Step 6: Create Your First Screen**

Create `mobile/src/screens/HomeScreen.tsx`:

```typescript
import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

export default function HomeScreen() {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>HerFoodCode</Text>
      <Text style={styles.subtitle}>Your Health Companion</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
  },
});
```

## **Step 7: Set Up API Service**

Create `mobile/src/services/api.ts`:

```typescript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000'; // Change to your backend URL

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API endpoints
export const endpoints = {
  recommend: '/recommend',
  health: '/health',
  userInsights: (userId: string) => `/user/${userId}/insights`,
  userHabits: (userId: string) => `/user/${userId}/habits`,
};
```

## **Step 8: Test API Connection**

Create `mobile/src/screens/TestScreen.tsx`:

```typescript
import React, { useState, useEffect } from 'react';
import { View, Text, Button, StyleSheet } from 'react-native';
import { api, endpoints } from '../services/api';

export default function TestScreen() {
  const [status, setStatus] = useState('Testing...');

  const testAPI = async () => {
    try {
      const response = await api.get(endpoints.health);
      setStatus(`✅ API Connected! RAG: ${response.data.rag_pipeline}`);
    } catch (error) {
      setStatus(`❌ API Error: ${error.message}`);
    }
  };

  useEffect(() => {
    testAPI();
  }, []);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>API Test</Text>
      <Text style={styles.status}>{status}</Text>
      <Button title="Test Again" onPress={testAPI} />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 20,
  },
  status: {
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
});
```

## **Step 9: Next Steps**

1. **Set up navigation** between screens
2. **Create the health assessment form** using your backend's UserInput model
3. **Build the recommendation display** screen
4. **Add habit tracking** functionality
5. **Implement user profile** management

## **🔧 Troubleshooting**

### **Common Issues:**

1. **"Metro bundler not found"**
   ```bash
   npx expo start --clear
   ```

2. **"Cannot connect to API"**
   - Make sure your backend is running on `http://localhost:8000`
   - Check if your phone and computer are on the same network
   - For physical device testing, use your computer's IP address instead of localhost

3. **"Module not found"**
   ```bash
   npm install
   npx expo start --clear
   ```

## **📱 Testing on Device**

1. **Install Expo Go** on your phone
2. **Start the development server**: `npx expo start`
3. **Scan the QR code** with Expo Go
4. **Test the app** on your device

## **🎯 Success Checklist**

- [ ] Expo project created
- [ ] Dependencies installed
- [ ] Basic screen created
- [ ] API service configured
- [ ] App runs on device
- [ ] API connection working

---

**Ready to start building your mobile app!** 🚀

