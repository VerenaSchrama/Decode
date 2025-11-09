# Testing Intervention Completion Flow - Complete Guide

## 🎯 Test Methods

### Method 1: API Endpoint Test (Recommended for Production)

#### Step 1: Get an Active Intervention Period

```bash
# Get active periods for a user
curl -X GET "https://api.decode-app.nl/intervention-periods/active" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "period": {
    "id": "period-uuid",
    "intervention_name": "Control your blood sugar",
    "selected_habits": ["Habit 1", "Habit 2"],
    "status": "active"
  }
}
```

#### Step 2: Complete the Intervention

```bash
PERIOD_ID="period-uuid-from-step-1"
TOKEN="your_bearer_token"

curl -X PUT "https://api.decode-app.nl/intervention-periods/${PERIOD_ID}/complete" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "notes": "Test completion"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Intervention period completed",
  "period_id": "period-uuid",
  "event_results": [
    {
      "handler": "complete_related_habits",
      "success": true,
      "result": {
        "updated_habits_count": 2,
        "total_habits": 2
      }
    },
    {
      "handler": "generate_completion_summary",
      "success": true,
      "result": {
        "adherence_rate": 75.5,
        "average_mood": 3.8,
        "mood_trend": "improved"
      }
    },
    {
      "handler": "send_completion_notification",
      "success": true,
      "result": {
        "notification": {
          "type": "intervention_completed",
          "title": "Intervention Completed 🎉"
        }
      }
    }
  ]
}
```

#### Step 3: Verify Database Changes

**Check Intervention Period:**
```sql
SELECT status, actual_end_date, notes 
FROM intervention_periods 
WHERE id = 'period-uuid';
-- Expected: status='completed', actual_end_date IS NOT NULL
```

**Check User Habits:**
```sql
SELECT habit_name, status 
FROM user_habits 
WHERE user_id = 'user-uuid' 
  AND status = 'completed';
-- Expected: All selected_habits have status='completed'
```

**Check Completion Summary:**
```sql
SELECT adherence_rate, average_mood, mood_trend 
FROM completion_summaries 
WHERE intervention_period_id = 'period-uuid';
-- Expected: Row with calculated metrics
```

**Check Notification:**
```sql
SELECT type, title, read 
FROM notifications 
WHERE user_id = 'user-uuid' 
  AND type = 'intervention_completed' 
ORDER BY created_at DESC 
LIMIT 1;
-- Expected: Notification record
```

#### Step 4: Test Double Completion Prevention

```bash
# Try to complete again (should fail)
curl -X PUT "https://api.decode-app.nl/intervention-periods/${PERIOD_ID}/complete" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Second attempt"}'
```

**Expected Response:**
```json
{
  "detail": "Intervention period already completed"
}
```
**Status Code:** `400 Bad Request`

---

### Method 2: Python Test Script (Local Development)

**Prerequisites:**
```bash
cd backend
source venv/bin/activate  # Activate virtual environment
```

**Run Test:**
```bash
python3 test_intervention_completion_flow.py
```

The script will:
1. ✅ Find or create a test intervention period
2. ✅ Complete it via InterventionService
3. ✅ Verify all 3 event listeners executed
4. ✅ Check database updates
5. ✅ Test double completion prevention

---

### Method 3: Manual Testing via App

1. **Start an Intervention** (if needed)
   - Complete intake
   - Select intervention
   - Start intervention period

2. **Complete the Intervention**
   - Navigate to intervention details
   - Click "Complete Intervention"
   - Add optional notes

3. **Verify Results**
   - Check that habits are no longer active
   - Check for completion summary (if analytics screen exists)
   - Check for notification (if notifications screen exists)

---

## ✅ Test Checklist

### Core Functionality
- [ ] **Period Status**: `intervention_periods.status = 'completed'`
- [ ] **End Date**: `actual_end_date` is set to current timestamp
- [ ] **Notes**: Optional notes are saved

