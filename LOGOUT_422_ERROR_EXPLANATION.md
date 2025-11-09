# Logout 422 Error Explanation

## Error Details

**Error**: `POST https://api.decode-app.nl/auth/logout` → `422 (Unprocessable Entity)`

**Root Cause**: Parameter mismatch between frontend request and backend endpoint expectation.

---

## The Problem

### Backend Expectation (`backend/api.py` line 2930)
```python
@app.post("/auth/logout")
async def logout_user(access_token: str):
    """
    Args:
        access_token: User's access token
    """
    return await auth_service.logout_user(access_token)
```

**FastAPI interprets this as**:
- `access_token` should come from **query parameter** or **request body**
- FastAPI looks for: `?access_token=...` or in JSON body

### Frontend Implementation (`mobile/src/services/authService.ts` line 76-82)
```typescript
const response = await fetch(`${this.baseUrl}/auth/logout`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,  // ⚠️ Token in header, not body/query
  },
  // ⚠️ No body sent
});
```

**Frontend sends**:
- Token in `Authorization` header (Bearer token)
- **No request body**
- **No query parameters**

### The Mismatch

```
Backend expects:  access_token parameter (query or body)
Frontend sends:   Authorization header only
Result:          422 Unprocessable Entity (missing required parameter)
```

---

## Why 422 Unprocessable Entity?

FastAPI returns `422` when:
- A required parameter is missing
- The request body doesn't match the expected schema
- Query parameters don't match the function signature

In this case: FastAPI can't find `access_token` because:
- It's not in the query string (`?access_token=...`)
- It's not in the request body (no body sent)
- FastAPI doesn't automatically read from `Authorization` header for simple parameters

---

## Why Logout Still "Succeeds" Locally

Looking at the logs:
```
AuthService: Logout request failed: 422
AuthContext: authService.logout completed
AuthContext: Clearing stored auth and dispatching logout
Logout completed successfully ✅
```

**Why this happens**:
1. Frontend catches the error but doesn't throw it (line 92 in `authService.ts`):
   ```typescript
   } catch (error) {
     console.error('🔴 AuthService: Logout error:', error);
     // Don't throw error for logout - user should be logged out locally anyway
   }
   ```

2. `AuthContext` continues with local logout regardless of API response:
   - Clears stored auth data
   - Dispatches logout action
   - Shows "Logout completed successfully"

**Result**: User is logged out locally, but server-side session invalidation fails.

---

## The Fix

The logout endpoint should read the token from the `Authorization` header (consistent with other endpoints):

### Option 1: Read from Authorization Header (Recommended)

**Backend** (`backend/api.py`):
```python
@app.post("/auth/logout")
async def logout_user(authorization: str = Header(None)):
    """
    Logout user and invalidate session
    
    Args:
        authorization: Authorization header with Bearer token
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authentication required")
    
    access_token = authorization.split(" ")[1]
    return await auth_service.logout_user(access_token)
```

### Option 2: Accept Token in Request Body

**Backend**:
```python
class LogoutRequest(BaseModel):
    access_token: str

@app.post("/auth/logout")
async def logout_user(request: LogoutRequest):
    return await auth_service.logout_user(request.access_token)
```

**Frontend**:
```typescript
const response = await fetch(`${this.baseUrl}/auth/logout`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ access_token: accessToken }),  // Add body
});
```

---

## Current Impact

### What Works
- ✅ User is logged out locally (frontend clears session)
- ✅ User can't access protected routes (local state cleared)
- ✅ UI shows logout success

### What Doesn't Work
- ❌ Server-side session not invalidated
- ❌ Token might still be valid on server (security concern)
- ❌ If user has token cached, they might still be able to use it

### Security Implications
- **Low-Medium Risk**: Token remains valid on server until it expires naturally
- **Mitigation**: Tokens have expiration times, but proper logout is better

---

## Recommended Fix

**Use Option 1** (Authorization header) because:
1. Consistent with other endpoints (`/daily-progress`, `/chat/message`, etc.)
2. No frontend changes needed
3. Follows REST API best practices
4. More secure (token in header, not body)

---

## Summary

| Aspect | Current State | Issue |
|--------|--------------|-------|
| **Backend expects** | `access_token` parameter | Query/body parameter |
| **Frontend sends** | `Authorization` header | Header only |
| **Result** | 422 Unprocessable Entity | Parameter mismatch |
| **Local logout** | ✅ Works | Frontend continues anyway |
| **Server logout** | ❌ Fails | Session not invalidated |
| **User experience** | ✅ Appears successful | But server-side fails silently |

**Fix**: Update backend to read token from `Authorization` header (like other endpoints).

