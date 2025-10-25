// TypeScript types for Story Intake form
export interface Profile {
  name: string;
  dateOfBirth: string; // Changed from age to date of birth
}

export interface Symptoms {
  selected: string[];
  additional?: string;
}

export interface InterventionItem {
  intervention: string;
  helpful: boolean;
}

export interface Interventions {
  selected: InterventionItem[];
  additional?: string;
}

export interface DietaryPreferences {
  selected: string[];
  additional?: string;
}

export interface LastPeriod {
  date: string; // Date of last period
  hasPeriod: boolean; // For "I don't have a period" option
  cycleLength?: number; // Average cycle length in days
}

export interface SelectedHabit {
  habit: string;
  selected: boolean;
}

export interface HabitSelectionData {
  habits: SelectedHabit[];
}

export interface StoryIntakeData {
  profile: Profile;
  lastPeriod: LastPeriod;
  symptoms: Symptoms;
  interventions: Interventions;
  dietaryPreferences: DietaryPreferences;
  consent: boolean;
  // anonymous field removed - all users are authenticated
  intake_id?: string; // ID returned from backend after intake submission
}

export interface StoryIntakeStep {
  id: number;
  title: string;
  subtitle: string;
  component: string;
}

export const STORY_INTAKE_STEPS: StoryIntakeStep[] = [
  {
    id: 1,
    title: "Your Name",
    subtitle: "What should we call you?",
    component: "NameStep"
  },
  {
    id: 2,
    title: "Date of Birth",
    subtitle: "When were you born?",
    component: "DateOfBirthStep"
  },
  {
    id: 3,
    title: "Last Period",
    subtitle: "When did your last period begin?",
    component: "LastPeriodStep"
  },
  {
    id: 4,
    title: "Cycle Length",
    subtitle: "What's your average cycle length?",
    component: "CycleLengthStep"
  },
  {
    id: 5,
    title: "Symptoms & Conditions",
    subtitle: "Have you ever experienced any of the following symptoms?",
    component: "SymptomsStep"
  },
  {
    id: 6,
    title: "Food Interventions You've Tried",
    subtitle: "What dietary approaches have you experimented with?",
    component: "InterventionsStep"
  },
  {
    id: 7,
    title: "Dietary Preferences",
    subtitle: "What are your dietary preferences and restrictions?",
    component: "DietaryStep"
  },
  {
    id: 8,
    title: "Consent & Privacy",
    subtitle: "Your data, your choice",
    component: "ConsentStep"
  }
];

// Symptom options - only symptoms women can experience, not medical diagnoses
export const SYMPTOM_OPTIONS = [
  "PCOS", "Endometriosis", "IBS", "Insulin resistance", "Thyroid disorders",
  "Adrenal fatigue", "Perimenopause", "Menopause", "Irregular periods",
  "Heavy periods", "Painful periods", "PMS", "PMDD", "Fertility issues",
  "Weight gain", "Hair loss", "Acne", "Mood swings", "Anxiety", "Depression",
  "Fatigue", "Sleep issues", "Brain fog", "Joint pain", "Digestive issues",
  "Food cravings", "Blood sugar issues", "Hot flashes", "Night sweats",
  "Headache", "Sleep quality", "Cravings: Sweet", "Backache",
  "Tender breasts", "Dry-skin", "Bloating", "Sensitive", 
  "Cramps", "Irritable"
];

export const INTERVENTION_OPTIONS = [
  "Control your blood sugar",
  "Mediterranean Diet",
  "Boost your fiber intake",
  "Less or no dairy",
  "Cut out or decrease stimulants",
  "Time-restricted eating",
  "High-protein diet",
  "Eat with your cycle"
];

export const DIETARY_PREFERENCE_OPTIONS = [
  "Vegetarian",
  "Vegan", 
  "Keto",
  "Gluten-free",
  "Dairy-free",
  "Paleo",
  "Low-carb",
  "High-protein",
  "Intermittent fasting",
  "Raw food",
  "Pescatarian",
  "Flexitarian",
  "Whole30",
  "Anti-inflammatory"
];

