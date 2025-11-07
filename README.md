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
npm start
```

Then:

- Press `w` to open in web browser
- Press `a` to open Android emulator
- Press `i` to open iOS simulator (macOS only)
- Scan QR code with Expo Go app

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

## Configuration

### Environment Variables

**Backend** (`backend/.env` - optional):

```env
PYTHONUNBUFFERED=1
DATABASE_URL=sqlite:///./app.db
SECRET_KEY=your-secret-key
```

**Frontend** (`frontend/.env`):

```env
EXPO_PUBLIC_API_URL=http://localhost:8080
NODE_ENV=development
```

**Note:** Expo env vars must be prefixed with `EXPO_PUBLIC_` to be accessible in client code.

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

### Hot Reload

Both services support hot reload:

- **Backend**: Auto-restarts on Python file changes
- **Frontend**: Instant updates on React/TypeScript changes

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

## Troubleshooting

### Backend Issues

**Poetry not found:**

```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -
# Add to PATH (~/.zshrc or ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
```

**Dependencies won't install:**

```bash
cd backend
poetry self update
poetry cache clear pypi --all
poetry install
```

**Import errors:**

- Make sure you're in the Poetry virtual environment: `poetry shell`

### Frontend Issues

**Node modules issues:**

```bash
cd frontend
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

**Metro bundler cache:**

```bash
cd frontend
npm start -- --reset-cache
```

**Port conflicts:**

- Backend: Change port in `start.sh` or uvicorn command
- Frontend: Expo will suggest an alternative port automatically

## Resources

- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Expo Docs](https://docs.expo.dev/)
- [Poetry Docs](https://python-poetry.org/docs/)
