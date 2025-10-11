# 🧹 SAFE Cleanup: Preserve InFlo Book Vectorstore

## ✅ **YES - You will still have the Alisa Vita book vectorstore!**

The safe cleanup script **preserves** the InFlo book vectorstore while only removing the old CSV and intervention-related files.

## 📊 **What Gets DELETED (Safe to remove)**

### **CSV Files (8 KB)**
- `data/Interventions_with_Habits.csv` - **Replaced by database tables**
- `data/Interventions_with_Habits_backup.csv` - **Backup file**

### **JSON Files (276 KB)**
- `data/intervention_embeddings.json` - **Old intervention embeddings cache**

### **Old Intervention Vectorstore (60 MB)**
- `data/vectorstore/a8ecfef5-fb33-4bb2-9735-cdae1b01b063/` - **Old intervention collection**

## ✅ **What Gets PRESERVED (Your InFlo book data)**

### **InFlo Book Vectorstore (80 MB)**
- `data/vectorstore/chroma/` - **Your InFlo book vectorstore** ✅
- `data/vectorstore/chroma/74e63d79-1275-4585-9bef-4ff7ef971c7b/` - **InFlo book collection** ✅
- `data/vectorstore/chroma.sqlite3` - **InFlo book database** ✅

### **InFlo Book Source Files**
- `data/raw_book/InFloBook.pdf` - **Original PDF** ✅
- `data/raw_book/InFloBook.txt` - **Extracted text** ✅
- `data/processed/chunks_AlisaVita.json` - **PDF chunks** ✅
- `data/inflo_phase_data.py` - **Phase data** ✅

### **New Database Vectorstore**
- `data/vectorstore/database_chroma/` - **New intervention vectorstore** ✅

## 🔍 **How the Two Vectorstores Work Together**

### **1. InFlo Book Vectorstore** (Preserved)
- **Purpose**: Provides scientific context from the InFlo book
- **Location**: `data/vectorstore/chroma/`
- **Collection**: `74e63d79-1275-4585-9bef-4ff7ef971c7b`
- **Used by**: `get_inflo_context()` function
- **Content**: Scientific literature chunks from InFlo book

### **2. Database Vectorstore** (New)
- **Purpose**: Provides intervention and habit recommendations
- **Location**: `data/vectorstore/database_chroma/`
- **Collection**: `interventions_and_habits`
- **Used by**: Intervention matcher
- **Content**: Database interventions and habits

## 🚀 **How to Execute Safe Cleanup**

### **Step 1: Run the Migration First**
```bash
cd /Users/verena_werk/Documents/SW_projects/hfc_app_v2/backend
source venv/bin/activate
python complete_data_migration.py
```

### **Step 2: Run the Safe Cleanup**
```bash
python cleanup_old_files_safe.py
```

## 🧪 **What the Safe Cleanup Does**

1. **✅ Verifies** InFlo book vectorstore is intact
2. **✅ Verifies** database migration is complete
3. **💾 Creates backup** of files before deletion
4. **🗑️ Deletes** only CSV and old intervention files
5. **🔍 Tests** InFlo book vectorstore after cleanup
6. **📊 Reports** space saved

## 🛡️ **Safety Features**

- **InFlo Preservation**: Never touches InFlo book vectorstore files
- **Verification**: Tests InFlo vectorstore after cleanup
- **Backup**: Creates backup before any deletion
- **Rollback**: Can restore from backup if needed

## 📋 **After Cleanup, You'll Have**

### **Two Working Vectorstores:**
1. **InFlo Book Vectorstore** - Scientific context from the book
2. **Database Vectorstore** - Intervention and habit recommendations

### **Complete Data Sources:**
- **Supabase Database** - Interventions and habits
- **InFlo Book PDF** - Original source material
- **Phase Data** - Cycle-specific information

## 🧪 **Testing After Cleanup**

### **Test InFlo Book Context:**
```python
from retrievers.vectorstores import get_inflo_context
context = get_inflo_context("menstrual cycle phases")
print(context)  # Should return InFlo book context
```

### **Test Intervention Recommendations:**
```python
from interventions.matcher import get_intervention_recommendation
result = get_intervention_recommendation("I have PCOS")
print(result)  # Should return intervention recommendation
```

### **Test API with Both Contexts:**
```bash
curl -X POST "http://localhost:8000/recommend" \
  -H "Content-Type: application/json" \
  -d '{"profile": {"name": "Test", "age": 30}, "symptoms": {"selected": ["PCOS"], "additional": ""}, "interventions": {"selected": [], "additional": ""}, "habits": {"selected": [], "additional": ""}, "dietaryPreferences": {"selected": [], "additional": ""}, "consent": true, "anonymous": true}'
```

## 🎯 **Benefits of Safe Cleanup**

- **💾 Space Saved**: ~68 MB (only intervention files)
- **📚 InFlo Preserved**: Scientific context still available
- **🗄️ Database Ready**: Clean database structure
- **🔧 Maintainable**: Clear separation of concerns
- **🚀 Performance**: Faster intervention matching

## ⚠️ **What If Something Goes Wrong?**

### **Rollback from Backup:**
```bash
# Restore from backup
cp data/cleanup_backup/Interventions_with_Habits.csv data/
cp data/cleanup_backup/intervention_embeddings.json data/
cp -r data/cleanup_backup/a8ecfef5-fb33-4bb2-9735-cdae1b01b063 data/vectorstore/
```

### **Rebuild InFlo Vectorstore (if needed):**
```bash
python build_science_vectorstore.py
```

---

## ✅ **Answer: YES, you will still have the Alisa Vita book vectorstore!**

The safe cleanup script specifically preserves all InFlo book data while only removing the old CSV and intervention files that have been migrated to the database.

**Ready to clean up safely? Run: `python cleanup_old_files_safe.py`** 🧹


