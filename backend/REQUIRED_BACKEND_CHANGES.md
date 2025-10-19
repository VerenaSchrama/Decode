# Required Backend Code Changes for New Schema

## 🎯 **OVERVIEW**
This document outlines all the backend code changes needed to work with the new database schema. The new schema uses `profiles` table instead of `user_profiles` and has updated column names.

---

## 🚨 **CRITICAL CHANGES NEEDED**

### **1. Column Name Updates in API Endpoints**

#### **A. `/interventions` Endpoint (api.py:338-367)**
**CURRENT CODE:**
```python
interventions.append({
    "id": intervention['Intervention_ID'],
    "name": intervention['Strategy Name'],  # ❌ OLD COLUMN NAME
    "profile": intervention['Clinical Background'],  # ❌ OLD COLUMN NAME
    "scientific_source": intervention.get('Scientific Source', ''),  # ❌ OLD COLUMN NAME
    "category": intervention.get('Category Strategy', ''),  # ❌ OLD COLUMN NAME
    "symptoms_match": intervention.get('Symptoms Match', ''),  # ❌ OLD COLUMN NAME
    "persona_fit": intervention.get('Persona Fit', ''),  # ❌ OLD COLUMN NAME
    "dietary_fit": intervention.get('Dietary Fit', ''),  # ❌ OLD COLUMN NAME
    "movement_amount": intervention.get('Amount of movement', '')  # ❌ OLD COLUMN NAME
})
```

**REQUIRED CHANGES:**
```python
interventions.append({
    "id": intervention['Intervention_ID'],
    "name": intervention['strategy_name'],  # ✅ NEW COLUMN NAME
    "profile": intervention['clinical_background'],  # ✅ NEW COLUMN NAME
    "scientific_source": intervention.get('show_sources', ''),  # ✅ NEW COLUMN NAME
    "category": intervention.get('category_strategy', ''),  # ✅ NEW COLUMN NAME
    "symptoms_match": intervention.get('symptoms_match', ''),  # ✅ NEW COLUMN NAME
    "persona_fit": intervention.get('persona_fit_prior', ''),  # ✅ NEW COLUMN NAME
    "dietary_fit": intervention.get('dietary_fit_prior', ''),  # ✅ NEW COLUMN NAME
    "movement_amount": intervention.get('amount_of_movement_prior', '')  # ✅ NEW COLUMN NAME
})
```

#### **B. User Input Models (models/user_input.py:14)**
**CURRENT CODE:**
```python
result = supabase_client.client.table('InterventionsBASE').select('Strategy Name').execute()
return [intervention['Strategy Name'] for intervention in result.data]  # ❌ OLD COLUMN NAME
```

**REQUIRED CHANGES:**
```python
result = supabase_client.client.table('InterventionsBASE').select('strategy_name').execute()
return [intervention['strategy_name'] for intervention in result.data]  # ✅ NEW COLUMN NAME
```

### **2. Table Reference Updates**

#### **A. Daily Progress Endpoints (api.py:422-671)**
**CURRENT CODE:**
```python
# Uses user_uuid referencing user_profiles
db_data = {
    'user_uuid': db_user_uuid,  # ❌ OLD COLUMN NAME
    'entry_date': entry_date,
    'habits_completed': [h['habit'] for h in completed_habits],
    'mood': mood.get('mood') if mood else None,
    'notes': mood.get('notes', '') if mood else ''
}

# Query uses user_uuid
result = supabase_client.client.table('daily_habit_entries')\
    .select('entry_date, completion_percentage')\
    .eq('user_uuid', db_user_uuid)  # ❌ OLD COLUMN NAME
```

**REQUIRED CHANGES:**
```python
# Use user_id referencing profiles
db_data = {
    'user_id': db_user_uuid,  # ✅ NEW COLUMN NAME
    'entry_date': entry_date,
    'habit_id': habit_id,  # ✅ NEW: Reference to user_habits.id
    'completed': True,  # ✅ NEW: Boolean instead of array
    'mood': mood.get('mood') if mood else None,
    'notes': mood.get('notes', '') if mood else '',
    'completion_percentage': completion_percentage
}

# Query uses user_id
result = supabase_client.client.table('daily_habit_entries')\
    .select('entry_date, completion_percentage')\
    .eq('user_id', db_user_uuid)  # ✅ NEW COLUMN NAME
```

### **3. New Table Integration**

