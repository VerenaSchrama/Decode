# User Flow Improvements: Intake → Habit Tracking → Analysis

## Executive Summary
The current app flow works but has several pain points that create friction and potential data loss. These recommendations focus on making the experience smoother, more reliable, and easier to maintain.

---

## 1. **State Management (High Priority)**

### Current Issues
- Heavy prop drilling through 4+ component layers
- State managed locally in `App.tsx`, making it difficult to access from nested screens
- `setTimeout` hack needed to ensure state updates (line 44 in AppNavigator.tsx)
- DailyHabitsScreen falls back to API calls when props aren't available (indicates data flow issues)

### Recommended Solution
✅ **Created `AppStateContext.tsx`** - Centralized state management

**Benefits:**
- Eliminates prop drilling
- Any component can access app state
- Easier to persist and restore state
- Better TypeScript support

**Implementation:**
```typescript
// Wrap App with AppStateProvider
<AppStateProvider>
  <AppContent />
</AppStateProvider>

// Use anywhere:
const { state, updateIntakeData } = useAppState();
```

---

## 2. **Automatic Session Restoration (High Priority)**

### Current Issues
- Session restoration only happens on login, not on app restart
- User has to manually navigate if they close the app mid-flow
- No indication of where they left off

### Recommended Solution

**A. Auto-detect user progress on app start:**
```typescript
useEffect(() => {
  if (isAuthenticated && user?.id) {
    const restoreSession = async () => {
      const session = await SessionService.restoreUserSession(user.id);
      if (session) {
        // Auto-navigate to appropriate screen
        if (session.current_intervention) {
          setCurrentScreen('main-app');
        } else if (session.intake_data && !session.current_intervention) {
          setCurrentScreen('recommendations');
        } else {
          setCurrentScreen('story-intake');
        }
        // Restore all state
        updateAppState(session);
      }
    };
    restoreSession();
  }
}, [isAuthenticated]);
```

**B. Add "Continue Where You Left Off" screen:**
- Show a welcome back screen with:
  - Last completed step
  - Quick action buttons
  - Progress indicator

**C. Save progress automatically:**
- Save intake data after each step
- Save intervention selection immediately
- Don't rely on user completing entire flow

---

## 3. **Improve Onboarding Flow (Medium Priority)**

### Current Issues
- Long multi-step intake can feel overwhelming
- No progress indicator showing how many steps remain
- No ability to save and come back later

### Recommended Solutions

**A. Add progress indicator:**
```tsx
<View style={styles.progressBar}>
  <Text>Step {currentStep} of {totalSteps}</Text>
  <ProgressBar progress={currentStep / totalSteps} />
</View>
```

**B. Allow saving draft:**
- Save intake data to AsyncStorage after each step
- Show "Save & Continue Later" button
- Restore draft on return

**C. Smart step skipping:**
- Already implemented for users without periods ✅
- Could extend: Skip dietary preferences if user selects "no restrictions"

---

## 4. **Error Handling & Recovery (High Priority)**

### Current Issues
- API failures can leave user stuck
- No retry mechanisms
- Silent failures (console.log only)

### Recommended Solutions

**A. Add Error Boundaries:**
```tsx
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    // Log to error tracking service
    // Show user-friendly error screen
    // Offer recovery options
  }
}
```

