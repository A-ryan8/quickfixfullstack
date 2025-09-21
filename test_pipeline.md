# Full-Stack Message Pipeline Test Guide

This guide will help you test the complete data pipeline between the Flutter app, backend server, and React website.

## Prerequisites

Make sure you have the following installed:
- Node.js (for backend and React)
- Flutter SDK (for Flutter app)
- A web browser

## Step 1: Start the Backend Server

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the server:
   ```bash
   npm start
   ```

   You should see: `Backend server is running at http://localhost:3000`

## Step 2: Start the React Website

1. Open a new terminal and navigate to the civic directory:
   ```bash
   cd civic
   ```

2. Install dependencies (if not already done):
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

   The React app should be available at `http://localhost:5173` (or similar port)

4. Navigate to the Messages page in the React app (you may need to login first)

## Step 3: Start the Flutter App

1. Open a new terminal and navigate to the flutter_app directory:
   ```bash
   cd flutter_app
   ```

2. Get Flutter dependencies:
   ```bash
   flutter pub get
   ```

3. Run the Flutter app:
   ```bash
   flutter run
   ```

## Step 4: Test the Pipeline

1. In the Flutter app, navigate to the Messages tab (should be the 4th tab in the bottom navigation)
2. Enter a test message like "Hello from Flutter app!"
3. Tap "Send Message"
4. You should see a success message in the Flutter app
5. Switch to the React website and navigate to the Messages page
6. You should see your message appear there within 5 seconds (auto-refresh)

## Expected Behavior

- ✅ Flutter app can send messages to backend
- ✅ Backend stores messages in memory
- ✅ React website displays messages in real-time
- ✅ Messages include timestamp
- ✅ Auto-refresh every 5 seconds in React app

## Troubleshooting

### Backend Issues
- Make sure port 3000 is not in use by another application
- Check that all dependencies are installed with `npm install`

### Flutter Issues
- Ensure Flutter SDK is properly installed
- Run `flutter doctor` to check for issues
- **IMPORTANT**: Flutter apps cannot access `localhost` from devices/emulators
- Use your computer's IP address instead: `http://10.30.243.189:3000`

### React Issues
- Check that the development server is running
- Ensure you're accessing the correct port
- Check browser console for any CORS errors

### Network Issues
- **SOLUTION**: The Flutter app and React app are configured to use IP address `10.30.243.189:3000`
- If your IP address changes, update both:
  - `flutter_app/lib/services/message_service.dart` (line 5)
  - `civic/src/pages/Messages.jsx` (line 15)
- Make sure all three services are running simultaneously

## API Endpoints

The backend provides these endpoints:
- `GET /api/messages` - Retrieve all messages
- `POST /api/messages` - Send a new message

## File Structure

```
├── backend/
│   ├── server.js          # Express server with message API
│   └── package.json       # Backend dependencies
├── flutter_app/
│   ├── lib/
│   │   ├── services/
│   │   │   └── message_service.dart  # HTTP client for backend
│   │   ├── message_screen.dart      # UI for sending messages
│   │   └── instagram_navigation.dart # Updated navigation
│   └── pubspec.yaml       # Flutter dependencies
└── civic/
    ├── src/
    │   ├── pages/
    │   │   └── Messages.jsx         # React page for displaying messages
    │   ├── components/
    │   │   └── Sidebar.jsx          # Updated navigation
    │   └── App.jsx                  # Updated routing
    └── package.json       # React dependencies
```
