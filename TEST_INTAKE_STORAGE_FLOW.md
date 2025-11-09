# Test Intake & Intervention Storage Flow

## Backend Deployed ✅
The backend has been deployed with comprehensive logging. All API calls will now be logged.

## Testing Steps

### 1. Open Browser Console
- Open your app in the browser
- Open Developer Tools (F12)
- Go to the Console tab
- Clear the console

### 2. Complete the Full Flow

#### Step 1: Complete Intake
1. Navigate to the Story Intake screen
2. Fill out all steps:
   - Symptoms
   - Last Period
   - Cycle Length (if applicable)
   - Interventions
   - Dietary Preferences
   - Consent
3. Click "Complete Intake"
4. **Watch for logs:**
   - `🔍 DEBUG: Sending intake data:`
   - `✅ Intake completed with intake_id:`

#### Step 2: View Recommendations
1. You should be redirected to Recommendations screen
2. Wait for recommendations to load
3. **Watch for logs:**
   - API call to `/recommend`
   - Recommendations received

#### Step 3: Select Intervention
1. Click on an intervention card to select it
2. Click "Start with this intervention" button
3. **Watch for logs:**
   - Period selection modal should appear

#### Step 4: Select Period
1. In the period selection modal:
   - Select a duration (e.g., 30 days)
   - Select a start date
   - Click "Start My Journey"
2. **Watch for logs:**
   - `🎯 RecommendationsScreen: handlePeriodSelected called with:`
   - `✅ RecommendationsScreen: Calling onInterventionSelected callback`
   - `🎯 AppNavigator: handleInterventionSelected called`
   - `📋 Intervention selected:`
   - `📅 Period data:`
   - `📤 Starting intervention period with request:`
   - `🌐 InterventionPeriodService: Making API call to /intervention-periods/start`
   - `📤 Request payload:`
   - `✅ InterventionPeriodService: API response status: 200`
   - `✅ Intervention period tracking started:`

### 3. Check Backend Logs

SSH into the server and check backend logs:

```bash
ssh root@65.108.149.135
journalctl -u mybackend -f --no-pager
```

**Watch for:**
- `🚀 POST /intervention-periods/start - REQUEST RECEIVED`
- `📥 Request body:`
- `📋 Extracted data:`
- `✅ Starting intervention for authenticated user:`
- `🔄 Calling intervention_period_service.start_intervention_period...`
- `✅ Intervention period started successfully:`

### 4. Verify in Supabase

After completing the flow, check Supabase:

1. **Check `intakes` table:**
   ```sql
   SELECT id, user_id, created_at 
   FROM intakes 
   WHERE user_id = 'YOUR_USER_ID' 
   ORDER BY created_at DESC 
   LIMIT 1;
   ```

2. **Check `intervention_periods` table:**
   ```sql
   SELECT id, user_id, intake_id, intervention_name, selected_habits, status, start_date, end_date
   FROM intervention_periods 
   WHERE user_id = 'YOUR_USER_ID' 
   ORDER BY created_at DESC 
   LIMIT 1;
   ```

3. **Check `user_habits` table:**
   ```sql
   SELECT id, user_id, habit_name, status, created_at
   FROM user_habits 
   WHERE user_id = 'YOUR_USER_ID' 
   ORDER BY created_at DESC;
   ```

## Expected Results

### ✅ Success Indicators:
- All frontend logs appear in sequence
- Backend receives the request
- `intervention_periods` record is created
- `user_habits` records are created (one per selected habit)
- Status is `active`

### ❌ Failure Indicators:
- Missing frontend logs (flow breaks before API call)
- Backend doesn't receive request (frontend issue)
- Backend receives request but fails (check error logs)
- Records not created in Supabase (check backend error logs)

## Common Issues

### Issue 1: No Frontend Logs
**Symptom:** No logs appear after clicking "Start My Journey"
**Cause:** Period selection modal callback not working
**Fix:** Check `InterventionPeriodScreen` component

### Issue 2: Frontend Logs but No Backend Request
**Symptom:** Frontend logs show API call attempt but backend doesn't receive it
**Cause:** Network error, CORS issue, or API URL incorrect
**Fix:** Check Network tab in browser DevTools

### Issue 3: Backend Receives Request but Fails
**Symptom:** Backend logs show request but error occurs
**Cause:** Missing data, validation error, or database error
**Fix:** Check backend error logs for details

### Issue 4: Backend Succeeds but No Records in Supabase
**Symptom:** Backend logs show success but no records created
**Cause:** Database transaction issue or RLS policy blocking
**Fix:** Check Supabase logs and RLS policies

## Next Steps After Testing

1. **If flow works:** Remove debug logging or keep minimal logging
2. **If flow breaks:** Share the console logs and backend logs for analysis
3. **If records not created:** Check Supabase RLS policies and database constraints

## Quick Test Command

To quickly check if backend is receiving requests:

```bash
ssh root@65.108.149.135 "journalctl -u mybackend -n 50 --no-pager | grep 'intervention-periods/start'"
```

This will show the last 50 log lines containing "intervention-periods/start".

