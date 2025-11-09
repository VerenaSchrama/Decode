#!/bin/bash
# Test script for intervention completion API endpoint
# Requires: jq (for JSON parsing), curl

API_URL="${API_URL:-http://localhost:8000}"
# Or use production: API_URL="https://api.decode-app.nl"

echo "🧪 Testing Intervention Completion API"
echo "======================================"
echo ""

# Get test credentials (you'll need to provide these)
read -p "Enter access token (Bearer token): " ACCESS_TOKEN
read -p "Enter intervention period ID to complete: " PERIOD_ID

if [ -z "$ACCESS_TOKEN" ] || [ -z "$PERIOD_ID" ]; then
    echo "❌ Access token and period ID are required"
    exit 1
fi

echo ""
echo "📋 Test 1: Complete intervention period"
echo "----------------------------------------"

RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
    "${API_URL}/intervention-periods/${PERIOD_ID}/complete" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "notes": "Test completion via API"
    }')

HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | sed '$d')

echo "HTTP Status: $HTTP_CODE"
echo "Response:"
echo "$BODY" | jq '.' 2>/dev/null || echo "$BODY"

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ Completion successful"
    
    # Check event results
    if command -v jq &> /dev/null; then
        EVENT_COUNT=$(echo "$BODY" | jq '.event_results | length' 2>/dev/null)
        echo ""
        echo "📡 Event Results: $EVENT_COUNT listeners executed"
        
        echo "$BODY" | jq '.event_results[] | "\(.handler): \(if .success then "✅" else "❌" end)"' 2>/dev/null
    fi
else
    echo "❌ Completion failed"
    exit 1
fi

echo ""
echo "📋 Test 2: Attempt double completion (should fail)"
echo "--------------------------------------------------"

DOUBLE_RESPONSE=$(curl -s -w "\n%{http_code}" -X PUT \
    "${API_URL}/intervention-periods/${PERIOD_ID}/complete" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "notes": "Second attempt"
    }')

DOUBLE_HTTP_CODE=$(echo "$DOUBLE_RESPONSE" | tail -n1)
DOUBLE_BODY=$(echo "$DOUBLE_RESPONSE" | sed '$d')

echo "HTTP Status: $DOUBLE_HTTP_CODE"
if [ "$DOUBLE_HTTP_CODE" -eq 400 ]; then
    echo "✅ Double completion prevented (expected 400)"
else
    echo "⚠️ Unexpected status: $DOUBLE_HTTP_CODE"
fi

echo ""
echo "✅ API Tests Complete"

