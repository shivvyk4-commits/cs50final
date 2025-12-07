# Lango - Spanish Learning Platform

## Overview

Lango is a Spanish learning web application that combines structured lessons with AI-powered conversational practice. The platform features personalized learning paths, vocabulary flashcards, verb conjugation practice, spaced repetition review, and automated lesson scheduling through Google Calendar integration. Built with Flask and powered by Google's Gemini AI, it provides adaptive difficulty levels and speech recognition for pronunciation practice.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Framework
- **Technology**: Flask (Python web framework)
- **Rationale**: Lightweight, flexible framework suitable for rapid development of web applications with AI integration
- **Key Components**:
  - SQLAlchemy ORM for database interactions
  - Flask-Login for user session management
  - Flask-Dance for OAuth integration
  - Modular route structure separating concerns

### Authentication & Authorization
- **Solution**: Replit-based OAuth authentication
- **Implementation**: Custom `replit_auth.py` module with Flask-Dance integration
- **Features**:
  - Browser session key tracking for multi-device support
  - User profile management with onboarding flow
  - Persistent login sessions via Flask session management
- **Rationale**: Leverages Replit's built-in authentication infrastructure for seamless user management

### Database Architecture
- **ORM**: SQLAlchemy with declarative base pattern
- **Models**:
  - `User`: Core user profile with learning preferences and progress tracking
  - `OAuth`: OAuth token storage linked to users and browser sessions
  - `LessonCategory`: Hierarchical lesson organization
  - `Vocabulary` & `Verb`: Learning content entities
  - `UserProgress`: Tracks completion status per category
  - `ChatSession` & `ChatMessage`: Conversation history storage
  - `VocabularyReview`: Spaced repetition scheduling
  - `ScheduledLesson`: Calendar integration for planned lessons
- **Configuration**: Connection pooling with health checks (pool_pre_ping) and 300-second recycle time for reliability
- **Rationale**: Relational model supports complex learning progress tracking and relationships between users, content, and reviews

### AI Integration
- **Service**: Google Gemini API
- **Implementation**: `gemini_service.py` with lazy client initialization
- **Features**:
  - Adaptive conversation difficulty (3 levels: Beginner, Intermediate, Advanced)
  - Dynamic response generation based on user progress
  - Contextual corrections and explanations
- **Difficulty System**:
  - **Level 1 (Beginner)**: 30% Spanish, simple sentences, present tense only
  - **Level 2 (Intermediate)**: 60% Spanish, compound sentences, multiple tenses
  - **Level 3 (Advanced)**: 85% Spanish, complex expressions, all grammatical structures
- **Rationale**: Provides scalable conversational practice without requiring human tutors, adapts to individual learning pace

### Frontend Architecture
- **Template Engine**: Jinja2 (Flask's default)
- **Design System**: Custom CSS with design tokens and utility classes
- **Typography**: Inter (UI/body) + Space Grotesk (headings) from Google Fonts
- **Component Strategy**: Reusable base template with block inheritance
- **Key Sections**:
  - Landing page for unauthenticated users
  - Onboarding flow (multi-step form)
  - Dashboard with lesson navigation
  - Interactive lesson components (flashcards, conjugation tables)
  - Chat interface for AI conversations
  - Spaced repetition review system
- **Rationale**: Server-side rendering reduces frontend complexity while maintaining interactive features through progressive enhancement

### Learning Content Management
- **Solution**: Seed data initialization on application startup
- **Implementation**: `seed_data.py` populates lesson categories with vocabulary and verbs
- **Content Structure**:
  - Categories (e.g., Greetings, Food) with icons and ordering
  - Vocabulary entries with Spanish word, English translation, pronunciation guide
  - Verb conjugations (present tense) for all pronouns
- **Rationale**: Pre-seeded content enables immediate learning experience without content management overhead

### Spaced Repetition System
- **Algorithm**: Track review intervals and next review dates per vocabulary item
- **Schema**: `VocabularyReview` model with `next_review_date` and `interval_days`
- **Implementation**: Reviews presented based on date-based filtering
- **Rationale**: Scientifically-backed method for long-term retention, proven effective in language learning

### Lesson Scheduling
- **Integration**: Google Calendar via Replit Connectors
- **Service**: `calendar_service.py` handles OAuth token management
- **Features**:
  - Automatic lesson scheduling based on user preferences
  - Manual rescheduling capabilities
  - Token refresh logic with expiration checking
- **Rationale**: Integrates learning into users' existing calendars, improving habit formation

### Session Management
- **Strategy**: Browser session key tracking in OAuth model
- **Implementation**: Unique constraint on `(user_id, browser_session_key, provider)`
- **Features**: Multi-device support with device-specific OAuth tokens
- **Rationale**: Allows users to maintain separate sessions across devices while sharing user data

### Error Handling
- **Custom Error Pages**: 403 (Access Denied), 404 (Page Not Found)
- **Logging**: Python logging module with DEBUG level throughout
- **Rationale**: Provides user-friendly error experiences and debugging capabilities

### Application Structure
- **Entry Point**: `main.py` runs Flask development server
- **Configuration**: Environment-based (DATABASE_URL, SESSION_SECRET, GEMINI_API_KEY)
- **Initialization Flow**: App → Database → Models → Routes → Seed Data
- **Middleware**: ProxyFix for proper header handling in deployed environments

## External Dependencies

### Third-Party APIs
- **Google Gemini API**: AI-powered conversation generation and language learning assistance
  - API key configuration via `GEMINI_API_KEY` environment variable
  - Client managed through `gemini_service.py`
- **Replit Connectors**: Google Calendar OAuth integration
  - Hostname via `REPLIT_CONNECTORS_HOSTNAME`
  - Authentication via `REPL_IDENTITY` or `WEB_REPL_RENEWAL` tokens

### Database
- **Type**: SQL database (configured via SQLAlchemy)
- **Connection**: `DATABASE_URL` environment variable
- **Features**: Connection pooling, automatic reconnection, health checks

### Authentication Provider
- **Replit OAuth**: User authentication and profile management
- **Implementation**: Flask-Dance OAuth consumer blueprint
- **Storage**: Custom `UserSessionStorage` class for token persistence

### Node.js Dependencies
- **googleapis**: Google APIs client library for potential calendar operations
- **Purpose**: Enables direct Google Calendar API interactions if needed beyond Replit Connectors

### Python Libraries
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM integration
- **Flask-Login**: User session management
- **Flask-Dance**: OAuth consumer implementation
- **google-genai**: Google Gemini API client
- **Werkzeug**: WSGI utilities and middleware

### Frontend Resources
- **Google Fonts**: Inter and Space Grotesk typefaces
- **Font Awesome**: Icon library (v6.4.0 via CDN)
- **Rationale**: CDN delivery reduces bundle size and improves cache hit rates

### Design Resources
- **Reference Document**: `design_guidelines.md` provides comprehensive design system
- **Inspiration**: Duolingo, Memrise, Linear aesthetics
- **Approach**: Progressive clarity, friendly professionalism, focus-driven layouts