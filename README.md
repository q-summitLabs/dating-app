# Dating App

Full-stack dating application with FastAPI backend and Expo/React Native frontend.

## Quick Start

### Backend

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

Or use the provided script:

```bash
cd backend
./start.sh
```

**Access:**

- API: http://localhost:8080
- API Docs: http://localhost:8080/docs

### Frontend

```bash
cd frontend
npm install
```

Install the Expo CLI if you haven’t already:

```bash
npm install -g expo-cli
```

Start the application using the Expo tunnel (handy for testing on physical devices):

```bash
npx expo start --tunnel
```

Once Metro starts, you can:

- Press `w` to open in the browser
- Press `a` to launch an Android emulator
- Press `i` to launch the iOS simulator (macOS only)
- Scan the QR code with the Expo Go app to run it on your device

## Prerequisites

- **Python 3.10+** & [Poetry](https://python-poetry.org/docs/#installation)
- **Node.js 18+** & npm
- For mobile: Expo CLI, Xcode (iOS) or Android Studio (Android)

## Project Structure

```
dating-app/
├── backend/          # FastAPI backend (Poetry)
│   ├── app/
│   │   └── main.py
│   └── pyproject.toml
└── frontend/         # Expo/React Native frontend
    ├── app/
    └── package.json
```

## Installation

### Backend

1. Install Poetry (if not already installed):

   ```bash
   curl -sSL https://install.python-poetry.org | python3 -
   ```

2. Install dependencies:

   ```bash
   cd backend
   poetry install
   ```

3. Activate virtual environment:
   ```bash
   poetry shell
   ```

### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```

## Development

### Installing Dependencies

**Backend:**

```bash
cd backend
poetry add <package>              # Production
poetry add --group dev <package>  # Development
```

**Frontend:**

```bash
cd frontend
npm install <package>      # Production
npm install -D <package>   # Development
```

### Code Quality

```bash
# Backend
cd backend && poetry run black .    # Format (if installed)
cd backend && poetry run flake8 .   # Lint (if installed)

# Frontend
cd frontend && npm run lint
```

## API Documentation

- **Swagger UI**: http://localhost:8080/docs
- **ReDoc**: http://localhost:8080/redoc

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Expo Docs](https://docs.expo.dev/)
- [Poetry Docs](https://python-poetry.org/docs/)
