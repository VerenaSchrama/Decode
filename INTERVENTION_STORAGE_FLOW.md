# Intervention Storage Flow

## Summary
**Interventions are NOT automatically stored after intake.** They are only stored when the user explicitly starts an intervention period.

## Complete Flow

### 1. Intake Completion
**Location:** `mobile/src/screens/StoryIntakeScreen.tsx`
- User completes intake form
- Calls `/recommend` endpoint
- **Stored:** `intakes` table with `intake_id`
- **Stored:** Recommendations in `intakes.recommendation_data` (JSONB)

### 2. View Recommendations
**Location:** `mobile/src/screens/RecommendationsScreen.tsx`
- User views recommended interventions
- Recommendations are displayed from `intakes.recommendation_data`
- **No intervention period created yet**

### 3. Select Intervention
**Location:** `mobile/src/screens/InterventionPeriodScreen.tsx`
- User selects an intervention from recommendations
- User selects duration (7, 14, 30, 60, or 90 days)
- User selects start date
- User clicks "Start My Journey"
- This triggers `onPeriodSelected` callback

### 4. Start Intervention Period ⭐ **THIS IS WHERE IT GETS STORED**
**Location:** `mobile/src/navigation/AppNavigator.tsx` → `handleInterventionSelected()`

**Flow:**
1. Validates `intake_id` exists
2. Extracts habits from selected intervention
3. Calls `interventionPeriodService.startInterventionPeriod()`
4. Makes POST request to `/intervention-periods/start`

**Backend:** `backend/api.py` → `/intervention-periods/start`
- Calls `intervention_period_service.start_intervention_period()`
- **Creates entry in `intervention_periods` table** with:
  - `user_id`
  - `intake_id`
  - `intervention_name`
  - `selected_habits`
  - `start_date`
  - `end_date` (calculated from `start_date + planned_duration_days`)
  - `status: 'active'`
- **Creates entries in `user_habits` table** for each selected habit

## Why No Intervention Might Exist

### Possible Reasons:
1. **User skipped the intervention selection step**
   - User viewed recommendations but didn't select one
   - User didn't complete the "Set Your Timeline" screen
   - User didn't click "Start My Journey"

2. **API call failed silently**
   - Check browser console for errors
   - Check backend logs for `/intervention-periods/start` errors
   - Authentication token might be invalid

3. **Missing `intake_id`**
   - The code tries to fetch it from `/user/intake/latest` if missing
   - If this fails, intervention period won't be created

4. **User went directly to habits screen**
   - If user navigates directly to habits without going through intervention selection
   - No intervention period will exist

## How to Verify

### Check Database:
```sql
-- Check if user has any intervention periods
SELECT * FROM intervention_periods 
WHERE user_id = '<user_id>' 
ORDER BY created_at DESC;

-- Check if user has any intakes
SELECT id, user_id, created_at, recommendation_data 
FROM intakes 
WHERE user_id = '<user_id>' 
ORDER BY created_at DESC;
```

### Check Frontend Console:
- Look for logs starting with `📤 Starting intervention period with request:`
- Look for `✅ Intervention period tracking started:` or `❌ Failed to start intervention period tracking:`

### Check Backend Logs:
- Look for `✅ Starting intervention for authenticated user: <user_id>`
- Look for `✅ Started intervention period: <intervention_name> for user <user_id>`
- Look for any error messages

## Solution

If user has completed intake but no intervention period exists:
1. User needs to go back to recommendations screen
2. Select an intervention
3. Complete the "Set Your Timeline" screen
4. Click "Start My Journey"

Or, you could add a feature to automatically create an intervention period when user selects habits, but currently it requires the explicit "Start My Journey" action.

