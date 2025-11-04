# Chat Message Storage Fix

## Problem

Chat messages disappear when users log out and log back in. Messages are not being persisted in Supabase.

## Root Cause

1. **Silent Error Handling**: Insert operations were wrapped in `try/except` blocks that only printed warnings and continued silently
2. **No Error Visibility**: Errors were caught but not surfaced, making it impossible to debug
3. **Possible RLS Issues**: Even though service role key should bypass RLS, errors weren't being logged

## Fixes Applied

### 1. Improved Error Logging (`/chat/message` endpoint)
- Changed from silent `print(f"Warning: ...")` to detailed error logging
- Now logs error type, full error message, and the data being inserted
- **Non-streaming endpoint now raises HTTPException** to surface errors

### 2. Improved Error Logging (`/chat/stream` endpoint)
- Added detailed error logging for both user and AI message inserts
- Logs error type and full error details
- **Streaming endpoint logs errors but doesn't fail the stream** (to avoid breaking user experience)

### 3. Fixed Context Data Format
- Ensured `context_used` is always a dict (JSONB) or None, not a string
- Fixed user message context: `{"user_context": user_context}`
- Fixed AI message context: `{"inflo_context": inflo_context}`

## Code Changes

### `/chat/message` endpoint:
```python
# Before: Silent failure
try:
    result = supabase_client.client.table('chat_messages').insert([user_message, ai_message]).execute()
    print(f"Successfully stored chat messages...")
except Exception as e:
    print(f"Warning: Could not store chat messages: {e}")
    # Continue without storing

# After: Detailed error logging + raise exception
try:
    result = supabase_client.client.table('chat_messages').insert([user_message, ai_message]).execute()
    print(f"✅ Successfully stored chat messages: {len(result.data)} messages")
except Exception as e:
    print(f"❌ ERROR storing chat messages: {e}")
    print(f"   Error type: {type(e).__name__}")
    print(f"   User message: {user_message}")
    print(f"   AI message: {ai_message}")
    raise HTTPException(status_code=500, detail=f"Failed to store chat messages: {str(e)}")
```

### `/chat/stream` endpoint:
```python
# Before: Silent failure
try:
    supabase_client.client.table('chat_messages').insert(user_record).execute()
except Exception as e:
    print(f"Warning(stream): Could not store user message: {e}")

# After: Detailed error logging
try:
    result = supabase_client.client.table('chat_messages').insert(user_record).execute()
    print(f"✅ Stored user message: {user_message_id}")
except Exception as e:
    print(f"❌ ERROR storing user message: {e}")
    print(f"   Error type: {type(e).__name__}")
    print(f"   User record: {user_record}")
```

## Next Steps for Debugging

After deploying, check server logs for:
1. `✅ Stored user message:` - Success logs
2. `❌ ERROR storing user message:` - Failure logs with full details

Common issues to check:
1. **Table doesn't exist** - Error will show "relation does not exist"
2. **RLS policy blocking** - Error will show "new row violates row-level security policy"
3. **Schema mismatch** - Error will show column type mismatch
4. **Service role key not configured** - Check if `SUPABASE_SERVICE_ROLE_KEY` is set

## Expected Behavior

- Messages should now be stored in Supabase
- If storage fails, errors will be visible in server logs
- Non-streaming endpoint will return 500 error if storage fails (user will see error)
- Streaming endpoint will log errors but continue streaming (user won't see error, but we'll know it failed)

## Verification

After deployment, test:
1. Send a chat message
2. Check server logs for "✅ Stored" messages
3. Log out and log back in
4. Check if chat history loads from `/chat/history`
5. If messages are missing, check logs for "❌ ERROR" messages

