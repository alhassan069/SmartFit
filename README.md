# SmartFit: AI-Powered Fitness Coach
AI Fitness Coach system that combines workout planning, nutrition guidance, and progress tracking with RAG-based knowledge retrieval through a simple chat interface.


## Tech
### 1. Backend Development (FastAPI + Python)
Build a RESTful API with the following CRUD operations:

User Management
Simple Registration: Create a user with a username, email, and password (plain text storage)
Simple Login: Basic authentication endpoint
User Profile: Store age, weight, height, fitness goals, medical conditions, activity level
Workout Plans
CRUD operations for workout plans
Fields: plan_name, difficulty_level, duration, target_muscle_groups, exercises_list
Basic pagination (limit/offset)
Exercise
CRUD for individual exercises
Fields: exercise_name, category, equipment_needed, difficulty, instructions, target_muscles etc
Progress Tracking
CRUD for user workout sessions
Fields: user_id, workout_id, date, exercises_completed, sets, reps, weights, duration, calories_burned
Nutrition Logs
CRUD for daily nutrition entries
Fields: user_id, date, meals, calories, macronutrients (protein, carbs, fats)
Chat Interface
POST endpoint for user questions
Integration with the RAG system for contextual responses
### 2. Database Architecture
SQL/MongoDB Database Storage:
User profiles and authentication data
User-generated data: workout logs, progress tracking, nutrition entries
Structured data: workout plans, user preferences
Relational data: user-workout relationships, user-nutrition relationships
Vector Database Storage:
Knowledge base content: exercise descriptions, nutrition information, fitness methodologies
Static reference material: training principles, recovery protocols, injury prevention guides
Embeddings: for semantic search and similarity matching
### 3. RAG Implementation
Knowledge Base Content:
Exercise Database: 100+ exercises with detailed descriptions, proper form, and variations
Nutrition Information: Food calories, macronutrients, meal planning guidelines
Fitness Methodologies: Training principles, recovery protocols, injury prevention
RAG System Requirements:
Implement vector embeddings for semantic search (using sentence-transformers or OpenAI embeddings)
Basic chunking strategy for documents (500-1000 token chunks)
Similarity search with relevance scoring
Context retrieval for user queries
Query Processing:
Accept natural language questions about workouts, nutrition, and fitness
Retrieve relevant context from the vector database
Generate responses using retrieved context + user's data
### 4. Frontend Implementation
Simple Chat Interface:
Login/Signup forms
Chat interface with message history
Basic user dashboard showing recent activity
Login state management via localStorage/sessionStorage
State Management:
Store user session in localStorage (user_id, username)
No JWT tokens - simple session-based auth
### 5. Authentication & State Management
Simple Authentication:
Basic username/password login (no encryption required)
Store user session in localStorage/SessionStorage
Simple session validation on protected endpoints
Frontend State:
localStorage: User session, preferences
sessionStorage: Chat history, temporary form data
No complex state management - vanilla JS or simple React state
Technical Specifications
Backend Stack
Framework: FastAPI
Database: PostgreSQL/MySQL or MongoDB
Vector Store: ChromaDB / FAISS (local storage) / PineCone
AI/ML: openai LLM + Embedding model

### Frontend Stack
Basic: Any framework of your choice
No advanced frameworks required
Data Storage Clarification
SQL/MongoDB → Everything user-specific, dynamic, structured (users, workouts, logs).
RAG → Everything domain knowledge, static, unstructured (fitness science, exercise/nutrition details).

### Traditional Database (SQL/MongoDB):
Users: id, username, email, password, age, weight, height, goals
Workouts: id, user_id, plan_name, date, exercises, duration
Nutrition: id, user_id, date, meals, calories, macros
Progress: id, user_id, workout_id, sets, reps, weights, notes
### Vector Database:
Exercise Knowledge: exercise descriptions, instructions, benefits
Nutrition Knowledge: food information, dietary guidelines, meal plans
Fitness Knowledge: training principles, recovery, injury prevention
### API Endpoints
Authentication
POST /auth/register - User registration
POST /auth/login - User login
GET /auth/user/{user_id} - Get user profile
Core CRUD
GET/POST/PUT/DELETE /workouts - Workout management
GET/POST/PUT/DELETE /exercises - Exercise database
GET/POST/PUT/DELETE /nutrition - Nutrition logging
GET/POST/PUT/DELETE /progress - Progress tracking
AI Chat
POST /chat/ask - Send question, get RAG-powered response
GET /chat/history/{user_id} - Get chat history
