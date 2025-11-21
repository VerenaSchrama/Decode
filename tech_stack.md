# Tech Stack - HerFoodCode Application

## Summary

HerFoodCode is a women's health and nutrition mobile application built with a modern, AI-powered architecture. The application uses **React Native** for cross-platform mobile development, **FastAPI** for the backend API, **Supabase** as the Backend-as-a-Service (BaaS) for database and authentication, and **LangChain/OpenAI** for AI-powered recommendations and chat functionality. The system implements a **Retrieval-Augmented Generation (RAG)** pipeline using **ChromaDB** vector stores to provide evidence-based nutrition recommendations personalized to users' cycle phases and health profiles.

---

## Frontend (Mobile Application)

### Core Framework
- **React Native** (v0.81.4) - Cross-platform mobile framework
- **React** (v19.1.0) - UI library
- **TypeScript** (v5.9.2) - Type-safe JavaScript
- **Expo** (v54.0.7) - Development platform and toolchain

### Navigation
- **@react-navigation/native** (v7.1.17) - Navigation library
- **@react-navigation/stack** (v7.4.8) - Stack navigator
- **@react-navigation/bottom-tabs** (v7.4.7) - Tab navigator
- **@react-navigation/elements** (v2.6.4) - Navigation elements

### State Management
- **React Context API** - Global state management (AppStateContext, AuthContext, ToastContext)
- **React Hooks** (useState, useEffect, useRef, useCallback) - Component state
- **@tanstack/react-query** (v5.89.0) - Server state management and caching (optional/available)

### UI Components & Libraries
- **@expo/vector-icons** (v15.0.2) - Icon library (Ionicons)
- **react-native-calendar-picker** (v8.0.5) - Calendar component for date selection
- **react-native-render-html** (v6.3.4) - HTML rendering
- **react-native-safe-area-context** (v5.6.0) - Safe area handling
- **react-native-screens** (v4.16.0) - Native screen components
- **@react-native-community/datetimepicker** (v8.4.5) - Date/time picker

### Data Persistence
- **@react-native-async-storage/async-storage** (v2.2.0) - Local key-value storage

### HTTP Client
- **axios** (v1.12.2) - HTTP client for API requests

### Additional Libraries
- **zustand** (v5.0.8) - Lightweight state management (available but not primary)

---

## Backend (API Server)

### Core Framework
- **FastAPI** (v0.115.9) - Modern Python web framework
- **Uvicorn** (v0.34.3) - ASGI server
- **Python** (3.13) - Programming language

### API & Web Framework
- **Starlette** (v0.45.3) - ASGI framework (FastAPI dependency)
- **Pydantic** (v2.11.5) - Data validation and settings management
- **Pydantic Settings** (v2.9.1) - Settings management
- **python-dotenv** (v1.1.0) - Environment variable management

### Database & Backend Services
- **Supabase** (v2.8.0) - Backend-as-a-Service
  - PostgreSQL database
  - Authentication (JWT-based)
  - Row Level Security (RLS)
  - Real-time subscriptions (available)
- **ChromaDB** (v1.0.12) - Vector database for embeddings
- **langchain-chroma** (v0.2.4) - LangChain integration for ChromaDB

### AI & Machine Learning
- **LangChain** (v0.3.25) - LLM application framework
- **LangChain Core** (v0.3.64) - Core LangChain functionality
- **LangChain Community** (v0.3.24) - Community integrations
- **LangChain OpenAI** (v0.2.5) - OpenAI integration
- **OpenAI** (v1.84.0) - OpenAI API client (GPT models)
- **tiktoken** (v0.9.0) - Token counting for LLMs
- **scikit-learn** - Machine learning utilities (for embeddings/similarity)

### RAG Pipeline
- **Custom RAG Implementation** - Retrieval-Augmented Generation pipeline
  - Vector store retrieval (ChromaDB)
  - Context building from scientific literature
  - Intervention matching based on user profiles
  - Cycle-aware habit recommendations

### Authentication & Security
- **python-jose** (v3.3.0) - JWT token handling
- **bcrypt** (v4.3.0) - Password hashing
- **Supabase Auth** - Authentication service

### HTTP & Networking
- **httpx** (v0.27.0) - Async HTTP client
- **httpx-sse** (v0.4.0) - Server-Sent Events support
- **requests** (v2.32.3) - HTTP library (legacy/sync)
- **aiohttp** (v3.12.11) - Async HTTP client/server

### Data Processing
- **pandas** (v2.2.2) - Data manipulation
- **numpy** (v2.1.0+) - Numerical computing
- **pdfplumber** (v0.10.3) - PDF text extraction
- **python-dateutil** (v2.9.0) - Date parsing

### Background Tasks & Scheduling
- **schedule** (v1.2.2) - Job scheduling
- **asyncio** - Async task management

### Observability & Monitoring
- **OpenTelemetry** (v1.34.0) - Observability framework
  - OpenTelemetry API
  - OpenTelemetry SDK
  - FastAPI instrumentation
  - ASGI instrumentation
- **coloredlogs** (v15.0.0) - Colored logging
- **PostHog** (v4.4.0) - Product analytics (available)

### Utilities
- **python-dateutil** (v2.9.0) - Date utilities
- **uuid** - UUID generation
- **json** - JSON handling
- **typing** - Type hints

---

## Database & Storage