#### **A. Add Habits Endpoint**
**NEW ENDPOINT NEEDED:**
```python
@app.get("/habits/{intervention_id}")
async def get_habits_for_intervention(intervention_id: int):
    """Get habits for specific intervention"""
    try:
        from models import supabase_client
        
        result = supabase_client.client.table('HabitsBASE')\
            .select('*')\
            .eq('connects_intervention_id', intervention_id)\
            .execute()
        
        habits = []
        for habit in result.data:
            habits.append({
                "id": habit['Habit_ID'],
                "name": habit['habit_name'],
                "description": habit['what_will_you_be_doing'],
                "why_it_works": habit['why_does_it_work'],
                "in_practice": habit['what_does_that_look_like_in_practice']
            })
        
        return {"habits": habits}
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error loading habits: {str(e)}"
        )
```

#### **B. Update Intervention Period Service**
**CURRENT CODE:** Uses `intervention_periods` table (which now exists)
**REQUIRED CHANGES:** Update to use new schema structure

```python
# Update intervention_period_service.py
def start_intervention_period(self, user_id: str, intervention_id: str, ...):
    period_data = {
        'user_id': user_id,  # ✅ References profiles.user_id
        'intervention_id': intervention_id,  # ✅ References user_interventions.id
        'intake_id': intake_id,  # ✅ References intakes.id
        'start_date': start_date,
        'planned_duration_days': planned_duration_days,
        'status': 'active'
    }
    
    result = self.supabase_client.client.table('intervention_periods')\
        .insert(period_data)\
        .execute()
```

### **4. SupabaseClient Updates**

#### **A. Update SupabaseClient Methods (models/supabase_models.py)**
**REQUIRED CHANGES:**
```python
def get_interventions(self):
    """Get all interventions from InterventionsBASE"""
    return self.client.table('InterventionsBASE').select('*').execute()

def get_habits_for_intervention(self, intervention_id: int):
    """Get habits for specific intervention"""
    return self.client.table('HabitsBASE')\
        .select('*')\
        .eq('connects_intervention_id', intervention_id)\
        .execute()

def get_daily_habit_entries(self, user_id: str, start_date: str, end_date: str):
    """Get daily habit entries for user"""
    return self.client.table('daily_habit_entries')\
        .select('*')\
        .eq('user_id', user_id)\
        .gte('entry_date', start_date)\
        .lte('entry_date', end_date)\
        .execute()

def get_user_intervention_periods(self, user_id: str):
    """Get user's intervention periods"""
    return self.client.table('intervention_periods')\
        .select('*')\
        .eq('user_id', user_id)\
        .execute()
```

---

## 📋 **IMPLEMENTATION PRIORITY**

### **HIGH PRIORITY (BREAKS FUNCTIONALITY)**
1. ✅ **Fix column names** in `/interventions` endpoint
2. ✅ **Update daily progress** to use `user_id` instead of `user_uuid`
3. ✅ **Update user input models** to use new column names
4. ✅ **Fix foreign key references** to use `profiles` table

### **MEDIUM PRIORITY (ENHANCES FUNCTIONALITY)**
1. ✅ **Add habits endpoint** for database-driven habit selection
2. ✅ **Update intervention period service** for new schema
3. ✅ **Add new SupabaseClient methods** for new tables

### **LOW PRIORITY (NICE TO HAVE)**
1. ✅ **Add feedback endpoints** for user feedback collection
2. ✅ **Add chat endpoints** for nutritionist chat
3. ✅ **Add analytics endpoints** for user insights

---

## 🔧 **STEP-BY-STEP IMPLEMENTATION**

### **Step 1: Fix Column Names**
1. Update `/interventions` endpoint in `api.py`
2. Update `models/user_input.py` column references
3. Test interventions endpoint

### **Step 2: Fix Daily Progress**
1. Update `save_daily_progress` endpoint
2. Update `get_daily_progress` endpoint  
3. Update `get_habit_streak` endpoint
4. Test daily progress functionality

### **Step 3: Add New Endpoints**
1. Add `/habits/{intervention_id}` endpoint
2. Update intervention period service
3. Add new SupabaseClient methods
4. Test new functionality

### **Step 4: Update Frontend Integration**
1. Update frontend to use new column names
2. Update frontend to use new endpoints
3. Test complete user journey

---

## 🚨 **CRITICAL NOTES**

1. **Backward Compatibility**: Some changes will break existing frontend code
2. **Data Migration**: Ensure all existing data is migrated to new schema
3. **Testing**: Test all endpoints after each change
4. **Rollback Plan**: Keep backup of working code before changes

The new schema is much better structured, but requires significant backend updates to work properly.
