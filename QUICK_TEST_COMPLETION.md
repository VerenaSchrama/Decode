# Quick Test: Intervention Completion Flow

## 🚀 Fastest Way to Test

### Step 1: Get Active Period ID

```bash
# Replace YOUR_TOKEN with your actual Bearer token
curl -X GET "https://api.decode-app.nl/intervention-periods/active" \
  -H "Authorization: Bearer YOUR_TOKEN" | jq '.period.id'
```

**Copy the period ID from the response.**

---

### Step 2: Complete the Intervention

```bash
# Replace PERIOD_ID and YOUR_TOKEN
PERIOD_ID="paste-period-id-here"
TOKEN="your-bearer-token"

curl -X PUT "https://api.decode-app.nl/intervention-periods/${PERIOD_ID}/complete" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Test completion"}' | jq '.'
```

---

### Step 3: Verify Results

**Check the response for:**
- ✅ `"success": true`
- ✅ `"event_results"` array with 3 entries
- ✅ All listeners show `"success": true`

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

## ✅ What to Verify

1. **Period Status**: Check `intervention_periods` table → `status = 'completed'`
2. **Habits Updated**: Check `user_habits` table → `status = 'completed'`
3. **Analytics Generated**: Check `completion_summaries` table → row exists
4. **Notification Created**: Check `notifications` table → row exists

---

## 🐛 If Something Fails

**No event_results?**
- Check server logs: "✅ Event listeners registered"
- Restart backend if needed

**Habits not updated?**
- Verify `selected_habits` array in `intervention_periods` table
- Check habit names match exactly

**Analytics/Notifications missing?**
- Run database migrations (tables may not exist)
- Check server logs for errors

