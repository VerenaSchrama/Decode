# Quick Test Checklist

## Pre-Test Setup
- [ ] Backend deployed (✅ Done)
- [ ] Browser console open
- [ ] Backend logs accessible (SSH ready)

## Test Flow

### 1. Intake Completion
- [ ] Complete all intake steps
- [ ] See log: `✅ Intake completed with intake_id:`
- [ ] Note the `intake_id` value

### 2. Recommendations
- [ ] Recommendations screen loads
- [ ] Select an intervention
- [ ] Click "Start with this intervention"

### 3. Period Selection
- [ ] Period selection modal appears
- [ ] Select duration (30 days)
- [ ] Select start date (today)
- [ ] Click "Start My Journey"

### 4. Frontend Logs (Check Console)
- [ ] `🎯 RecommendationsScreen: handlePeriodSelected called`
- [ ] `🎯 AppNavigator: handleInterventionSelected called`
- [ ] `📤 Starting intervention period with request:`
- [ ] `🌐 InterventionPeriodService: Making API call`
- [ ] `✅ Intervention period tracking started:`

### 5. Backend Logs (Check Server)
```bash
ssh root@65.108.149.135
journalctl -u mybackend -f
```
- [ ] `🚀 POST /intervention-periods/start - REQUEST RECEIVED`
- [ ] `✅ Starting intervention for authenticated user:`
- [ ] `✅ Intervention period started successfully:`

### 6. Supabase Verification
- [ ] Check `intervention_periods` table has new record
- [ ] Check `user_habits` table has records (one per habit)
- [ ] Verify `status = 'active'`
- [ ] Verify `selected_habits` array is populated

## If Something Fails

**No frontend logs?**
→ Check if period selection modal is completing

**Frontend logs but no backend request?**
→ Check Network tab for failed requests

**Backend receives but fails?**
→ Check backend error logs for details

**Backend succeeds but no records?**
→ Check Supabase RLS policies

