# Chat Authentication Fixes - Scalability & Sustainability Analysis

## Current Implementation Issues

### ❌ **1. Code Duplication**
**Problem:** Token refresh logic exists in **3 places**:
- `mobile/src/services/api.ts` (axios interceptor) - ✅ Already exists
- `mobile/src/services/apiService.ts` (fetch-based) - ⚠️ Just added (duplicate)
- `mobile/src/screens/NutritionistChatScreen.tsx` - ⚠️ Per-screen registration

**Impact:**
- Maintenance burden: changes must be made in multiple places
- Inconsistent behavior between axios and fetch requests
- Higher risk of bugs

### ❌ **2. State Synchronization Problem**
**Problem:** When `apiService` refreshes a token:
- ✅ Updates AsyncStorage
- ✅ Updates `apiService.authToken`
- ❌ **Does NOT update AuthContext state**
- ❌ Components using `useAuth()` get stale session data

**Example:**
```typescript
// In apiService.makeRequest (after refresh):
this.authToken = newSession.access_token; // ✅ Updated
await AsyncStorage.setItem('@auth_session', ...); // ✅ Updated

// But AuthContext state is still:
state.session.access_token = "<old expired token>" // ❌ Stale!
```

### ❌ **3. Per-Screen Registration**
**Problem:** Refresh callback registered in `NutritionistChatScreen.tsx`:
```typescript
// ❌ Registered per screen - not scalable
useEffect(() => {
  apiService.setRefreshTokenCallback(refreshCallback);
}, [session?.access_token]);
```

**Impact:**
- Must register in every screen that uses `apiService`
- Easy to forget
- Inconsistent initialization across screens

### ❌ **4. Race Condition Risk**
**Problem:** Multiple simultaneous 401 errors could:
- Trigger multiple refresh attempts
- Cause race conditions
- Waste resources
- Potentially fail due to concurrent refresh calls

### ❌ **5. Missing Global Registration**
**Problem:** 
- `AuthContext` registers callback globally for `api.ts` (axios)
- But `apiService` (fetch) callback is registered per-screen
- Inconsistent pattern

## ✅ Recommended Solutions

### **Solution 1: Centralize Token Refresh in AuthContext**
Register `apiService` refresh callback **globally** in `AuthContext`, alongside `api.ts`:

```typescript
// In AuthContext.tsx
useEffect(() => {
  const refreshCallback = async (refreshToken: string) => {
    const newSession = await authService.refreshToken(refreshToken);
    // Update AuthContext state
    dispatch({
      type: 'AUTH_SUCCESS',
      payload: { user: state.user, session: newSession },
    });
    return newSession;
  };
  
  // Register for axios (existing)
  setRefreshTokenCallback(refreshCallback);
  
  // ✅ Register for apiService (NEW)
  apiService.setRefreshTokenCallback(refreshCallback);
}, [state.user]);
```

**Benefits:**
- ✅ Single source of truth
- ✅ Automatic state synchronization
- ✅ Works for all screens automatically
- ✅ Consistent with axios pattern

### **Solution 2: Add Refresh Lock Mechanism**
Prevent concurrent refresh attempts:

```typescript
class ApiService {
  private isRefreshing = false;
  private refreshPromise: Promise<any> | null = null;
  
  private async refreshTokenIfNeeded(): Promise<void> {
    if (this.isRefreshing && this.refreshPromise) {
      return this.refreshPromise; // Wait for ongoing refresh
    }
    
    this.isRefreshing = true;
    this.refreshPromise = this.doRefresh();
    
    try {
      await this.refreshPromise;
    } finally {
      this.isRefreshing = false;
      this.refreshPromise = null;
    }
  }
}
```

### **Solution 3: Update AuthContext State After Refresh**
In `apiService.makeRequest`, after successful refresh:

```typescript
// After refreshing token:
const newSession = await this.refreshTokenCallback(session.refresh_token);

// ✅ Notify AuthContext to update state
// This requires exposing a method or using an event system
// Or better: have AuthContext handle all refresh logic
```

### **Solution 4: Remove Per-Screen Registration**
Remove from `NutritionistChatScreen.tsx`:

```typescript
// ❌ REMOVE THIS:
useEffect(() => {
  apiService.setRefreshTokenCallback(refreshCallback);
}, [session?.access_token]);

// ✅ Token refresh is now handled globally in AuthContext
```

## Scalability Assessment

### Current Implementation: ⚠️ **Moderate Risk**
- **Works for now**: ✅ Fixes immediate 401 errors
- **Not scalable**: ❌ Requires changes in every screen
- **Not sustainable**: ❌ State synchronization issues
- **Maintenance burden**: ⚠️ High (3 places to update)

### With Recommended Fixes: ✅ **Production Ready**
- **Scalable**: ✅ Works automatically for all screens
- **Sustainable**: ✅ Single source of truth
- **Maintainable**: ✅ Changes in one place
- **Robust**: ✅ Handles race conditions

## Implementation Priority

1. **HIGH**: Move refresh callback registration to `AuthContext` (global)
2. **HIGH**: Update AuthContext state after refresh
3. **MEDIUM**: Add refresh lock mechanism
4. **LOW**: Remove per-screen registrations

## Conclusion

The current fix **works** but is **not sustainable** for production because:
- ❌ State synchronization issues
- ❌ Code duplication
- ❌ Per-screen registration requirement
- ❌ Race condition risks

**Recommended**: Implement the centralized approach in `AuthContext` for a production-ready solution.

