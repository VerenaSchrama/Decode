# Testing Intervention Completion Flow

## Quick Test Guide

### Option 1: Python Test Script (Recommended)

```bash
cd backend
python3 test_intervention_completion_flow.py
```

This script will:
1. Find or create a test intervention period
2. Complete it via the service
3. Verify all event listeners executed
4. Check database updates (period, habits, analytics, notifications)
5. Test double completion prevention

---

### Option 2: API Test (via curl)

```bash
# Set variables
API_URL="https://api.decode-app.nl"  # or http://localhost:8000
ACCESS_TOKEN="your_bearer_token"
PERIOD_ID="intervention_period_id"

# Complete intervention
curl -X PUT "${API_URL}/intervention-periods/${PERIOD_ID}/complete" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Test completion"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Intervention period completed",
  "period_id": "...",
  "event_results": [
    {"handler": "complete_related_habits", "success": true},
    {"handler": "generate_completion_summary", "success": true},
    {"handler": "send_completion_notification", "success": true}
  ]
}
```

---

### Option 3: Manual Database Verification

After completing an intervention, verify in Supabase:

#### 1. Check Intervention Period
```sql
SELECT 
    id, 
    status, 
    actual_end_date, 
    notes 
FROM intervention_periods 
WHERE id = '{period_id}';
```
**Expected**: `status = 'completed'`, `actual_end_date` set

#### 2. Check User Habits
```sql
SELECT 
    habit_name, 
    status 
FROM user_habits 
WHERE user_id = '{user_id}' 
  AND habit_name IN (SELECT unnest(selected_habits) FROM intervention_periods WHERE id = '{period_id}');
```
**Expected**: All habits have `status = 'completed'`

#### 3. Check Completion Summary
```sql
SELECT 
    adherence_rate, 
    average_mood, 
    mood_trend 
FROM completion_summaries 
WHERE intervention_period_id = '{period_id}';
```
**Expected**: Row with calculated metrics

#### 4. Check Notification
```sql
SELECT 
    type, 
    title, 
    read 
FROM notifications 
WHERE user_id = '{user_id}' 
  AND type = 'intervention_completed' 
ORDER BY created_at DESC 
LIMIT 1;
```
**Expected**: Notification record created

---

## Test Checklist

- [ ] **Period Status Updated**: `intervention_periods.status = 'completed'`
- [ ] **End Date Set**: `actual_end_date` is not null
- [ ] **Habits Updated**: All related `user_habits.status = 'completed'`
- [ ] **Analytics Generated**: `completion_summaries` row created
- [ ] **Notification Created**: `notifications` row created
- [ ] **Double Completion Prevented**: Second attempt returns 400
- [ ] **Event Listeners Executed**: All 3 listeners in `event_results`

---

## Troubleshooting

### No Event Results
**Check**: Server logs for "✅ Event listeners registered"
**Fix**: Ensure `import services` happens in startup

### Habits Not Updated
**Check**: `selected_habits` array in `intervention_periods` table
**Fix**: Ensure habit names match exactly

### Analytics Not Generated
**Check**: `completion_summaries` table exists
**Fix**: Run migration SQL
**Note**: Analytics calculates even if table missing (graceful degradation)

### Notification Not Created
**Check**: `notifications` table exists
**Fix**: Run migration SQL
**Note**: Notification service degrades gracefully if table missing

