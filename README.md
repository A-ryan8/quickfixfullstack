# 🏛️ QuickFix - Civic Engagement Platform

A complete civic engagement platform that allows citizens to report municipal issues through a mobile app, with AI-powered image analysis and an admin dashboard for complaint management.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │    │  FastAPI Backend │    │ React Dashboard │
│   (Mobile)      │◄──►│   (Python)      │◄──►│   (Admin)       │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  MySQL Database │
                       │   (civic_db)    │
                       └─────────────────┘
```

## 🚀 Features

### Mobile App (Flutter)
- 📱 **Cross-platform** mobile app for iOS and Android
- 📸 **Image capture** with camera or gallery selection
- 📍 **GPS location** detection and manual location input
- 🤖 **AI-powered** image analysis using Gemini API
- 📄 **Automatic PDF** report generation
- 🌐 **Multi-language** support (English, Hindi, Marathi)

### Backend API (FastAPI)
- 🔌 **RESTful API** with automatic documentation
- 🗄️ **MySQL database** integration
- 📁 **File upload** handling for images and PDFs
- 🔄 **Real-time** status updates
- 🛡️ **CORS** enabled for cross-origin requests
- 📊 **Statistics** endpoint for dashboard analytics

### Admin Dashboard (React)
- 📊 **Interactive dashboard** with complaint management
- 📋 **Data grid** with sorting, filtering, and pagination
- 🔄 **Real-time** status updates
- 📈 **Analytics** and statistics visualization
- 🎨 **Modern UI** with Material-UI components
- 📱 **Responsive** design for all devices

## 🛠️ Technology Stack

### Frontend
- **Flutter** - Mobile app development
- **React** - Admin dashboard
- **Material-UI** - UI components
- **Vite** - Build tool

### Backend
- **FastAPI** - Python web framework
- **MySQL** - Database
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### AI & Services
- **Google Gemini API** - Image analysis
- **PDF Generation** - Automatic report creation
- **File Upload** - Image and document handling

## 📋 Prerequisites

- **Python 3.8+**
- **Node.js 16+**
- **Flutter SDK 3.0+**
- **MySQL 8.0+**
- **Git**

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd completequickfix
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```

### 3. Database Setup
```bash
# Create database
mysql -u root -p
CREATE DATABASE civic_db;
```

### 4. Environment Configuration
```bash
# Copy environment template
cp env_template.txt .env
# Edit .env with your database credentials
```

### 5. Start Backend Server
```bash
python -m uvicorn main_simple_complaints:app --reload --host 0.0.0.0 --port 8000
```

### 6. React Dashboard Setup
```bash
cd civic
npm install
npm run dev
```

### 7. Flutter App Setup
```bash
cd flutter_app
flutter pub get
flutter run
```

## 📁 Project Structure

```
completequickfix/
├── backend/                 # FastAPI backend
│   ├── main_simple_complaints.py  # Main server file
│   ├── database.py         # Database connection
│   ├── models.py           # Data models
│   ├── config.py           # Configuration
│   ├── uploads/            # Uploaded images
│   ├── pdfs/               # Generated PDFs
│   └── venv/               # Python virtual environment
├── civic/                  # React admin dashboard
│   ├── src/
│   │   ├── pages/          # Dashboard pages
│   │   ├── components/     # UI components
│   │   └── api/            # API communication
│   └── package.json        # Dependencies
├── flutter_app/            # Flutter mobile app
│   ├── lib/
│   │   ├── services/       # API and PDF services
│   │   └── upload_complaint_screen.dart
│   └── pubspec.yaml        # Dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Backend Environment Variables
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=civic_db
DB_PORT=3306
```

### AI API Configuration
- **Gemini API Key** - Configured in `flutter_app/lib/services/api_service.dart`
- **API URL** - `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent`

## 📊 API Endpoints

### Complaints
- `GET /api/complaints` - Get all complaints
- `POST /api/complaints` - Create new complaint
- `PUT /api/complaints/{id}` - Update complaint status
- `DELETE /api/complaints/{id}` - Delete complaint

### Statistics
- `GET /api/complaints/stats` - Get complaint statistics

### Health Check
- `GET /` - API health check
- `GET /api/test-db` - Database connection test

## 🧪 Testing

### Backend API Testing
```bash
cd backend
python test_api.py
```

### Manual Testing
```bash
# Test complaints endpoint
curl http://localhost:8000/api/complaints

# Test stats endpoint
curl http://localhost:8000/api/complaints/stats
```

## 📱 Mobile App Features

### Complaint Submission
1. **Capture/Select Image** - Camera or gallery
2. **Location Detection** - GPS or manual input
3. **AI Analysis** - Automatic title and description generation
4. **PDF Generation** - Professional report creation
5. **Upload** - Submit to backend server

### AI Integration
- **Image Analysis** - Identifies municipal issues
- **Title Generation** - Creates concise issue titles
- **Description Generation** - Detailed problem analysis
- **Fallback System** - Works even when AI is unavailable

## 🎛️ Admin Dashboard Features

### Complaint Management
- **View All Complaints** - Complete list with details
- **Status Updates** - Change complaint status
- **Image Viewing** - Click to view complaint images
- **Real-time Updates** - Automatic refresh after changes

### Analytics
- **Total Complaints** - Overall count
- **Status Breakdown** - By complaint status
- **Recent Activity** - Latest submissions
- **Monthly Trends** - Historical data

## 🔒 Security Features

- **Environment Variables** - Sensitive data protection
- **CORS Configuration** - Cross-origin request handling
- **Input Validation** - Pydantic model validation
- **File Upload Security** - Type and size restrictions

## 🚀 Deployment

### Backend Deployment
```bash
# Production server
uvicorn main_simple_complaints:app --host 0.0.0.0 --port 8000
```

### React Dashboard Deployment
```bash
cd civic
npm run build
# Deploy dist/ folder to your web server
```

### Flutter App Deployment
```bash
cd flutter_app
flutter build apk  # Android
flutter build ios  # iOS
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API documentation at `http://localhost:8000/docs`

## 🎉 Acknowledgments

- **Google Gemini API** for AI image analysis
- **FastAPI** for the excellent Python web framework
- **Material-UI** for beautiful React components
- **Flutter** for cross-platform mobile development

---

**Built with ❤️ for better civic engagement**





