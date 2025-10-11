# 🔐 Authentication Migration Guide

## **Overview**
This guide explains how to migrate from the current demo user system to full Supabase Auth with email/password authentication.

## **🚀 Implementation Steps**

### **Step 1: Run Database Migration**
Execute the SQL script in your Supabase SQL Editor:

```sql
-- Run: setup_supabase_auth.sql
-- This will:
-- 1. Create user_profiles table
-- 2. Add UUID columns to existing tables
-- 3. Set up RLS policies
-- 4. Create auth triggers
```

### **Step 2: Install Dependencies**
```bash
cd backend
source venv/bin/activate
pip install email-validator==2.2.0
```

### **Step 3: Update Environment Variables**
Add to your `.env` file:
```env
# Supabase Auth (already configured)
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Optional: JWT secret for additional security
JWT_SECRET=your_jwt_secret_key
```

### **Step 4: Test Authentication**
```bash
# Start the server
uvicorn api:app --reload --host 0.0.0.0 --port 8000

# Test registration
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "name": "Test User",
    "age": 28,
    "anonymous": false
  }'

# Test login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'
```

## **📱 Frontend Integration**

### **Registration Flow**
1. User fills out registration form
2. Call `POST /auth/register` with user data
3. Store access token and user info
4. Redirect to main app

### **Login Flow**
1. User enters email/password
2. Call `POST /auth/login`
3. Store access token and user info
4. Redirect to main app

### **Protected Routes**
Include access token in headers:
```javascript
headers: {
  'Authorization': `Bearer ${accessToken}`,
  'Content-Type': 'application/json'
}
```

### **Logout Flow**
1. Call `POST /auth/logout` with access token
2. Clear stored tokens and user data
3. Redirect to login screen

## **🔄 Data Migration**

### **Existing Demo Users**
- Demo users (ID 21, etc.) will continue to work
- New authenticated users will get UUIDs
- Both systems can coexist during transition

### **User Data Linking**
- `daily_habit_entries.user_uuid` links to authenticated users
- `intakes.user_uuid` links to authenticated users
- `user_profiles` table stores additional user info

## **🔒 Security Features**

### **Row Level Security (RLS)**
- Users can only access their own data
- Automatic data isolation
- No cross-user data leakage

### **Token Management**
- JWT access tokens
- Refresh token support
- Automatic token validation

### **Password Security**
- Supabase handles password hashing
- Secure password requirements
- Password reset functionality

## **📊 API Endpoints**

### **Authentication**
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `POST /auth/logout` - Logout user
- `POST /auth/verify` - Verify token

### **Profile Management**
- `GET /auth/profile/{user_id}` - Get user profile
- `PUT /auth/profile/{user_id}` - Update user profile

### **Existing Endpoints (Updated)**
- All existing endpoints now support both demo users and authenticated users
- User ID can be either integer (demo) or UUID (authenticated)

## **🎯 Benefits**

### **For Users**
- ✅ Secure account creation
- ✅ Persistent data across devices
- ✅ Password reset capability
- ✅ Privacy and data control

### **For Development**
- ✅ Proper user management
- ✅ Data isolation and security
- ✅ Scalable authentication
- ✅ Easy frontend integration

## **🚨 Breaking Changes**

### **API Changes**
- User IDs are now UUIDs for authenticated users
- Some endpoints may need token validation
- Demo user system still works for testing

### **Database Changes**
- New `user_profiles` table
- UUID columns added to existing tables
- RLS policies enabled

## **🔧 Troubleshooting**

### **Common Issues**
1. **Token validation fails**: Check if user is logged in
2. **RLS blocks data access**: Ensure user is authenticated
3. **Profile not found**: User may not have completed registration

### **Debug Steps**
1. Check Supabase Auth logs
2. Verify RLS policies
3. Test with both demo and authenticated users
4. Check token expiration

## **📈 Next Steps**

1. **Frontend Integration**: Update mobile app to use auth endpoints
2. **User Onboarding**: Create registration/login screens
3. **Data Migration**: Move demo users to authenticated accounts
4. **Advanced Features**: Add OAuth, password reset, etc.

---

**Ready to implement?** Run the SQL migration and test the authentication endpoints! 🚀

