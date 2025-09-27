# Node.js Backend Test

This is a Node.js version of the backend API for testing purposes.

## Setup

1. Install dependencies:
```bash
npm install
```

2. Create `.env` file:
```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your-password
DB_NAME=civic_complaints
PORT=3000
```

3. Start the server:
```bash
npm start
```

## API Endpoints

- `GET /` - Health check
- `GET /api/complaints` - Get all complaints
- `POST /api/complaints` - Create a new complaint
- `GET /api/complaints/stats` - Get complaint statistics

## Testing

Run tests:
```bash
npm test
```

## Development

Start with auto-reload:
```bash
npm run dev
```
