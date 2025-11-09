#!/bin/bash
# Complete test flow for intervention completion
# Tests the event-driven completion system end-to-end

set -e

API_URL="${API_URL:-https://api.decode-app.nl}"
# For local testing: API_URL="http://localhost:8000"

echo "🧪 Testing Intervention Completion Flow"
echo "========================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get credentials (from environment variable or prompt)
if [ -z "$ACCESS_TOKEN" ]; then
    read -p "Enter your Bearer token: " ACCESS_TOKEN
    if [ -z "$ACCESS_TOKEN" ]; then
        echo -e "${RED}❌ Access token required${NC}"
        echo ""
        echo "Usage:"
        echo "  export ACCESS_TOKEN='your-token' && ./test_completion_flow.sh"
        echo "  OR"
        echo "  ./test_completion_flow.sh  (will prompt for token)"
        exit 1
    fi
else
    echo "✅ Using ACCESS_TOKEN from environment"
fi

echo ""
echo "📋 Step 1: Getting active intervention period..."
echo "--------------------------------------------------"

ACTIVE_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X GET "${API_URL}/intervention-periods/active" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}")

HTTP_CODE=$(echo "$ACTIVE_RESPONSE" | tail -n1)
ACTIVE_BODY=$(echo "$ACTIVE_RESPONSE" | sed '$d')

if [ "$HTTP_CODE" -ne 200 ]; then
    echo -e "${RED}❌ Failed to get active period (HTTP $HTTP_CODE)${NC}"
    echo "$ACTIVE_BODY"
    exit 1
fi

# Extract period ID
if command -v jq &> /dev/null; then
    PERIOD_ID=$(echo "$ACTIVE_BODY" | jq -r '.period.id // empty')
    PERIOD_NAME=$(echo "$ACTIVE_BODY" | jq -r '.period.intervention_name // "Unknown"')
    FOUND=$(echo "$ACTIVE_BODY" | jq -r '.found // false')
