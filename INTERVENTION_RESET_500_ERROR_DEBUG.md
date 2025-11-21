# Intervention Reset 500 Error - Debug Guide

## Error
```
POST https://api.decode-app.nl/intervention-periods/reset 500 (Internal Server Error)
```

## What I've Done

### 1. Added Enhanced Logging
- Added detailed logging in `reset_intervention_period` endpoint
- Added logging in `start_intervention_period` method
- Added error traceback printing

### 2. Improved Error Handling
- Better error messages for HabitsBASE table queries
- More detailed error information in exception handlers
- Added logging for database insert operations

## Next Steps

**Please try the "Change Intervention" action again**, and then we can check the logs to see the exact error:

```bash
ssh root@65.108.149.135
journalctl -u mybackend --since '1 minute ago' --no-pager | grep -A 30 -i 'reset\|error\|exception'
```

## Potential Issues to Check

1. **HabitsBASE table access**
   - Column names might be different
   - Table might not exist or be accessible
   - RLS (Row Level Security) might be blocking access

2. **Database constraints**
   - Missing required fields in `intervention_periods` table
   - Foreign key constraints failing
   - Data type mismatches

3. **Date format issues**
   - Start date parsing might fail
   - End date calculation might be incorrect

4. **Supabase client issues**
   - Authentication/authorization problems
   - Service role key issues

## How to Debug

After you try again, run:
```bash
ssh root@65.108.149.135 "journalctl -u mybackend --since '2 minutes ago' --no-pager | tail -100"
```

This will show the detailed error message and stack trace.

