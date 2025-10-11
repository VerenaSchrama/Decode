# 🚀 New Schema Migration Instructions

## 📋 **Overview**
This migration updates your app to use the new `InterventionsBASE` and `HabitsBASE` tables instead of the old CSV-based system.

## 🎯 **What This Migration Does**

### **Before (Current State):**
- Old `interventions` and `habits` tables
- CSV-based data structure
- Simple intervention matching

### **After (Target State):**
- New `InterventionsBASE` table with rich intervention data
- New `HabitsBASE` table with detailed habit information
- Enhanced matching with more data fields
- Better recommendation system

## 📊 **New Database Schema**

### **InterventionsBASE Table:**
- `Intervention_ID` (Primary Key)
- `Strategy Name` - Name of the intervention
- `Clinical Background` - Detailed description
- `What will you be doi...` - Action description
- `Show Sources` - Scientific sources
- `Downloadable Sources` - Downloadable references
- `Category Strategy` - Strategy category
- `Symtpoms match` - Matching symptoms
- `Persona fit (prior)` - Persona fit description
- `Dietary fit (prior)` - Dietary fit description
- `Amount of movemen...` - Movement requirements

### **HabitsBASE Table:**
- `Habit_ID` (Primary Key)
- `Connects Interventio...` (Foreign Key to InterventionsBASE)
- `Habit Name` - Name of the habit
- `What will you be doing` - Action description
- `Why does it work` - Scientific explanation
- `What does that look l...` - Practical implementation

## 🚀 **How to Execute the Migration**

### **Step 1: Run the Complete Migration**
```bash
cd /Users/verena_werk/Documents/SW_projects/hfc_app_v2/backend
source venv/bin/activate
python complete_new_schema_migration.py
```

This will:
- ✅ Migrate data from old tables to new schema
- ✅ Update Supabase models
- ✅ Update intervention matcher
- ✅ Update API endpoints
- ✅ Test the complete system

### **Step 2: Verify the Migration**
```bash
# Test the API
python -c "
from interventions.matcher import get_intervention_recommendation
result = get_intervention_recommendation('I have PCOS and want to control my blood sugar')
print('Test result:', result)
"
```

### **Step 3: Test Your Mobile App**
1. Start your backend server: `uvicorn api:app --reload`
2. Test the mobile app's recommendation flow
3. Verify that recommendations show the new rich data

## 🔧 **Manual Steps (if needed)**

### **If Tables Don't Exist:**
1. Go to Supabase dashboard → SQL Editor
2. Run this SQL:

```sql
-- Create InterventionsBASE table
CREATE TABLE IF NOT EXISTS "InterventionsBASE" (
    "Intervention_ID" int8 NOT NULL PRIMARY KEY,
    "Strategy Name" text,
    "Clinical Background" text,
    "What will you be doi..." text,
    "Show Sources" text,
    "Downloadable Sources" text,
    "Category Strategy" text,
    "Symtpoms match" text,
    "Persona fit (prior)" text,
    "Dietary fit (prior)" text,
    "Amount of movemen..." text
);

-- Create HabitsBASE table
CREATE TABLE IF NOT EXISTS "HabitsBASE" (
    "Habit_ID" int8 NOT NULL PRIMARY KEY,
    "Connects Interventio..." int8,
    "Habit Name" text,
    "What will you be doing" text,
    "Why does it work" text,
    "What does that look l..." text,
    FOREIGN KEY ("Connects Interventio...") REFERENCES "InterventionsBASE"("Intervention_ID")
);
```

## 📊 **What Gets Migrated**

### **InterventionsBASE (8 records):**
- Rich intervention data with clinical background
- Scientific sources and references
- Category and symptom matching
- Persona and dietary fit information
- Movement requirements

### **HabitsBASE (40 records):**
- Detailed habit descriptions
- Scientific explanations
- Practical implementation guides
- Linked to specific interventions

## 🧪 **Testing the Migration**

### **Test 1: Database Data**
```python
from models.supabase_models import supabase_client

# Check InterventionsBASE
interventions = supabase_client.get_interventions_base()
print(f"InterventionsBASE: {len(interventions.data)}")

# Check HabitsBASE
habits = supabase_client.get_habits_base()
print(f"HabitsBASE: {len(habits.data)}")
```

### **Test 2: Intervention Matcher**
```python
from interventions.matcher import get_intervention_recommendation

result = get_intervention_recommendation("I have PCOS and want to control my blood sugar")
print(f"Recommended: {result.get('intervention_name')}")
print(f"Category: {result.get('category_strategy')}")
print(f"Symptoms: {result.get('symptoms_match')}")
print(f"Habits: {len(result.get('habits', []))}")
```

### **Test 3: API Endpoint**
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "profile": {"name": "Test User", "age": 30},
    "symptoms": {"selected": ["PCOS"], "additional": ""},
    "interventions": {"selected": [], "additional": ""},
    "habits": {"selected": [], "additional": ""},
    "dietaryPreferences": {"selected": [], "additional": ""},
    "consent": true,
    "anonymous": true
  }'
```

## 🎯 **Benefits of New Schema**

- **📊 Richer Data**: More detailed intervention and habit information
- **🔍 Better Matching**: Enhanced matching with multiple data fields
- **📚 Scientific Sources**: Proper source attribution and references
- **👤 Persona Fit**: Better understanding of who each intervention is for
- **🍽️ Dietary Fit**: Clear dietary compatibility information
- **🏃 Movement Info**: Exercise and movement requirements
- **🔗 Better Linking**: Proper foreign key relationships

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **"No interventions found in new schema"**
   - Run the migration script again
   - Check if tables exist in Supabase

2. **"Failed to load interventions from new schema"**
   - Check database connection
   - Verify table names are correct

3. **"Matcher test failed"**
   - Check if embeddings are working
   - Verify database has data

4. **"API returns old data"**
   - Restart your backend server
   - Clear any caches

### **Rollback (if needed):**
```bash
# The old tables should still exist
# You can switch back by updating the matcher to use old tables
```

## ✅ **Success Checklist**

- [ ] New tables created in Supabase
- [ ] Data migrated successfully
- [ ] Supabase models updated
- [ ] Intervention matcher updated
- [ ] API endpoints updated
- [ ] Migration test passed
- [ ] API endpoints returning new data
- [ ] Mobile app working with new data
- [ ] Rich intervention data displayed

## 📁 **Files Created/Modified**

### **New Files:**
- `migrate_to_new_schema.py` - Data migration script
- `update_supabase_models.py` - Supabase models updater
- `update_matcher_new_schema.py` - Matcher updater
- `complete_new_schema_migration.py` - Complete migration script
- `NEW_SCHEMA_MIGRATION_INSTRUCTIONS.md` - This file

### **Modified Files:**
- `models/supabase_models.py` - Updated for new schema
- `interventions/matcher.py` - Updated for new schema
- `api.py` - Updated endpoints

---

**Ready to migrate? Run: `python complete_new_schema_migration.py`** 🚀

## 🎉 **After Migration**

Your app will now:
- ✅ Use rich intervention data from InterventionsBASE
- ✅ Display detailed habit information from HabitsBASE
- ✅ Show scientific sources and references
- ✅ Provide better persona and dietary fit information
- ✅ Include movement requirements
- ✅ Maintain all existing functionality while adding new features


