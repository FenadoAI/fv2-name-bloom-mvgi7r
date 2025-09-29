# 👶 Baby Name Generator

A modern AI-powered baby name generator that helps expectant parents discover perfect names for their little ones. Built with React and FastAPI, featuring user accounts, favorites management, and shareable lists.

## ✨ Features

### 🤖 AI-Powered Name Generation
- Generate personalized baby names using advanced AI
- Filter by gender (boy, girl, unisex)
- Choose from different styles (traditional, modern, unique, etc.)
- Get detailed information including origin, meaning, and popularity

### 👤 User Management
- Secure user registration and authentication
- JWT-based session management
- Persistent favorites across sessions

### ❤️ Favorites System
- Save favorite names to your personal collection
- Easy add/remove from favorites
- View all favorites in a dedicated page

### 🔗 Social Sharing
- Create shareable links for your favorite names
- Share with partners, family, and friends
- Public access to shared lists without registration

### 📱 Modern UI/UX
- Responsive design for all devices
- Beautiful gradient backgrounds
- Intuitive card-based name display
- Smooth animations and transitions
- Accessibility-first design

## 🛠️ Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **MongoDB** - Document database for flexible data storage
- **LiteLLM** - AI model integration for name generation
- **JWT** - Secure authentication
- **bcrypt** - Password hashing
- **Motor** - Async MongoDB driver

### Frontend
- **React 19** - Latest React with modern patterns
- **React Router v7** - Client-side routing
- **Tailwind CSS** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible UI components
- **Lucide React** - Icon library
- **Axios** - HTTP client

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Node.js 18+
- MongoDB (local or cloud)
- Bun or npm

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd baby-name-generator
   ```

2. **Backend Setup**
   ```bash
   cd backend
   pip install -r requirements.txt

   # Start the backend server
   uvicorn server:app --reload --host 0.0.0.0 --port 8001
   ```

3. **Frontend Setup**
   ```bash
   cd frontend
   bun install  # or npm install

   # Start the development server
   bun start    # or npm start
   ```

4. **Access the Application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8001
   - API Documentation: http://localhost:8001/docs

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register a new user
- `POST /api/auth/login` - Login user

### Name Generation
- `POST /api/names/generate` - Generate baby names with filters

### Favorites Management
- `POST /api/favorites/add/{name_id}` - Add name to favorites
- `DELETE /api/favorites/remove/{name_id}` - Remove from favorites
- `GET /api/favorites` - Get user's favorites

### Sharing
- `POST /api/favorites/share` - Create shareable list
- `GET /api/shared/{share_token}` - Access shared list

## 🧪 Testing

### API Testing
Run the comprehensive API test suite:
```bash
python test_api.py
```

### Frontend Testing
Build and test the frontend:
```bash
cd frontend
npm run build
npm test
```

### Backend Testing
```bash
# Test AI agents functionality
cd backend && python tests/test_agents.py

# Test FastAPI endpoints
cd backend && python tests/test_api.py
```

## 📁 Project Structure

```
baby-name-generator/
├── backend/                 # FastAPI backend
│   ├── server.py           # Main server application
│   ├── ai_agents/          # AI integration modules
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment configuration
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   │   ├── ui/        # shadcn/ui components
│   │   │   ├── NameGenerator.js
│   │   │   ├── AuthPage.js
│   │   │   └── SharedFavorites.js
│   │   ├── App.js         # Main application
│   │   └── index.js       # Entry point
│   ├── package.json       # Dependencies
│   └── tailwind.config.js # Tailwind configuration
├── test_api.py            # API test suite
└── README.md              # This file
```

## 🌟 Key Features Explained

### AI Name Generation
The app uses advanced AI to generate contextual baby names based on:
- **Gender preference** (boy, girl, unisex)
- **Style preference** (traditional, modern, unique, classic, trendy)
- **Count** (1-50 names per generation)

Each generated name includes:
- **Origin**: Cultural/linguistic background
- **Meaning**: What the name represents
- **Popularity Score**: 1-100 scale indicating how common the name is

### User Experience
- **No login required** for basic name generation
- **Account creation** unlocks favorites and sharing
- **Instant favorites** with heart icon toggle
- **Shareable lists** with unique tokens
- **Mobile-first** responsive design

### Security
- **Password hashing** with bcrypt
- **JWT tokens** for secure sessions
- **Input validation** on all endpoints
- **CORS protection** configured for development

Built with ❤️ for expecting parents everywhere 👶