### Event Listeners
- [ ] **Habit Service**: `user_habits.status = 'completed'` for all selected habits
- [ ] **Analytics Service**: `completion_summaries` row created with metrics
- [ ] **Notification Service**: `notifications` row created

### Edge Cases
- [ ] **Double Completion**: Returns 400 if already completed
- [ ] **Missing Data**: Handles missing `planned_end_date` gracefully
- [ ] **No Mood Data**: Analytics still generates (mood fields may be null)
- [ ] **No Habits**: Habit listener handles gracefully

### Event Results
- [ ] **All Listeners Fire**: `event_results` contains 3 entries
- [ ] **Success Status**: All listeners report `success: true`
- [ ] **Error Isolation**: One listener failure doesn't block others

---

## 🔍 Verification Queries

### Complete Verification Query

```sql
-- Get complete completion status
WITH period_info AS (
    SELECT 
        ip.id,
        ip.user_id,
        ip.intervention_name,
        ip.status,
        ip.actual_end_date,
        ip.selected_habits,
        cs.adherence_rate,
        cs.average_mood,
        cs.mood_trend,
        n.title as notification_title
    FROM intervention_periods ip
    LEFT JOIN completion_summaries cs ON cs.intervention_period_id = ip.id
    LEFT JOIN notifications n ON n.user_id = ip.user_id 
        AND n.type = 'intervention_completed'
        AND n.created_at >= ip.actual_end_date
    WHERE ip.id = 'YOUR_PERIOD_ID'
)
SELECT 
    pi.*,
    COUNT(uh.id) as completed_habits_count,
    STRING_AGG(uh.habit_name, ', ') as completed_habits
FROM period_info pi
LEFT JOIN user_habits uh ON uh.user_id = pi.user_id 
    AND uh.habit_name = ANY(pi.selected_habits)
    AND uh.status = 'completed'
GROUP BY pi.id, pi.user_id, pi.intervention_name, pi.status, 
         pi.actual_end_date, pi.selected_habits, 
         pi.adherence_rate, pi.average_mood, pi.mood_trend, 
         pi.notification_title;
```

---

## 🐛 Common Issues

### Issue: "No event_results in response"

**Cause**: Event listeners not registered
**Fix**: Check server logs for "✅ Event listeners registered"
**Solution**: Ensure `import services` in `startup_event()`

### Issue: "Habits not updated"

**Cause**: Habit names don't match
**Fix**: Check `selected_habits` array matches `user_habits.habit_name` exactly
**Solution**: Verify habit names are consistent

### Issue: "Analytics not generated"

**Cause**: `completion_summaries` table doesn't exist
**Fix**: Run migration SQL
**Note**: Analytics still calculates (graceful degradation)

### Issue: "Double completion not prevented"

**Cause**: Status check not working
**Fix**: Verify period status check in `complete_period()`

---

## 📊 Expected Results Summary

| Component | Before | After |
|-----------|--------|-------|
| `intervention_periods.status` | `"active"` | `"completed"` ✅ |
| `intervention_periods.actual_end_date` | `NULL` | `TIMESTAMP` ✅ |
| `user_habits.status` | `"active"` | `"completed"` ✅ |
| `completion_summaries` | No row | Row with metrics ✅ |
| `notifications` | No row | Row with notification ✅ |
| Event listeners | N/A | 3 executed ✅ |

---

## 🚀 Quick Test Command

```bash
# One-liner test (replace variables)
PERIOD_ID="your-period-id" TOKEN="your-token" && \
curl -X PUT "https://api.decode-app.nl/intervention-periods/${PERIOD_ID}/complete" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notes":"Test"}' | jq '.event_results[] | {handler, success}'
```

**Expected Output:**
```json
{
  "handler": "complete_related_habits",
  "success": true
}
{
  "handler": "generate_completion_summary",
  "success": true
}
{
  "handler": "send_completion_notification",
  "success": true
}
```

