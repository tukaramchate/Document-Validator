# Document-Validator

A full-stack AI-powered document validation application that verifies whether documents are real or fake based on multiple validation points.

## Overview

This is a final year project that uses AI for document validation combined with database verification. The system analyzes documents using CNN, OCR, and various validation techniques to determine authenticity.

## Project Structure

```
Document-Validator/
├── frontend/          # React.js frontend with Vite
├── backend/           # Python Flask backend
└── AI Model/          # Machine Learning models (CNN, OCR)
```

## Tech Stack

**Frontend:**
- React.js with Vite
- Tailwind CSS for styling
- Axios for API calls
- React Router for routing
- Recharts for data visualization
- JWT authentication
- HTML5 file upload

**Backend:**
- Python Flask
- Flask-CORS
- JWT authentication
- File upload handling

**AI/ML:**
- CNN (Convolutional Neural Networks)
- OCR (Optical Character Recognition)
- Document analysis algorithms

## Setup Instructions

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Create a `.env` file based on `.env.example`:
```
VITE_API_URL=http://localhost:5000/api
```

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Create a `.env` file based on `.env.example`:
```
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here
```

The backend runs on `http://localhost:5000`

### AI Model Setup

```bash
cd "AI Model"
pip install -r requirements.txt
```

## Getting Started

1. **Start Backend:**
   ```bash
   cd backend
   python app.py
   ```

2. **Start Frontend:**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access Application:**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:5000/api

## Features

- Document upload and validation
- AI-powered authenticity detection using CNN
- OCR for text extraction and verification
- User authentication with JWT
- Real-time data visualization
- Database cross-verification
- Responsive design with Tailwind CSS

## How It Works

1. User uploads a document through the React frontend
2. Document is sent to Flask backend for processing
3. AI model (CNN + OCR) analyzes the document
4. Multiple validation points are checked against the database
5. Results are returned showing authenticity score and details
6. Data is visualized using charts for easy understanding

## License

See LICENSE file for details.