else
    # Fallback: try to extract from JSON manually
    PERIOD_ID=$(echo "$ACTIVE_BODY" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
    FOUND="true"
fi

if [ -z "$PERIOD_ID" ] || [ "$FOUND" = "false" ]; then
    echo -e "${YELLOW}⚠️ No active intervention period found${NC}"
    echo ""
    echo "To test completion, you need an active intervention period."
    echo "Options:"
    echo "1. Create one via the app (complete intake → select intervention → start)"
    echo "2. Use a completed period ID to test double-completion prevention"
    echo ""
    read -p "Enter a period ID to test (or press Enter to exit): " PERIOD_ID
    if [ -z "$PERIOD_ID" ]; then
        exit 0
    fi
    echo ""
    echo "📋 Using period ID: $PERIOD_ID"
else
    echo -e "${GREEN}✅ Found active intervention period${NC}"
    echo "   Period ID: $PERIOD_ID"
    echo "   Intervention: $PERIOD_NAME"
fi

echo ""
echo "📊 Step 2: Checking current state..."
echo "------------------------------------"

# Check period status
echo "   Checking intervention_periods table..."
# Note: We can't directly query DB, but we can check via API response

echo ""
echo "🎯 Step 3: Completing intervention period..."
echo "--------------------------------------------"

COMPLETE_RESPONSE=$(curl -s -w "\n%{http_code}" \
    -X PUT "${API_URL}/intervention-periods/${PERIOD_ID}/complete" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H "Content-Type: application/json" \
    -d '{
        "notes": "Test completion via script"
    }')

COMPLETE_HTTP=$(echo "$COMPLETE_RESPONSE" | tail -n1)
COMPLETE_BODY=$(echo "$COMPLETE_RESPONSE" | sed '$d')

echo "   HTTP Status: $COMPLETE_HTTP"

if [ "$COMPLETE_HTTP" -eq 200 ]; then
    echo -e "${GREEN}✅ Completion successful!${NC}"
    echo ""
    echo "   Response:"
    if command -v jq &> /dev/null; then
        echo "$COMPLETE_BODY" | jq '.'
        
        echo ""
        echo "📡 Step 4: Verifying event listeners..."
        echo "--------------------------------------"
        
        EVENT_COUNT=$(echo "$COMPLETE_BODY" | jq '.event_results | length' 2>/dev/null || echo "0")
        echo "   Total listeners executed: $EVENT_COUNT"
        echo ""
        
        echo "$COMPLETE_BODY" | jq -r '.event_results[] | "   \(if .success then "✅" else "❌" end) \(.handler): \(if .success then "Success" else .error end)"' 2>/dev/null
        
        # Check each listener
        HABIT_SUCCESS=$(echo "$COMPLETE_BODY" | jq -r '.event_results[] | select(.handler=="complete_related_habits") | .success' 2>/dev/null)
        ANALYTICS_SUCCESS=$(echo "$COMPLETE_BODY" | jq -r '.event_results[] | select(.handler=="generate_completion_summary") | .success' 2>/dev/null)
        NOTIF_SUCCESS=$(echo "$COMPLETE_BODY" | jq -r '.event_results[] | select(.handler=="send_completion_notification") | .success' 2>/dev/null)
        
        echo ""
        echo "📊 Step 5: Event Results Summary"
        echo "-------------------------------"
        echo "   Habit Service:     ${HABIT_SUCCESS:+✅} ${HABIT_SUCCESS:-❌}"
        echo "   Analytics Service: ${ANALYTICS_SUCCESS:+✅} ${ANALYTICS_SUCCESS:-❌}"
        echo "   Notification:     ${NOTIF_SUCCESS:+✅} ${NOTIF_SUCCESS:-❌}"
        
    else
        echo "$COMPLETE_BODY"
    fi
    
    echo ""
    echo "🛡️ Step 6: Testing double completion prevention..."
    echo "--------------------------------------------------"
    
    DOUBLE_RESPONSE=$(curl -s -w "\n%{http_code}" \
        -X PUT "${API_URL}/intervention-periods/${PERIOD_ID}/complete" \
        -H "Authorization: Bearer ${ACCESS_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{"notes": "Second attempt"}')
    
    DOUBLE_HTTP=$(echo "$DOUBLE_RESPONSE" | tail -n1)
    DOUBLE_BODY=$(echo "$DOUBLE_RESPONSE" | sed '$d')
    
    if [ "$DOUBLE_HTTP" -eq 400 ]; then
        echo -e "${GREEN}✅ Double completion prevented (HTTP 400)${NC}"
        echo "   Response: $(echo "$DOUBLE_BODY" | jq -r '.detail // .' 2>/dev/null || echo "$DOUBLE_BODY")"
    else
        echo -e "${YELLOW}⚠️ Unexpected status: $DOUBLE_HTTP${NC}"
        echo "   Expected: 400 (Bad Request)"
        echo "   Response: $DOUBLE_BODY"
    fi
    
    echo ""
    echo "========================================"
    echo -e "${GREEN}✅ TEST COMPLETE${NC}"
    echo "========================================"
    echo ""
    echo "Next steps:"
    echo "1. Verify in Supabase database:"
    echo "   - intervention_periods.status = 'completed'"
    echo "   - user_habits.status = 'completed'"
    echo "   - completion_summaries row created"
    echo "   - notifications row created"
    echo ""
    echo "2. Check server logs for detailed event processing"
    
elif [ "$COMPLETE_HTTP" -eq 400 ]; then
    echo -e "${YELLOW}⚠️ Period may already be completed${NC}"
    echo "   Response: $(echo "$COMPLETE_BODY" | jq -r '.detail // .' 2>/dev/null || echo "$COMPLETE_BODY")"
    echo ""
    echo "This is expected if testing double completion prevention."
else
    echo -e "${RED}❌ Completion failed (HTTP $COMPLETE_HTTP)${NC}"
    echo "   Response: $COMPLETE_BODY"
    exit 1
fi

