# Intervention Completion Refactoring - Implementation Guide

## 🎯 Quick Start

### 1. Run Database Migrations

Execute these SQL scripts in your Supabase SQL editor:

```sql
-- Create completion_summaries table
\i backend/migrations/create_completion_summaries_table.sql

-- Create notifications table (optional but recommended)
\i backend/migrations/create_notifications_table.sql
```

Or copy-paste the SQL from:
- `backend/migrations/create_completion_summaries_table.sql`
- `backend/migrations/create_notifications_table.sql`

### 2. Deploy Backend

```bash
cd /Users/verena_werk/Documents/SW_projects/hfc_app_v2
bash deploy.sh
```

### 3. Verify

Check server logs for:
- ✅ `Event listeners registered for intervention completion`
- ✅ `Scheduled daily intervention auto-completion at 00:05`

---

## 📋 Architecture

### Event Flow

```
PUT /intervention-periods/{period_id}/complete
    ↓
InterventionService.complete_period()
    ├─ Check if already completed (prevent double)
    ├─ Update intervention_periods.status = 'completed'
    └─ Publish event: "intervention.completed"
        ├─→ HabitService.complete_related_habits()
        │   └─ Update user_habits.status = 'completed'
        ├─→ AnalyticsService.generate_completion_summary()
        │   └─ Calculate metrics → Store in completion_summaries
        └─→ NotificationService.send_completion_notification()
            └─ Create notification record
```

### Auto-Completion Flow

```
Daily Scheduler (00:05 UTC)
    ↓
auto_complete_expired_periods()
    ├─ Find periods: status='active' AND end_date <= today
    └─ For each expired period:
        └─ InterventionService.complete_period(auto_completed=True)
            └─ Same event flow as manual completion
```

---

## 🔧 Configuration

### Event Listeners

Listeners are auto-registered in `backend/services/__init__.py`:

```python
event_bus.subscribe("intervention.completed", complete_related_habits)
event_bus.subscribe("intervention.completed", generate_completion_summary)
event_bus.subscribe("intervention.completed", send_completion_notification)
```

### Scheduler

Runs in background thread, checks every minute:

```python
# backend/api.py startup_event()
schedule.every().day.at("00:05").do(auto_complete_all)
```

---

## 📊 Database Schema

### completion_summaries

```sql
CREATE TABLE completion_summaries (
    id UUID PRIMARY KEY,
    intervention_period_id UUID REFERENCES intervention_periods(id),
    user_id UUID REFERENCES profiles(user_id),
    adherence_rate DECIMAL(5,2),  -- 0-100%
    average_mood DECIMAL(3,2),    -- 1-5
    mood_trend TEXT,              -- 'improved'|'declined'|'stable'
    summary_json JSONB,           -- Additional insights
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

### notifications

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES profiles(user_id),
    type TEXT,                    -- 'intervention_completed', etc.
    title TEXT,
    body TEXT,
    data JSONB,                  -- Additional payload
    read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ
);
```

---

## 🧪 Testing

### Manual Test

```bash
# Complete an intervention period
curl -X PUT https://api.decode-app.nl/intervention-periods/{period_id}/complete \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Test completion"}'
```

### Expected Response

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

### Verify Database

```sql
-- Check intervention period
SELECT status, actual_end_date FROM intervention_periods WHERE id = '{period_id}';
-- Should show: status = 'completed'

-- Check user habits
SELECT status FROM user_habits WHERE user_id = '{user_id}' AND habit_name IN (...);
-- Should show: status = 'completed'

-- Check completion summary
SELECT * FROM completion_summaries WHERE intervention_period_id = '{period_id}';
-- Should show analytics data

-- Check notifications
SELECT * FROM notifications WHERE user_id = '{user_id}' AND type = 'intervention_completed';
-- Should show notification record
```

---

## 🐛 Troubleshooting

### Event Listeners Not Firing

**Check**: Server logs for "✅ Event listeners registered"
**Fix**: Ensure `import services` happens in `startup_event()`

### Analytics Not Generated

**Check**: `completion_summaries` table exists
**Fix**: Run migration SQL
**Note**: Analytics still calculates even if table missing (graceful degradation)

### Habits Not Updated

**Check**: `selected_habits` array in `intervention_periods` table
**Fix**: Ensure habit names match exactly

### Auto-Completion Not Running

**Check**: Server logs for "✅ Scheduled daily intervention auto-completion"
**Fix**: Verify scheduler thread is running

---

## 📈 Monitoring

### Key Metrics to Track

1. **Completion Rate**: % of periods completed vs started
2. **Auto-Completion Rate**: % auto-completed vs manual
3. **Event Processing**: Success rate of event listeners
4. **Analytics Generation**: % of completions with summaries
5. **Notification Delivery**: % of notifications created

### Log Messages

- `✅ Completed intervention period: {period_id}`
- `✅ Updated {count} habits to completed status`
- `✅ Generated completion summary for period {period_id}`
- `✅ Stored notification for user {user_id}`
- `✅ Auto-completion task completed: {count} periods completed`

---

## 🔮 Future Enhancements

1. **True Atomic Transactions**: PostgreSQL stored procedures
2. **Event Persistence**: Store events in database for audit
3. **Retry Logic**: Retry failed event handlers
4. **Distributed Events**: Redis/RabbitMQ for multi-instance
5. **Push Notifications**: FCM/APNS integration
6. **Email Notifications**: Send completion emails
7. **Advanced Analytics**: ML-based insights

---

## ✅ Checklist

- [x] Event bus implemented
- [x] InterventionService refactored
- [x] Habit completion listener
- [x] Analytics generation listener
- [x] Notification listener
- [x] Auto-completion scheduler
- [x] Edge case handling
- [x] API endpoint updated
- [x] Database migrations created
- [x] Tests created
- [x] Documentation complete

---

## 📚 File Reference

- **Event Bus**: `backend/services/event_bus.py`
- **Main Service**: `backend/services/intervention_service.py`
- **Habit Listener**: `backend/services/habit_service.py`
- **Analytics Listener**: `backend/services/analytics_service.py`
- **Notification Listener**: `backend/services/notification_service.py`
- **Scheduler**: `backend/services/intervention_scheduler.py`
- **API Endpoint**: `backend/api.py` (line 2377)
- **Tests**: `backend/tests/test_intervention_completion.py`
- **Migrations**: `backend/migrations/`