### Primary Database
- **Supabase PostgreSQL** - Main relational database
  - Tables: `users`, `intakes`, `intervention_periods`, `user_habits`, `daily_habit_entries`, `daily_moods`, `daily_summaries`, `chat_messages`, `cycle_phases`, `InterventionsBASE`, `HabitsBASE`, `custom_interventions`, `user_interventions`, `completion_summaries`, `notifications`, `profiles`

### Vector Database
- **ChromaDB** - Vector store for embeddings
  - Scientific literature embeddings
  - Intervention matching
  - RAG context retrieval

### Local Storage (Mobile)
- **AsyncStorage** - Client-side key-value storage
  - Session tokens
  - User preferences
  - Cached data

---

## AI & LLM Services

### LLM Provider
- **OpenAI API** - GPT models for:
  - Chat responses
  - Recipe generation
  - Intervention explanations
  - Personalized recommendations

### Embeddings
- **OpenAI Embeddings** - Text embeddings for vector search
- **LangChain Embeddings** - Embedding abstraction layer

### RAG Components
- **Vector Store Retrieval** - ChromaDB-based similarity search
- **Context Building** - User profile + cycle phase + intervention context
- **Prompt Engineering** - Enhanced prompts with scientific evidence
- **Intervention Matcher** - Similarity-based intervention matching

---

## Architecture Patterns

### Backend Architecture
- **RESTful API** - FastAPI endpoints
- **Event-Driven Architecture** - In-memory event bus for intervention completion
- **Service Layer Pattern** - Separation of concerns (services/, models/)
- **Repository Pattern** - Data access abstraction (Supabase models)
- **Singleton Pattern** - Service instances (InterventionPeriodService, CyclePhaseService)

### Frontend Architecture
- **Component-Based Architecture** - React components
- **Context API** - Global state management
- **Custom Hooks** - Reusable logic
- **Service Layer** - API abstraction (services/)
- **Screen-Based Navigation** - Screen components

### Data Flow
1. **User Input** → Frontend (React Native)
2. **API Request** → Backend (FastAPI)
3. **Authentication** → Supabase Auth (JWT)
4. **Data Storage** → Supabase PostgreSQL
5. **RAG Processing** → LangChain + ChromaDB + OpenAI
6. **Response** → Frontend (React Native)

---

## Development Tools

### Backend
- **Python Virtual Environment** - Dependency isolation
- **Uvicorn** - Development server with hot reload
- **Python-dotenv** - Environment configuration

### Frontend
- **Expo CLI** - Development tooling
- **TypeScript** - Type checking
- **React Native Debugger** - Debugging tools

### Version Control
- **Git** - Source control

---

## Deployment & Infrastructure

### Backend Deployment
- **Hetzner** - Cloud server hosting
- **systemd** - Service management
- **rsync** - File synchronization
- **Uvicorn** - Production ASGI server

### Frontend Deployment
- **Vercel** - Web deployment (mentioned in CORS config)
- **Expo** - Mobile app distribution

### Environment
- **Environment Variables** - Configuration management
- **CORS** - Cross-origin resource sharing
- **HTTPS** - Secure connections

---

## Key Features & Integrations

### Core Features
- **User Authentication** - Email/password with Supabase Auth
- **Intake Flow** - Multi-step user onboarding
- **Intervention Recommendations** - AI-powered matching
- **Daily Habit Tracking** - Progress tracking with mood
- **Cycle Phase Tracking** - Menstrual cycle awareness
- **Nutritionist Chat** - AI-powered chat with RAG
- **Recipe Generation** - Personalized recipe creation
- **Progress Analytics** - User progress metrics
- **Intervention Management** - Start, complete, reset interventions

### Integrations
- **Supabase** - Database, Auth, Storage
- **OpenAI** - LLM and embeddings
- **ChromaDB** - Vector search
- **LangChain** - LLM orchestration

---

## Security

### Authentication
- **JWT Tokens** - Bearer token authentication
- **Supabase Auth** - Secure user management
- **Token Refresh** - Automatic token renewal

### Data Security
- **Row Level Security (RLS)** - Database-level access control
- **Service Role Keys** - Backend operations bypass RLS
- **Input Validation** - Pydantic models
- **CORS Configuration** - Controlled cross-origin access

---

## Performance Optimizations

### Backend
- **Async/Await** - Non-blocking I/O
- **Connection Pooling** - Database connections
- **Caching** - Vector store caching
- **Parallel Processing** - Promise.all for concurrent operations

### Frontend
- **React.memo** - Component memoization (where applicable)
- **useCallback/useMemo** - Hook optimization
- **Lazy Loading** - Code splitting
- **Parallel API Calls** - Concurrent data fetching

---

## Testing & Quality

### Code Quality
- **TypeScript** - Type safety
- **Pydantic** - Data validation
- **Linting** - Code quality checks

### Error Handling
- **Try-Catch Blocks** - Error handling
- **HTTP Status Codes** - Proper error responses
- **User-Friendly Messages** - Error communication

---

## Documentation

- **API Documentation** - FastAPI auto-generated docs
- **Code Comments** - Inline documentation
- **Markdown Files** - Implementation guides and status docs

---

## Future Considerations

### Potential Additions
- **Unit Tests** - pytest for backend, Jest for frontend
- **E2E Tests** - Integration testing
- **CI/CD Pipeline** - Automated deployment
- **Monitoring** - Application performance monitoring
- **Error Tracking** - Sentry or similar
- **Analytics** - User behavior tracking

---

*Last Updated: Based on current codebase analysis*
*Version: 2.0.0*

