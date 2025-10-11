# 🎯 Intervention Matching After Migration

## 📋 **How User Intake Matching Works with New Schema**

After migration to `InterventionsBASE` and `HabitsBASE`, the matching process will be significantly enhanced with richer data and more sophisticated matching algorithms.

## 🔄 **Complete Matching Flow**

### **1. User Intake Collection**
```
User fills out story intake form →
Profile + Symptoms + Interventions + Habits + Dietary Preferences →
Structured UserInput object
```

### **2. Text Processing for Matching**
```python
def build_text_from_structured_input(user_input: UserInput) -> str:
    """Convert structured input to searchable text"""
    
    parts = []
    
    # Profile information
    if user_input.profile.name:
        parts.append(f"Name: {user_input.profile.name}")
    if user_input.profile.age:
        parts.append(f"Age: {user_input.profile.age}")
    
    # Symptoms
    if user_input.symptoms.selected:
        parts.append(f"Symptoms: {', '.join(user_input.symptoms.selected)}")
    if user_input.symptoms.additional:
        parts.append(f"Additional symptoms: {user_input.symptoms.additional}")
    
    # Previous interventions
    if user_input.interventions.selected:
        parts.append(f"Tried interventions: {', '.join(user_input.interventions.selected)}")
    if user_input.interventions.additional:
        parts.append(f"Additional interventions: {user_input.interventions.additional}")
    
    # Previous habits
    if user_input.habits.selected:
        parts.append(f"Tried habits: {', '.join(user_input.habits.selected)}")
    if user_input.habits.additional:
        parts.append(f"Additional habits: {user_input.habits.additional}")
    
    # Dietary preferences
    if user_input.dietaryPreferences.selected:
        parts.append(f"Dietary preferences: {', '.join(user_input.dietaryPreferences.selected)}")
    if user_input.dietaryPreferences.additional:
        parts.append(f"Additional dietary info: {user_input.dietaryPreferences.additional}")
    
    return " | ".join(parts)
```

### **3. Enhanced Intervention Matching**

#### **A. Rich Data Embedding Creation**
```python
def _get_or_compute_embeddings(self):
    """Create embeddings using rich InterventionsBASE data"""
    
    embeddings = []
    for intervention_data in self.interventions_data:
        intervention = intervention_data['intervention']
        
        # Create comprehensive text for matching
        profile_text = f"""
        Strategy: {intervention['Strategy Name']}
        Clinical Background: {intervention['Clinical Background']}
        Symptoms Match: {intervention['Symtpoms match']}
        Persona Fit: {intervention['Persona fit (prior)']}
        Dietary Fit: {intervention['Dietary fit (prior)']}
        Category: {intervention['Category Strategy']}
        Movement: {intervention['Amount of movemen...']}
        """
        
        embedding = self.embeddings.embed_query(profile_text)
        embeddings.append(embedding)
    
    return np.array(embeddings)
```

#### **B. Multi-Field Similarity Matching**
```python
def get_intervention_recommendation(self, user_input: str, min_similarity: float = 0.50):
    """Enhanced matching using multiple data fields"""
    
    # 1. Create user input embedding
    user_embedding = self.embeddings.embed_query(user_input)
    user_embedding = np.array(user_embedding).reshape(1, -1)
    
    # 2. Calculate similarities with all interventions
    similarities = cosine_similarity(user_embedding, self.profile_embeddings)[0]
    
    # 3. Find best match
    best_idx = np.argmax(similarities)
    best_similarity = similarities[best_idx]
    
    # 4. Get rich intervention data
    best_intervention_data = self.interventions_data[best_idx]
    best_intervention = best_intervention_data['intervention']
    best_habits = best_intervention_data['habits']
    
    # 5. Return enhanced recommendation
    return {
        "intervention_id": best_intervention['Intervention_ID'],
        "intervention_name": best_intervention['Strategy Name'],
        "clinical_background": best_intervention['Clinical Background'],
        "scientific_source": best_intervention['Show Sources'],
        "similarity_score": float(best_similarity),
        "habits": [habit['Habit Name'] for habit in best_habits],
        "category_strategy": best_intervention['Category Strategy'],
        "symptoms_match": best_intervention['Symtpoms match'],
        "persona_fit": best_intervention['Persona fit (prior)'],
        "dietary_fit": best_intervention['Dietary fit (prior)'],
        "movement_amount": best_intervention['Amount of movemen...']
    }
```

## 🧠 **Enhanced Matching Features**

