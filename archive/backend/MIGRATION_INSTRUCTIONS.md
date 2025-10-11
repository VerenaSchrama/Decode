# 🚀 Data Migration Instructions: CSV → Database

## 📋 **Overview**
This migration moves your app from using a single CSV file (`Interventions_with_Habits.csv`) to separate linked database tables for interventions and habits, and rebuilds the vectorstore using database data.

## 🎯 **What This Migration Does**

### **Before (Current State):**
- Single CSV file with 8 interventions and 5 habits each
- Vectorstore built from CSV data
- Code reads directly from CSV

### **After (Target State):**
- Separate `interventions` table (8 records)
- Separate `habits` table (40 records, linked by `intervention_id`)
- Vectorstore built from database data
- All code uses database instead of CSV

## 📋 **Exact Steps to Execute**

### **Step 1: Verify Database Schema**
```bash
cd /Users/verena_werk/Documents/SW_projects/hfc_app_v2/backend
```

1. Go to your Supabase dashboard
2. Navigate to SQL Editor
3. Copy and paste the contents of `check_database_schema.sql`
4. Execute the SQL to verify your current schema

### **Step 2: Run the Complete Migration**
```bash
# Activate your virtual environment
source venv/bin/activate

# Run the complete migration
python complete_data_migration.py
```

This will:
- ✅ Migrate CSV data to separate database tables
- ✅ Build new vectorstore from database data
- ✅ Update intervention matcher to use database
- ✅ Update all code references
- ✅ Test the migration

### **Step 3: Verify the Migration**
```bash
# Test the API
python -c "
from interventions.matcher import get_intervention_recommendation
result = get_intervention_recommendation('I have PCOS and want to control my blood sugar')
print('Test result:', result)
"
```

### **Step 4: Test Your Mobile App**
1. Start your backend server: `uvicorn api:app --reload`
2. Test the mobile app's recommendation flow
3. Verify that recommendations are working

## 🔧 **Manual Steps (if needed)**

### **If Database Tables Don't Exist:**
1. Go to Supabase dashboard → SQL Editor
2. Run this SQL:

```sql
-- Create interventions table
CREATE TABLE IF NOT EXISTS interventions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    profile TEXT NOT NULL,
    scientific_source TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create habits table
CREATE TABLE IF NOT EXISTS habits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    intervention_id UUID REFERENCES interventions(id) ON DELETE CASCADE,
    scientific_source TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_habits_intervention_id ON habits(intervention_id);
CREATE INDEX IF NOT EXISTS idx_interventions_name ON interventions(name);
```

## 📊 **What Gets Migrated**

### **Interventions Table (8 records):**
- `id`: UUID primary key
- `name`: Intervention name (e.g., "Control your blood sugar")
- `profile`: Target user profile
- `scientific_source`: Research source URL

### **Habits Table (40 records):**
- `id`: UUID primary key
- `name`: Habit description
- `intervention_id`: Foreign key to interventions table
- `scientific_source`: Research source URL

### **Vectorstore:**
- New collection: `interventions_and_habits`
- Location: `data/vectorstore/database_chroma/`
- Contains both intervention and habit documents

## 🧪 **Testing the Migration**

### **Test 1: Database Data**
```python
from models.supabase_models import supabase_client

# Check interventions
interventions = supabase_client.client.table('interventions').select('*').execute()
print(f"Interventions: {len(interventions.data)}")

# Check habits
habits = supabase_client.client.table('habits').select('*').execute()
print(f"Habits: {len(habits.data)}")
```

### **Test 2: Intervention Matcher**
```python
from interventions.matcher import get_intervention_recommendation

result = get_intervention_recommendation("I have PCOS and want to control my blood sugar")
print(f"Recommended: {result.get('recommended_intervention')}")
print(f"Similarity: {result.get('similarity_score')}")
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

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **"No interventions found in database"**
   - Run the migration script again
   - Check if CSV file exists and is readable

2. **"Vectorstore build failed"**
   - Check if OpenAI API key is set
   - Verify database has data

3. **"Matcher test failed"**
   - Check if embeddings are working
   - Verify database connection

4. **"API returns old data"**
   - Restart your backend server
   - Clear any caches

### **Rollback (if needed):**
```bash
# Restore from backup
cp data/Interventions_with_Habits_backup.csv data/Interventions_with_Habits.csv

# Revert to old vectorstore
rm -rf data/vectorstore/database_chroma
mv data/vectorstore/chroma data/vectorstore/chroma_backup
```

## ✅ **Success Checklist**

- [ ] Database schema verified
- [ ] Migration script completed without errors
- [ ] 8 interventions in database
- [ ] 40 habits in database
- [ ] Vectorstore built successfully
- [ ] Intervention matcher working
- [ ] API endpoints returning data
- [ ] Mobile app working
- [ ] Old CSV backed up

## 📁 **Files Created/Modified**

### **New Files:**
- `check_database_schema.sql` - Database verification
- `migrate_csv_to_database.py` - CSV to database migration
- `build_database_vectorstore.py` - Vectorstore builder
- `update_intervention_matcher.py` - Matcher updater
- `complete_data_migration.py` - Complete migration script
- `MIGRATION_INSTRUCTIONS.md` - This file

### **Modified Files:**
- `interventions/matcher.py` - Updated to use database
- `retrievers/vectorstores.py` - Updated paths

### **Backup Files:**
- `data/Interventions_with_Habits_backup.csv` - Original CSV backup

---

**Ready to migrate? Run: `python complete_data_migration.py`** 🚀