**B. Network Error Handling:**
```typescript
const fetchWithRetry = async (fn, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

**C. Offline Mode:**
- Queue API calls when offline
- Sync when connection restored
- Show clear offline indicator

---

## 5. **Loading States & Feedback (Medium Priority)**

### Current Issues
- Inconsistent loading indicators
- Some API calls have no loading state
- Long waits (e.g., `/recommend` endpoint) can feel broken

### Recommended Solutions

**A. Global Loading Indicator:**
```tsx
const LoadingOverlay = ({ visible, message }) => (
  visible && (
    <Modal transparent>
      <View style={styles.overlay}>
        <ActivityIndicator />
        <Text>{message || 'Loading...'}</Text>
      </View>
    </Modal>
  )
);
```

**B. Skeleton Screens:**
- Show skeleton UI while loading recommendations
- Better UX than spinner

**C. Optimistic Updates:**
- Show success immediately for habit tracking
- Sync in background
- Rollback if error

---

## 6. **Data Synchronization (Medium Priority)**

### Current Issues
- DailyHabitsScreen loads habits from API as fallback (line 341-369)
- Indicates data might not be properly passed down
- Race conditions possible

### Recommended Solution

**A. Single Source of Truth:**
- Use AppStateContext for all app data
- API calls only for fetching, not for fallbacks

**B. Data Validation Layer:**
```typescript
const validateAndLoadHabits = async () => {
  if (state.selectedHabits.length > 0) {
    return state.selectedHabits;
  }
  // Only fetch if truly missing
  const activeHabits = await apiService.getActiveHabits(userId);
  updateSelectedHabits(activeHabits);
  return activeHabits;
};
```

---

## 7. **Navigation Improvements (Low Priority)**

### Current Issues
- Screen transitions feel abrupt
- No deep linking support
- Hard to test individual flows

### Recommended Solutions

**A. Use React Navigation properly:**
- Already using NavigationContainer ✅
- Add navigation params for deep linking
- Add transition animations

**B. Deep Linking:**
```typescript
// Support URLs like: app://recommendations?intake_id=123
const linking = {
  prefixes: ['app://'],
  config: {
    screens: {
      Recommendations: 'recommendations',
      MainApp: 'main-app',
    },
  },
};
```

---

## 8. **User Experience Enhancements**

### A. Skip Optional Steps
- Make dietary preferences truly optional
- Allow skipping to recommendations
- Add "I'll set this up later" options

### B. Quick Actions
- "Start Fresh" button if user wants to redo intake
- "Change Intervention" button in main app
- "Edit Habits" button

### C. Progress Tracking
- Show visual progress through entire flow
- Celebrate milestones (intake complete, first habit tracked)
- Gamification elements (streaks, achievements)

---

## 9. **Performance Optimizations**

### A. Lazy Loading
- Load recommendations screen only when needed
- Code-split heavy screens

### B. Caching
- Cache recommendations response
- Cache intervention data
- Cache habit data

### C. Debouncing
- Debounce API calls during intake form typing
- Debounce habit tracking saves

---

## 10. **Testing & Quality**

### A. Add Error Tracking
- Integrate Sentry or similar
- Track API failures
- Monitor user flows

### B. Analytics
- Track where users drop off
- Measure time to complete intake
- Identify friction points

### C. A/B Testing
- Test different onboarding flows
- Test recommendation presentation styles

---

## Implementation Priority

1. **Critical (Do First):**
   - ✅ AppStateContext (created)
   - Automatic session restoration
   - Error boundaries

2. **High Priority:**
   - Remove setTimeout hack
   - Fix data synchronization
   - Add retry mechanisms

3. **Medium Priority:**
   - Loading states consistency
   - Progress indicators
   - Offline support

4. **Nice to Have:**
   - Deep linking
   - A/B testing
   - Analytics

---

## Quick Wins (Can implement immediately)

1. **Add "Continue" button to DailyHabitsScreen** if no habits found
2. **Show loading spinner** during `/recommend` API call
3. **Add error toast** messages for API failures
4. **Save intake draft** to AsyncStorage after each step
5. **Add progress bar** to intake flow

---

## Code Examples

### Using AppStateContext:
```tsx
// In any component
import { useAppState } from '../contexts/AppStateContext';

function MyComponent() {
  const { state, updateIntakeData } = useAppState();
  
  // Access state anywhere
  const habits = state.selectedHabits;
  
  // Update state
  const handleComplete = (data) => {
    updateIntakeData(data);
  };
}
```

### Session Restoration:
```tsx
useEffect(() => {
  if (user?.id && !state.intakeData) {
    SessionService.restoreUserSession(user.id)
      .then(session => {
        if (session?.intake_data) {
          updateIntakeData(session.intake_data);
          // Auto-navigate
          if (session.current_intervention) {
            updateCurrentScreen('main-app');
          }
        }
      });
  }
}, [user?.id]);
```

---

## Metrics to Track

- Time to complete intake
- Drop-off rate at each step
- API call success rate
- Session restoration success rate
- Average time before first habit tracked
- User return rate