### **1. Multi-Dimensional Matching**
- **Clinical Background** - Main matching field
- **Symptoms Match** - Specific symptom targeting
- **Persona Fit** - User profile compatibility
- **Dietary Fit** - Dietary preference alignment
- **Category Strategy** - Intervention type matching

### **2. Rich Habit Recommendations**
```python
def get_habits_for_intervention(intervention_id: int):
    """Get detailed habits with explanations"""
    
    habits = supabase_client.get_habits_by_intervention_base(intervention_id)
    
    return [
        {
            "name": habit['Habit Name'],
            "action": habit['What will you be doing'],
            "explanation": habit['Why does it work'],
            "implementation": habit['What does that look l...']
        }
        for habit in habits.data
    ]
```

### **3. Scientific Source Attribution**
- **Show Sources** - Displayed scientific references
- **Downloadable Sources** - Links to full papers
- **Proper Citation** - Academic-style references

## 📊 **Matching Algorithm Details**

### **Step 1: Text Preprocessing**
```
User Input: "I have PCOS, irregular periods, weight gain, tried keto before"
↓
Processed: "Symptoms: PCOS, irregular periods, weight gain | Tried interventions: keto"
```

### **Step 2: Embedding Creation**
```
Processed Text → OpenAI Embeddings → Vector Representation
```

### **Step 3: Similarity Calculation**
```
User Vector vs All Intervention Vectors → Cosine Similarity Scores
```

### **Step 4: Ranking and Filtering**
```
Sort by similarity score → Filter by minimum threshold → Return best match
```

## 🎯 **Example Matching Scenarios**

### **Scenario 1: PCOS User**
```
User Input: "I have PCOS, irregular periods, weight gain, insulin resistance"
↓
Matched Intervention: "Control your blood sugar"
- Clinical Background: "Woman with PCOS, insulin resistance..."
- Symptoms Match: "PCOS, Weight gain, Irregular cycles"
- Similarity Score: 0.85
- Habits: [5 specific blood sugar control habits]
```

### **Scenario 2: Mediterranean Diet User**
```
User Input: "I want to reduce inflammation, eat more plant-based foods"
↓
Matched Intervention: "Mediterranean Diet"
- Clinical Background: "Chronic low-grade inflammation..."
- Category Strategy: "Anti-inflammatory"
- Dietary Fit: "Plant-based variety, olive oil"
- Similarity Score: 0.78
```

## 🔍 **Advanced Matching Features**

### **1. Symptom-Specific Matching**
- Matches user symptoms to `Symtpoms match` field
- Prioritizes interventions that specifically target user's symptoms

### **2. Persona-Based Matching**
- Uses `Persona fit (prior)` to match user profile
- Considers lifestyle, preferences, and goals

### **3. Dietary Compatibility**
- Matches `Dietary fit (prior)` with user preferences
- Ensures dietary recommendations align with user's eating style

### **4. Movement Level Matching**
- Considers `Amount of movemen...` field
- Matches user's activity level and preferences

## 🧪 **Testing the Matching**

### **Test 1: Basic Matching**
```python
from interventions.matcher import get_intervention_recommendation

result = get_intervention_recommendation("I have PCOS and want to control my blood sugar")
print(f"Recommended: {result['intervention_name']}")
print(f"Similarity: {result['similarity_score']}")
print(f"Category: {result['category_strategy']}")
```

### **Test 2: Multiple Recommendations**
```python
from interventions.matcher import get_multiple_intervention_recommendations

results = get_multiple_intervention_recommendations("I have inflammation and digestive issues", max_results=3)
for intervention in results['recommendations']:
    print(f"- {intervention['intervention_name']} (score: {intervention['similarity_score']:.3f})")
```

## 🚀 **Benefits of New Matching System**

### **1. Richer Data**
- More detailed intervention descriptions
- Scientific explanations for habits
- Better source attribution

### **2. Better Accuracy**
- Multi-field matching
- Symptom-specific targeting
- Persona-based recommendations

### **3. Enhanced User Experience**
- More relevant recommendations
- Detailed habit explanations
- Scientific credibility

### **4. Scalability**
- Easy to add new interventions
- Flexible matching criteria
- Database-driven updates

## 📋 **Migration Impact on Matching**

### **Before Migration:**
- Simple CSV-based matching
- Basic profile text matching
- Limited data fields

### **After Migration:**
- Rich database-driven matching
- Multi-dimensional similarity
- Enhanced user experience
- Scientific source attribution
- Detailed habit explanations

---

**The new matching system will provide much more accurate and personalized recommendations using the rich data from your InterventionsBASE and HabitsBASE tables!** 🎯


