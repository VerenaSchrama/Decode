# Mood Trend Calculation Explained

## Overview

The mood trend calculation compares the average mood in the **first half** of the intervention period versus the **second half** to determine if mood improved, declined, or remained stable.

---

## Calculation Method

### Step 1: Collect Mood Values

```python
# Get all mood entries for the intervention period
moods = [
    {'entry_date': '2025-01-01', 'mood': 3},
    {'entry_date': '2025-01-02', 'mood': 4},
    {'entry_date': '2025-01-03', 'mood': 3},
    # ... more entries
]

# Extract mood values (1-5 scale)
mood_values = [3, 4, 3, 4, 5, 4, 5, 5, 4, 5]  # Example
```

**Source**: `daily_moods` table, filtered by:
- `user_id` = intervention user
- `entry_date` between `start_date` and `end_date` of intervention period

---

### Step 2: Split into First and Second Half

```python
# Requires at least 4 mood entries to calculate trend
if len(mood_values) >= 4:
    mid_point = len(mood_values) // 2  # Integer division
    
    # First half: mood entries from start to midpoint
    first_half = mood_values[:mid_point]
    # Example: [3, 4, 3, 4, 5]  (first 5 entries)
    
    # Second half: mood entries from midpoint to end
    second_half = mood_values[mid_point:]
    # Example: [4, 5, 5, 4, 5]  (last 5 entries)
```

**Note**: If there are fewer than 4 mood entries, trend defaults to `"stable"`.

---

### Step 3: Calculate Averages

```python
# Average mood in first half
first_half_avg = sum(first_half) / len(first_half)
# Example: (3 + 4 + 3 + 4 + 5) / 5 = 3.8

# Average mood in second half
second_half_avg = sum(second_half) / len(second_half)
# Example: (4 + 5 + 5 + 4 + 5) / 5 = 4.6
```

---

### Step 4: Compare with Threshold

```python
# Threshold: 0.3 points difference
THRESHOLD = 0.3

if second_half_avg > first_half_avg + THRESHOLD:
    mood_trend = "improved"      # Second half is significantly better
elif second_half_avg < first_half_avg - THRESHOLD:
    mood_trend = "declined"      # Second half is significantly worse
else:
    mood_trend = "stable"        # Change is within threshold
```

---

## Examples

### Example 1: Improved Mood

**Mood Values**: `[2, 2, 3, 3, 4, 4, 4, 5]` (8 entries)

**Calculation**:
- `mid_point = 8 // 2 = 4`
- `first_half = [2, 2, 3, 3]` → `avg = 2.5`
- `second_half = [4, 4, 4, 5]` → `avg = 4.25`
- `difference = 4.25 - 2.5 = 1.75`
- `1.75 > 0.3` → **"improved"** ✅

---

### Example 2: Declined Mood

**Mood Values**: `[5, 5, 4, 4, 3, 3, 2, 2]` (8 entries)

**Calculation**:
- `mid_point = 8 // 2 = 4`
- `first_half = [5, 5, 4, 4]` → `avg = 4.5`
- `second_half = [3, 3, 2, 2]` → `avg = 2.5`
- `difference = 2.5 - 4.5 = -2.0`
- `-2.0 < -0.3` → **"declined"** ⬇️

---

### Example 3: Stable Mood

**Mood Values**: `[3, 4, 3, 4, 3, 4, 3, 4]` (8 entries)

**Calculation**:
- `mid_point = 8 // 2 = 4`
- `first_half = [3, 4, 3, 4]` → `avg = 3.5`
- `second_half = [3, 4, 3, 4]` → `avg = 3.5`
- `difference = 3.5 - 3.5 = 0.0`
- `0.0` is within `[-0.3, +0.3]` → **"stable"** ➡️

---

### Example 4: Insufficient Data

**Mood Values**: `[3, 4, 3]` (3 entries)

**Calculation**:
- `len(mood_values) = 3 < 4`
- **Default**: **"stable"** (not enough data to determine trend)

---

## Threshold Explanation

### Why 0.3?

The threshold of **0.3** represents a **meaningful change** on a 1-5 mood scale:

- **0.3 points** ≈ **6% of the scale** (0.3 / 5 = 0.06)
- Small enough to detect real improvements
- Large enough to filter out noise/fluctuation

