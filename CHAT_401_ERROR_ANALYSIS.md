# Chat 401 Error Analysis - "Invalid Refresh Token: Already Used"

## Error Flow

```
1. GET /chat/history → 401 (Unauthorized)
2. Frontend detects 401 → Attempts token refresh
3. POST /auth/refresh with refresh_token → 401 "Invalid Refresh Token: Already Used"
4. Refresh fails → Original request fails → Falls back to local storage
```

## Root Cause Analysis

### 🔴 **Problem 1: Refresh Token Rotation (Supabase Behavior)**

**Supabase uses refresh token rotation:**
- When you use a refresh token, Supabase **invalidates the old token** and returns a **new refresh token**
- The old refresh token can **never be used again**
- This is a security feature to prevent token reuse attacks

**What's happening:**
1. First refresh attempt uses `refresh_token_A` → Gets `refresh_token_B` back
2. Second refresh attempt (before first completes) uses `refresh_token_A` again → **"Already Used" error**
3. OR: First refresh succeeds, but stored token is not updated, so next refresh uses old token

### 🔴 **Problem 2: Frontend - No Shared Refresh Lock**

**Issue:**
- `apiService` (fetch-based) has its own refresh lock (`isRefreshing`, `refreshPromise`)
- `api.ts` (axios interceptor) has NO refresh lock
- Both can trigger refresh simultaneously
- They both read the **same old refresh_token** from AsyncStorage
- First refresh succeeds and gets new token
- Second refresh tries to use the old token → **"Already Used"**

**Code locations:**
- `mobile/src/services/apiService.ts` - Has refresh lock (lines 111-112, 172-186)
- `mobile/src/services/api.ts` - NO refresh lock (lines 22-69)
- Both call the same `refreshCallback` from AuthContext, but they don't coordinate

### 🔴 **Problem 3: Race Condition Window**

**Timeline of concurrent refresh:**
```
T0: GET /chat/history → 401
T1: apiService detects 401, reads refresh_token_A from AsyncStorage
T2: axios interceptor detects 401, reads refresh_token_A from AsyncStorage (SAME!)
T3: apiService calls refreshCallback(refresh_token_A) → Starts refresh
T4: axios interceptor calls refreshCallback(refresh_token_A) → Starts refresh (CONCURRENT!)
T5: Backend receives first refresh → Succeeds, returns refresh_token_B
T6: Backend receives second refresh → Fails "Already Used" (refresh_token_A is invalid)
```

### 🔴 **Problem 4: Backend - No Concurrent Refresh Protection**

**Backend `refresh_token()` method:**
```python
async def refresh_token(self, refresh_token: str):
    session = self.client.auth.refresh_session(refresh_token)
    return {
        "access_token": session.session.access_token,
        "refresh_token": session.session.refresh_token,  # NEW token
        "expires_at": session.session.expires_at
    }
```

**Issue:**
- Backend correctly returns new refresh token
- But if multiple requests hit this endpoint with the same old token simultaneously
- First succeeds, second fails with "Already Used"
- No server-side deduplication (not critical if frontend is fixed)

## Solutions Required

### ✅ **Solution 1: Shared Global Refresh Lock (CRITICAL)**

**Problem:** Axios and fetch have separate refresh mechanisms

**Fix:** Create a shared global refresh lock that both use:
- Single source of truth for "is refresh in progress"
- Single promise that all concurrent requests wait for
- Prevents any concurrent refresh attempts

### ✅ **Solution 2: Ensure New Refresh Token Saved Immediately**

**Problem:** New refresh token must be saved before next refresh attempt

**Fix:**
- Save new refresh_token immediately after receiving it
- Use the shared refresh promise to ensure all requests get the same new token
- Don't allow any new refresh attempts until current one completes and saves

### ✅ **Solution 3: Handle "Already Used" Error Gracefully**

**Problem:** When refresh fails with "Already Used", user should be logged out

**Fix:**
- Detect "Already Used" error
- Clear stored session
- Force re-login (refresh token is truly invalid)

## Frontend Problems

1. ❌ **No shared refresh lock** - axios and fetch have separate refresh mechanisms
2. ❌ **Concurrent refresh attempts** - Both can refresh simultaneously with same token
3. ❌ **Race condition window** - Both read old token before either saves new one
4. ❌ **No handling for "Already Used"** - Should force re-login

## Backend Problems

1. ⚠️ **No concurrent refresh protection** - Multiple requests with same token both process
2. ✅ **Refresh token rotation working correctly** - Returns new token (this is correct behavior)
3. ⚠️ **Error message could be clearer** - "Already Used" is correct but could explain rotation

## Recommended Fix Priority

### **CRITICAL (Fix Now):**
1. **Shared global refresh lock** - Prevent concurrent refreshes
2. **Handle "Already Used" error** - Force re-login when refresh token is invalid

### **HIGH PRIORITY:**
3. **Ensure atomic token save** - Save new token immediately in refresh callback
4. **Better error handling** - Clear user message when refresh fails

## Implementation Plan

### ✅ Step 1: Create Global Refresh Lock (COMPLETED)
- Created `mobile/src/services/tokenRefreshManager.ts`
- Shared module for refresh coordination
- Both axios and fetch use the same lock

### ✅ Step 2: Update Axios Interceptor (COMPLETED)
- Uses `performTokenRefresh()` from global manager
- No longer has independent refresh logic
- Shares lock with fetch-based apiService

### ✅ Step 3: Update apiService (COMPLETED)
- Removed private refresh lock
- Uses `performTokenRefresh()` from global manager
- Shares lock with axios interceptor

### ✅ Step 4: Handle "Already Used" (COMPLETED)
- Detects "Already Used" error in all refresh paths
- Clears stored session
- Forces logout via AuthContext dispatch

## Fix Summary

### What Was Fixed:
1. **Shared Global Refresh Lock** - `tokenRefreshManager.ts` ensures only ONE refresh happens at a time
2. **Unified Refresh Logic** - Both axios and fetch use the same `performTokenRefresh()` function
3. **Immediate Token Save** - New refresh token is saved immediately after receiving it
4. **Error Handling** - "Already Used" errors now clear session and force logout

### How It Works:
1. First 401 error triggers `performTokenRefresh()`
2. Sets `isRefreshing = true` and creates `refreshPromise`
3. Any concurrent 401 errors wait for the same `refreshPromise`
4. After refresh completes, all waiting requests get the same new token
5. No concurrent refresh attempts = no "Already Used" errors
