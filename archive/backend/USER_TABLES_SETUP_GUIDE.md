# User Tables Setup Guide

## 🎯 **Objective**
Create user-specific database tables (`user_habits` and `user_interventions`) linked to the existing `users` table to support the following API endpoints:
- `GET /user/{user_id}/insights`
- `GET /user/{user_id}/habits`
- `POST /interventions/submit`

## 📊 **Current Database Status**

### ✅ **Existing Tables**
- `users` - User accounts (id, email, hashed_password, created_at, current_strategy)
- `InterventionsBASE` - Base interventions (9 interventions)
- `HabitsBASE` - Base habits linked to interventions
- `chat_messages` - Chat history (already exists)

### ❌ **Missing Tables**
- `user_habits` - User's personal habit tracking
- `user_interventions` - User-generated interventions
- `intervention_habits` - Habits for user-generated interventions
- `daily_habit_entries` - Daily progress tracking
- `intervention_feedback` - User feedback on interventions

## 🔧 **Setup Instructions**

### **Step 1: Create Tables in Supabase**

1. **Open Supabase Dashboard**
   - Go to your Supabase project dashboard
   - Navigate to **SQL Editor** (left sidebar)

2. **Run SQL Script**
   - Copy the contents of `setup_user_tables.sql`
   - Paste into the SQL Editor
   - Click **"Run"** to execute

3. **Verify Tables Created**
   - Go to **Table Editor** (left sidebar)
   - Check that these tables exist:
     - `user_habits`
     - `user_interventions`
     - `intervention_habits`
     - `daily_habit_entries`
     - `intervention_feedback`

### **Step 2: Test the Setup**

Run the verification script:
```bash
cd /Users/verena_werk/Documents/SW_projects/hfc_app_v2/backend
source venv/bin/activate
python test_user_endpoints.py
```

## 📋 **Table Schemas**

### **user_habits**
```sql
- id (UUID, Primary Key)
- user_id (INTEGER, Foreign Key → users.id)
- habit_name (VARCHAR)
- habit_description (TEXT)
- intervention_id (INTEGER, Foreign Key → InterventionsBASE.Intervention_ID)
- status (VARCHAR: 'active', 'completed', 'paused', 'cancelled')
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- completed_at (TIMESTAMP)
- notes (TEXT)
```

### **user_interventions**
```sql
- id (UUID, Primary Key)
- user_id (INTEGER, Foreign Key → users.id)
- name (VARCHAR)
- description (TEXT)
- profile_match (TEXT)
- scientific_source (TEXT)
- status (VARCHAR: 'pending', 'approved', 'rejected')
- helpful_count (INTEGER)
- total_tries (INTEGER)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- reviewed_by (VARCHAR)
- review_notes (TEXT)
```

### **intervention_habits**
```sql
- id (UUID, Primary Key)
- intervention_id (UUID, Foreign Key → user_interventions.id)
- number (INTEGER)
- description (TEXT)
- created_at (TIMESTAMP)
```

### **daily_habit_entries**
```sql
- id (UUID, Primary Key)
- user_id (INTEGER, Foreign Key → users.id)
- entry_date (DATE)
- habits_completed (TEXT[])
- mood (VARCHAR)
- notes (TEXT)
- completion_percentage (DECIMAL)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

### **intervention_feedback**
```sql
- id (UUID, Primary Key)
- intervention_id (UUID, Foreign Key → user_interventions.id)
- user_id (INTEGER, Foreign Key → users.id)
- rating (INTEGER, 1-5)
- helpful (BOOLEAN)
- comments (TEXT)
- created_at (TIMESTAMP)
```

## 🔒 **Security Features**

- **Row Level Security (RLS)** enabled on all tables
- **Users can only access their own data** (based on user_id)
- **Approved interventions are publicly viewable** (for browsing)
- **Foreign key constraints** ensure data integrity

## 🚀 **Expected Results After Setup**

### **Working Endpoints**
- ✅ `GET /health` - Server status
- ✅ `GET /interventions` - List all interventions
- ✅ `POST /recommend` - Get personalized recommendations
- ✅ `POST /chat/message` - AI chat functionality
- ✅ `POST /daily-progress` - Track daily habits
- ✅ `GET /user/{user_id}/insights` - User insights
- ✅ `GET /user/{user_id}/habits` - User's habits
- ✅ `POST /interventions/submit` - Submit custom interventions

### **API Response Examples**

**GET /user/{user_id}/insights**
```json
{
  "user_id": "123",
  "total_habits": 5,
  "active_habits": 3,
  "completed_habits": 2,
  "current_interventions": ["Ketogenic diet", "Eat with your cycle"],
  "progress_summary": "You're doing great! 60% completion rate this week."
}
```

**POST /interventions/submit**
```json
{
  "id": "uuid-here",
  "user_id": "123",
  "name": "Custom PCOS Diet",
  "description": "Personalized diet plan for PCOS management",
  "status": "pending",
  "created_at": "2024-01-01T00:00:00Z"
}
```

## 🐛 **Troubleshooting**

### **Common Issues**

1. **"Could not find the table" errors**
   - Solution: Run the SQL script in Supabase SQL Editor

2. **RLS policy errors**
   - Solution: Check that RLS policies were created correctly

3. **Foreign key constraint errors**
   - Solution: Ensure the `users` table exists and has data

4. **Permission denied errors**
   - Solution: Check that the API key has proper permissions

### **Verification Commands**

```bash
# Check if tables exist
python create_tables_simple.py

# Test all endpoints
python test_user_endpoints.py

# Check server logs
tail -f /var/log/your-app.log
```

## 📈 **Next Steps**

After successful setup:

1. **Test with real user data**
2. **Implement user authentication** (if not already done)
3. **Add more sophisticated RLS policies** (if needed)
4. **Monitor performance** and add indexes as needed
5. **Implement data backup strategies**

## 📞 **Support**

If you encounter issues:
1. Check the Supabase logs in the dashboard
2. Verify table schemas match the SQL script
3. Test individual endpoints with the test script
4. Check API server logs for detailed error messages