### Threshold Examples

| First Half Avg | Second Half Avg | Difference | Trend |
|----------------|-----------------|------------|-------|
| 3.0 | 3.2 | +0.2 | **stable** (within threshold) |
| 3.0 | 3.4 | +0.4 | **improved** (exceeds threshold) |
| 3.0 | 2.8 | -0.2 | **stable** (within threshold) |
| 3.0 | 2.6 | -0.4 | **declined** (exceeds threshold) |

---

## Code Location

**File**: `backend/services/analytics_service.py`  
**Function**: `generate_completion_summary()`  
**Lines**: 103-115

```python
# Calculate mood trend (compare first half vs second half)
mood_trend = "stable"
if len(mood_values) >= 4:
    mid_point = len(mood_values) // 2
    first_half_avg = sum(mood_values[:mid_point]) / mid_point
    second_half_avg = sum(mood_values[mid_point:]) / len(mood_values[mid_point:])
    
    if second_half_avg > first_half_avg + 0.3:
        mood_trend = "improved"
    elif second_half_avg < first_half_avg - 0.3:
        mood_trend = "declined"
    else:
        mood_trend = "stable"
```

---

## Edge Cases

### 1. Odd Number of Entries

**Example**: 9 mood entries
- `mid_point = 9 // 2 = 4` (integer division)
- `first_half = [0:4]` = 4 entries
- `second_half = [4:9]` = 5 entries

**Result**: Second half has one more entry (acceptable asymmetry)

---

### 2. Missing Mood Entries

**Example**: Period has 30 days, but only 10 mood entries
- Uses only the 10 available mood entries
- Splits those 10 into first 5 and last 5
- **Does not** interpolate or fill missing days

---

### 3. No Mood Data

**Example**: Period has no mood entries
- `mood_values = []`
- `len(mood_values) = 0 < 4`
- **Result**: `mood_trend = "stable"` (default)

---

## Limitations & Considerations

### 1. **Time-Based Split, Not Chronological**

The split is based on **entry order**, not actual dates. If mood entries are not evenly distributed across the period, the comparison may not reflect true temporal trends.

**Example Problem**:
- Days 1-10: 2 mood entries (both mood=2)
- Days 11-30: 8 mood entries (all mood=5)
- First half: `[2, 2]` → avg = 2.0
- Second half: `[5, 5, 5, 5, 5, 5, 5, 5]` → avg = 5.0
- **Result**: "improved" (but this reflects data density, not time)

**Potential Fix**: Sort by `entry_date` before splitting (already done via `.order('entry_date', desc=False)`)

---

### 2. **Threshold Sensitivity**

The 0.3 threshold may be:
- **Too sensitive**: Small fluctuations trigger "improved"/"declined"
- **Too insensitive**: Real improvements missed

**Consideration**: Could be made configurable or adaptive based on period length.

---

### 3. **Minimum Data Requirement**

Requires **4+ mood entries** to calculate trend. Shorter periods or infrequent mood tracking will default to "stable".

---

## Potential Improvements

### 1. **Weighted by Time**

Instead of simple split, weight by actual days:

```python
# Weight by number of days in each half
first_half_days = (mid_date - start_date).days
second_half_days = (end_date - mid_date).days
```

### 2. **Linear Regression**

Use linear regression to detect trend direction:

```python
from scipy import stats
slope, intercept, r_value, p_value, std_err = stats.linregress(days, mood_values)
if slope > 0.1:
    trend = "improved"
elif slope < -0.1:
    trend = "declined"
else:
    trend = "stable"
```

### 3. **Adaptive Threshold**

Adjust threshold based on period length:

```python
# Longer periods: smaller threshold (more sensitive)
# Shorter periods: larger threshold (less sensitive)
threshold = 0.3 if total_days >= 30 else 0.5
```

---

## Summary

**Mood Trend Calculation**:
1. ✅ Collects all mood entries for the period
2. ✅ Splits into first half and second half
3. ✅ Calculates average mood for each half
4. ✅ Compares with 0.3 threshold
5. ✅ Returns: `"improved"` | `"declined"` | `"stable"`

**Requirements**:
- Minimum 4 mood entries
- Mood values on 1-5 scale
- Entries ordered chronologically

**Threshold**: **0.3 points** difference required for "improved" or "declined"

