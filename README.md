# HerFoodCode - AI-Powered Women's Health App

A comprehensive health and wellness application that provides personalized intervention recommendations for women's health conditions, particularly PCOS and hormonal imbalances.

## 🏗️ Architecture

- **Backend**: FastAPI with Supabase database
- **Frontend**: React Native mobile app
- **AI**: OpenAI GPT-4 with RAG pipeline
- **Database**: PostgreSQL (Supabase)
- **Authentication**: Supabase Auth with RLS

## 📁 Project Structure

```
hfc_app_v2/
├── backend/                    # FastAPI backend
│   ├── api.py                 # Main API endpoints
│   ├── rag_pipeline.py        # RAG processing pipeline
│   ├── auth_service.py        # Authentication service
│   ├── llm.py                 # LLM configuration
│   ├── llm_explanations.py    # LLM explanation generation
│   ├── simple_intake_service.py # Data collection service
│   ├── models/                # Data models and schemas
│   ├── interventions/         # Intervention matching logic
│   ├── retrievers/            # Vector store retrieval
│   ├── utils/                 # Utility functions
│   ├── data/                  # Data and vector stores
│   └── requirements.txt       # Python dependencies
├── mobile/                    # React Native mobile app
│   ├── src/
│   │   ├── screens/           # App screens
│   │   ├── components/        # Reusable components
│   │   ├── navigation/        # Navigation logic
│   │   ├── services/          # API services
│   │   ├── contexts/          # React contexts
│   │   ├── types/             # TypeScript types
│   │   └── constants/         # App constants
│   ├── App.tsx               # Main app component
│   └── package.json          # Node.js dependencies
└── archive/                   # Archived files (deprecated)
```

## 🚀 Quick Start

### Backend Setup

1. **Install dependencies**:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env with your Supabase and OpenAI credentials
   ```

3. **Start the server**:
   ```bash
   uvicorn api:app --reload --host 0.0.0.0 --port 8000
   ```

### Mobile App Setup

1. **Install dependencies**:
   ```bash
   cd mobile
   npm install
   ```

2. **Start the development server**:
   ```bash
   npx expo start
   ```

## 🔧 Key Features

### Backend Features
- **RAG Pipeline**: Retrieval-Augmented Generation for intervention recommendations
- **Authentication**: User registration, login, and profile management
- **Database Integration**: Supabase with Row Level Security (RLS)
- **LLM Integration**: OpenAI GPT-4 for explanations and recommendations
- **Vector Search**: ChromaDB for semantic search of interventions

### Mobile App Features
- **Authentication**: Login/Register screens with form validation
- **Story Intake**: Comprehensive health assessment
- **Recommendations**: AI-powered intervention suggestions
- **Habit Tracking**: Daily habit monitoring and streaks
- **Profile Management**: User profile and settings

## 📊 Data Flow

1. **User Input** → Mobile app collects health data
2. **API Processing** → Backend validates and processes input
3. **RAG Pipeline** → Matches user data with interventions
4. **LLM Enhancement** → Generates personalized explanations
5. **Response** → Returns recommendations to mobile app

## 🔐 Security

- **Row Level Security (RLS)** enabled on all user tables
- **JWT Authentication** with Supabase Auth
- **Data Isolation** - users can only access their own data
- **Input Validation** with Pydantic models

## 🧪 Testing

The application includes comprehensive testing for:
- API endpoints
- Authentication flows
- Database operations
- Mobile app functionality

## 📝 API Endpoints

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `GET /auth/profile/{user_id}` - Get user profile

### Recommendations
- `POST /recommend` - Get intervention recommendations
- `POST /daily-progress` - Save daily habit progress
- `GET /user/{user_id}/daily-progress` - Get user progress

## 🗄️ Database Schema

### Core Tables
- `user_profiles` - User account information
- `intakes` - Health assessment data
- `daily_habit_entries` - Daily habit tracking
- `InterventionsBASE` - Intervention database
- `HabitsBASE` - Habit database

## 🔄 Development

### Adding New Features
1. Update models in `backend/models/`
2. Add API endpoints in `backend/api.py`
3. Update mobile app screens in `mobile/src/screens/`
4. Test with the provided test scripts

### Database Changes
1. Update models in `backend/models/`
2. Run migration scripts (if needed)
3. Update RLS policies
4. Test with authentication

## 📚 Documentation

- **API Documentation**: Available at `http://localhost:8000/docs` when running
- **Code Comments**: Comprehensive inline documentation
- **Type Hints**: Full TypeScript and Python type annotations

## 🚨 Troubleshooting

### Common Issues
1. **Database Connection**: Check Supabase credentials in `.env`
2. **OpenAI API**: Verify API key and quota
3. **Mobile App**: Ensure backend is running on correct port
4. **Authentication**: Check RLS policies and user permissions

### Logs
- Backend logs: Check terminal output
- Mobile logs: Use Expo CLI or React Native debugger
- Database logs: Check Supabase dashboard

## 📄 License

This project is proprietary software. All rights reserved.

## 🤝 Contributing

For development questions or issues, please contact the development team.

---

**Status**: Production Ready ✅  
**Last Updated**: January 2025  
**Version**: 2.0.0