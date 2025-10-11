"""
Based on scientific literature (InFlo Book Phase-Specific Data)
Comprehensive data structure for cycle-synced recommendations based on InFlo book content
"""

INFLO_PHASE_DATA = {
    "follicular": {
        "phase_info": {
            "name": "Follicular Phase",
            "description": "Your body is preparing for ovulation. Energy levels are rising - great time for new habits!",
            "duration": "7-10 days",
            "energy_level": "rising",
            "hormonal_focus": "estrogen rising, liver detoxification"
        },
        "foods": {
            "grains": ["barley", "oats", "rye", "wheat"],
            "vegetables": ["artichoke", "broccoli", "carrot", "green peas", "parsley", "string beans", "zucchini"],
            "fruits": ["avocado", "grapefruit", "lemon", "lime", "orange", "plum", "pomegranate"],
            "legumes": ["black-eyed pea", "great northern bean", "green lentil", "lima bean", "navy bean"],
            "nuts": ["brazil nuts", "cashews", "flaxseeds", "lychee", "sunflower seeds", "walnut"]
        },
        "cooking_methods": ["steaming", "sautéing"],
        "habits": {
            "blood_sugar": [
                "Choose barley or oats instead of refined grains for stable blood sugar",
                "Include artichoke and broccoli for liver detoxification support",
                "Use light cooking methods (steaming) to preserve nutrients",
                "Add flaxseeds to meals for fiber and hormone balance",
                "Focus on gentle movement to avoid overstressing your system"
            ],
            "mediterranean": [
                "Include artichoke and broccoli in your Mediterranean meals",
                "Use extra-virgin olive oil with steamed vegetables",
                "Add walnuts and cashews for healthy fats",
                "Choose barley or oats as your whole grain base",
                "Include green peas and string beans for plant variety"
            ],
            "fiber": [
                "Start with artichoke and broccoli for gentle fiber introduction",
                "Include green peas and string beans for soluble fiber",
                "Add flaxseeds gradually to support digestion",
                "Choose barley and oats for whole grain fiber",
                "Use steaming to make vegetables easier to digest"
            ],
            "dairy_free": [
                "Focus on artichoke and broccoli for calcium-rich alternatives",
                "Include walnuts and cashews for healthy fats and minerals",
                "Use barley and oats as dairy-free grain options",
                "Add flaxseeds for omega-3s and fiber",
                "Choose green peas and string beans for plant protein"
            ],
            "stimulant_reduction": [
                "Include artichoke and broccoli for natural energy support",
                "Choose barley and oats for sustained energy without crashes",
                "Add walnuts and cashews for stable blood sugar",
                "Use light cooking methods to preserve natural energy",
                "Focus on gentle movement to boost natural energy"
            ],
            "time_restricted": [
                "Start with barley and oats for stable blood sugar during fasting",
                "Include artichoke and broccoli for nutrient density",
                "Add flaxseeds for satiety and hormone balance",
                "Use light cooking methods to maximize nutrient absorption",
                "Focus on gentle movement to support metabolic health"
            ],
            "high_protein": [
                "Include green peas and string beans for plant protein",
                "Add walnuts and cashews for healthy fats and protein",
                "Choose barley and oats as protein-rich grains",
                "Use artichoke and broccoli for nutrient-dense vegetables",
                "Focus on strength training to maximize protein utilization"
            ],
            "cycle_syncing": [
                "Rotate vegetables based on cycle phase (artichoke, broccoli this phase)",
                "Choose grains that support liver function (barley, oats)",
                "Include nuts and seeds for hormone production (walnuts, flaxseeds)",
                "Use cooking methods that support detoxification (steaming)",
                "Focus on activities that match rising energy levels"
            ]
        }
    },
    "ovulatory": {
        "phase_info": {
            "name": "Ovulatory Phase",
            "description": "Peak fertility and energy. Perfect time for challenging activities and social engagement.",
            "duration": "3-4 days",
            "energy_level": "peak",
            "hormonal_focus": "estrogen surge, heart support"
        },
        "foods": {
            "grains": ["amaranth", "corn", "quinoa"],
            "vegetables": ["asparagus", "brussels sprouts", "chard", "escarole", "scallion", "spinach"],
            "fruits": ["apricot", "cantaloupe", "coconut", "fig", "guava", "peach", "strawberry"],
            "legumes": ["red lentil", "black soybean"],
            "nuts": ["almond", "flaxseeds", "pecan", "pistachio"]
        },
        "cooking_methods": ["raw", "steaming", "poaching"],
        "habits": {
            "blood_sugar": [
                "Enjoy raw vegetables and fruits to balance estrogen surge",
                "Choose quinoa and amaranth for complex carbohydrates",
                "Include asparagus and Brussels sprouts for hormone metabolism",
                "Add raw nuts like almonds for healthy fats",
                "Try high-intensity activities to maximize your peak energy"
            ],
            "mediterranean": [
                "Focus on raw vegetables like spinach and escarole",
                "Include quinoa as your primary grain",
                "Add almonds and pistachios for healthy fats",
                "Use light cooking methods to preserve nutrients",
                "Include red lentils for plant protein"
            ],
            "fiber": [
                "Emphasize raw vegetables for maximum fiber and nutrients",
                "Include Brussels sprouts and spinach for cruciferous benefits",
                "Add flaxseeds and chia seeds to smoothies",
                "Choose quinoa and amaranth for whole grain fiber",
                "Include red lentils for both protein and fiber"
            ],
            "dairy_free": [
                "Focus on raw vegetables for calcium and nutrients",
                "Include almonds and pistachios for calcium-rich nuts",
                "Choose quinoa and amaranth as nutrient-dense grains",
                "Add flaxseeds for omega-3s and minerals",
                "Use raw preparation to maximize nutrient absorption"
            ],
            "stimulant_reduction": [
                "Include raw vegetables for natural energy and nutrients",
                "Choose quinoa and amaranth for sustained energy",
                "Add almonds and pistachios for stable blood sugar",
                "Use raw preparation to preserve natural energy",
                "Focus on high-intensity activities for natural energy boost"
            ],
            "time_restricted": [
                "Start with quinoa and amaranth for stable blood sugar",
                "Include raw vegetables for maximum nutrient density",
                "Add almonds and pistachios for satiety",
                "Use raw preparation to maximize nutrient absorption",
                "Focus on high-intensity activities to support metabolic health"
            ],
            "high_protein": [
                "Include red lentils and black soybeans for plant protein",
                "Add almonds and pistachios for protein and healthy fats",
                "Choose quinoa as a complete protein grain",
                "Use raw vegetables for nutrient-dense protein support",
                "Focus on high-intensity training to maximize protein synthesis"
            ],
            "cycle_syncing": [
                "Emphasize raw foods to balance estrogen surge",
                "Choose grains that support heart health (quinoa, amaranth)",
                "Include nuts and seeds for hormone balance (almonds, flaxseeds)",
                "Use raw preparation to maximize nutrient absorption",
                "Focus on high-intensity activities that match peak energy"
            ]
        }
    },
    "luteal": {
        "phase_info": {
            "name": "Luteal Phase",
            "description": "Progesterone is rising. Focus on stress management and comfort foods.",
            "duration": "10-14 days",
            "energy_level": "moderate to declining",
            "hormonal_focus": "progesterone support, elimination"
        },
        "foods": {
            "grains": ["brown rice", "millet (kasha)"],
            "vegetables": ["cauliflower", "collard greens", "daikon", "onion", "parsnip", "radish", "squash", "sweet potato"],
            "fruits": ["apple", "date", "pear"],
            "legumes": ["chickpea", "kidney bean"],
            "nuts": ["hickory", "pine nut", "pumpkin seeds"]
        },
        "cooking_methods": ["roasting", "baking"],
        "habits": {
            "blood_sugar": [
                "Choose sweet potato and brown rice for stable blood sugar",
                "Include cauliflower and collard greens for fiber support",
                "Use roasting and baking methods for warming foods",
                "Add pumpkin seeds for magnesium and healthy fats",
                "Focus on strength training to support metabolism"
            ],
            "mediterranean": [
                "Include roasted vegetables like cauliflower and squash",
                "Use brown rice as your whole grain base",
                "Add pine nuts and pumpkin seeds for healthy fats",
                "Include chickpeas and kidney beans for plant protein",
                "Use olive oil in roasting for Mediterranean flavors"
            ],
            "fiber": [
                "Increase fiber with roasted vegetables like cauliflower",
                "Include collard greens and sweet potato for soluble fiber",
                "Add chickpeas and kidney beans for protein and fiber",
                "Choose brown rice and millet for whole grain fiber",
                "Use roasting to make vegetables more digestible"
            ],
            "dairy_free": [
                "Focus on roasted vegetables for calcium and nutrients",
                "Include pine nuts and pumpkin seeds for calcium-rich seeds",
                "Choose brown rice and millet as nutrient-dense grains",
                "Add chickpeas and kidney beans for protein and minerals",
                "Use roasting to enhance nutrient absorption"
            ],
            "stimulant_reduction": [
                "Include roasted vegetables for natural energy and nutrients",
                "Choose brown rice and sweet potato for sustained energy",
                "Add pine nuts and pumpkin seeds for stable blood sugar",
                "Use roasting for warming, comforting preparation",
                "Focus on strength training for natural energy boost"
            ],
            "time_restricted": [
                "Start with brown rice and sweet potato for stable blood sugar",
                "Include roasted vegetables for maximum nutrient density",
                "Add pine nuts and pumpkin seeds for satiety",
                "Use roasting to enhance nutrient absorption",
                "Focus on strength training to support metabolic health"
            ],
            "high_protein": [
                "Include chickpeas and kidney beans for plant protein",
                "Add pine nuts and pumpkin seeds for protein and healthy fats",
                "Choose brown rice as a protein-rich grain",
                "Use roasted vegetables for nutrient-dense protein support",
                "Focus on strength training to maximize protein utilization"
            ],
            "cycle_syncing": [
                "Focus on warming foods to support progesterone",
                "Choose grains that support elimination (brown rice, millet)",
                "Include nuts and seeds for hormone balance (pine nuts, pumpkin seeds)",
                "Use roasting and baking for warming preparation",
                "Focus on strength training that matches moderate energy"
            ]
        }
    },
    "menstrual": {
        "phase_info": {
            "name": "Menstrual Phase",
            "description": "Your period is active. Focus on rest, iron-rich foods, and gentle movement.",
            "duration": "3-7 days",
            "energy_level": "lowest",
            "hormonal_focus": "iron replenishment, kidney support"
        },
        "foods": {
            "grains": ["buckwheat", "wild rice"],
            "vegetables": ["beet", "kale", "kelp", "mushrooms"],
            "fruits": ["blackberry", "blueberry", "concord grape", "watermelon"],
            "legumes": ["adzuki bean", "black turtle bean"],
            "nuts": ["chestnut", "sesame seeds", "sunflower seeds"]
        },
        "cooking_methods": ["soups", "stews", "slow cooking"],
        "habits": {
            "blood_sugar": [
                "Focus on iron-rich foods like beets and black turtle beans",
                "Choose buckwheat and wild rice for stable blood sugar",
                "Use warming cooking methods like soups and stews",
                "Include sesame seeds for iron and healthy fats",
                "Prioritize gentle movement like walking or yoga"
            ],
            "mediterranean": [
                "Include iron-rich vegetables like kale and beets",
                "Use wild rice as your grain base",
                "Add sesame seeds and sunflower seeds for healthy fats",
                "Include adzuki beans for plant protein and iron",
                "Use olive oil in warming preparations"
            ],
            "fiber": [
                "Focus on iron-rich fiber sources like beets and kale",
                "Include adzuki beans and black turtle beans for protein and fiber",
                "Choose buckwheat and wild rice for whole grain fiber",
                "Add sesame seeds for additional fiber and nutrients",
                "Use gentle cooking methods to support digestion"
            ],
            "dairy_free": [
                "Focus on iron-rich vegetables for calcium and nutrients",
                "Include sesame seeds and sunflower seeds for calcium-rich seeds",
                "Choose buckwheat and wild rice as nutrient-dense grains",
                "Add adzuki beans and black turtle beans for protein and minerals",
                "Use gentle cooking methods to enhance nutrient absorption"
            ],
            "stimulant_reduction": [
                "Include iron-rich vegetables for natural energy and nutrients",
                "Choose buckwheat and wild rice for sustained energy",
                "Add sesame seeds and sunflower seeds for stable blood sugar",
                "Use gentle cooking methods for warming, restorative preparation",
                "Focus on gentle movement for natural energy boost"
            ],
            "time_restricted": [
                "Start with buckwheat and wild rice for stable blood sugar",
                "Include iron-rich vegetables for maximum nutrient density",
                "Add sesame seeds and sunflower seeds for satiety",
                "Use gentle cooking methods to enhance nutrient absorption",
                "Focus on gentle movement to support metabolic health"
            ],
            "high_protein": [
                "Include adzuki beans and black turtle beans for plant protein",
                "Add sesame seeds and sunflower seeds for protein and healthy fats",
                "Choose buckwheat as a protein-rich grain",
                "Use iron-rich vegetables for nutrient-dense protein support",
                "Focus on gentle movement to support protein utilization"
            ],
            "cycle_syncing": [
                "Focus on iron-rich foods to replenish blood loss",
                "Choose grains that support kidney function (buckwheat, wild rice)",
                "Include nuts and seeds for hormone balance (sesame, sunflower)",
                "Use gentle cooking methods for restorative preparation",
                "Focus on gentle activities that match low energy levels"
            ]
        }
    }
}

def get_phase_data(phase: str) -> dict:
    """Get phase-specific data from InFlo book"""
    return INFLO_PHASE_DATA.get(phase, {})

def get_phase_habits(phase: str, intervention_type: str) -> list:
    """Get phase-specific habits for a given intervention type"""
    phase_data = get_phase_data(phase)
    if not phase_data or "habits" not in phase_data:
        return []
    
    return phase_data["habits"].get(intervention_type, [])

def get_phase_info(phase: str) -> dict:
    """Get phase information"""
    phase_data = get_phase_data(phase)
    return phase_data.get("phase_info", {})

def get_phase_foods(phase: str) -> dict:
    """Get phase-specific food recommendations"""
    phase_data = get_phase_data(phase)
    return phase_data.get("foods", {})

def get_phase_cooking_methods(phase: str) -> list:
    """Get phase-specific cooking methods"""
    phase_data = get_phase_data(phase)
    return phase_data.get("cooking_methods", [])

