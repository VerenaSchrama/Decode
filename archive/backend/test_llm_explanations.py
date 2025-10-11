#!/usr/bin/env python3
"""
Test script for LLM-generated intervention explanations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.user_input import UserInput, Profile, Symptoms, Interventions, DietaryPreferences, LastPeriod
from llm_explanations import generate_intervention_explanation, generate_batch_explanations

def test_single_explanation():
    """Test generating a single explanation"""
    print("🧪 Testing single explanation generation...")
    
    # Create test user input
    user_input = UserInput(
        profile=Profile(
            name="Sarah",
            age=28
        ),
        symptoms=Symptoms(
            selected=["PCOS", "Irregular periods", "Weight gain"],
            additional="insulin resistance and fatigue"
        ),
        interventions=Interventions(
            selected=[],
            additional=""
        ),
        dietaryPreferences=DietaryPreferences(
            selected=["Mediterranean"],
            additional=""
        ),
        lastPeriod=LastPeriod(
            hasPeriod=True,
            date="2024-01-15",
            cycleLength=35
        ),
        consent=True,
        anonymous=False
    )
    
    # Test intervention data
    intervention = {
        'intervention_id': 1,
        'intervention_name': 'Less or no dairy',
        'intervention_profile': 'This intervention focuses on reducing dairy consumption to minimize exposure to natural hormones that can affect insulin sensitivity and hormonal balance.',
        'similarity_score': 0.85,
        'symptoms_match': 'PCOS, insulin resistance',
        'persona_fit': 'Women with hormonal imbalances',
        'dietary_fit': 'Mediterranean diet compatible'
    }
    
    try:
        explanation = generate_intervention_explanation(user_input, intervention, 0.85)
        print(f"✅ Generated explanation: {explanation}")
        return True
    except Exception as e:
        print(f"❌ Error generating explanation: {e}")
        return False

def test_batch_explanations():
    """Test generating explanations for multiple interventions"""
    print("\n🧪 Testing batch explanation generation...")
    
    # Create test user input
    user_input = UserInput(
        profile=Profile(
            name="Emma",
            age=32
        ),
        symptoms=Symptoms(
            selected=["Mood swings", "Bloating", "Food cravings"],
            additional="feeling tired and irritable"
        ),
        interventions=Interventions(
            selected=[],
            additional=""
        ),
        dietaryPreferences=DietaryPreferences(
            selected=["Vegan"],
            additional=""
        ),
        lastPeriod=LastPeriod(
            hasPeriod=True,
            date="2024-01-10",
            cycleLength=28
        ),
        consent=True,
        anonymous=False
    )
    
    # Test interventions
    interventions = [
        {
            'intervention_id': 1,
            'intervention_name': 'Less or no dairy',
            'intervention_profile': 'Reduces dairy to minimize hormone exposure',
            'similarity_score': 0.75,
            'symptoms_match': 'mood swings, bloating',
            'persona_fit': 'Women with PMS symptoms',
            'dietary_fit': 'Plant-based compatible'
        },
        {
            'intervention_id': 2,
            'intervention_name': 'Intermittent fasting',
            'intervention_profile': 'Time-restricted eating to improve insulin sensitivity',
            'similarity_score': 0.68,
            'symptoms_match': 'cravings, fatigue',
            'persona_fit': 'Women with blood sugar issues',
            'dietary_fit': 'Flexible approach'
        }
    ]
    
    try:
        explanations = generate_batch_explanations(user_input, interventions)
        print(f"✅ Generated {len(explanations)} explanations:")
        for i, explanation in enumerate(explanations):
            print(f"  {i+1}. {explanation}")
        return True
    except Exception as e:
        print(f"❌ Error generating batch explanations: {e}")
        return False

def test_api_integration():
    """Test the full API integration"""
    print("\n🧪 Testing API integration...")
    
    try:
        import requests
        
        # Test data
        test_data = {
            "profile": {
                "name": "Test User",
                "age": 30
            },
            "symptoms": {
                "selected": ["PCOS", "Weight gain"],
                "additional": "insulin resistance"
            },
            "interventions": {
                "selected": [],
                "additional": ""
            },
            "dietaryPreferences": {
                "selected": ["Mediterranean"],
                "additional": ""
            },
            "lastPeriod": {
                "hasPeriod": True,
                "date": "2024-01-15",
                "cycleLength": 30
            },
            "consent": True,
            "anonymous": False
        }
        
        # Make API request
        response = requests.post(
            "http://localhost:8000/recommend",
            json=test_data,
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ API request successful")
            
            if 'interventions' in data and data['interventions']:
                first_intervention = data['interventions'][0]
                if 'why_recommended' in first_intervention:
                    print(f"✅ Explanation found: {first_intervention['why_recommended']}")
                    return True
                else:
                    print("❌ No 'why_recommended' field found in response")
                    return False
            else:
                print("❌ No interventions found in response")
                return False
        else:
            print(f"❌ API request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API integration: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing LLM Explanations System")
    print("=" * 50)
    
    # Test individual functions
    test1 = test_single_explanation()
    test2 = test_batch_explanations()
    
    # Test API integration
    test3 = test_api_integration()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Single explanation: {'✅ PASS' if test1 else '❌ FAIL'}")
    print(f"Batch explanations: {'✅ PASS' if test2 else '❌ FAIL'}")
    print(f"API integration: {'✅ PASS' if test3 else '❌ FAIL'}")
    
    if all([test1, test2, test3]):
        print("\n🎉 All tests passed! LLM explanations are working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the errors above.")
