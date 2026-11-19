# Setup Instructions

## Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.10+ (for backend)
- **Git** (for version control)

## Method 1: Local Development Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Regginear/IAMShield-AI.git
cd IAMShield-AI
```

### 2. Database Setup

SQLite is the default database. The backend creates `backend/iamshield.db`
and its tables automatically on startup; no database server is required.

### 3. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: create a .env file for SECRET_KEY and CORS settings
copy .env.example .env

# Run migrations (if any)
# (Will be implemented)

# Start the server
python -m uvicorn app.main:app --reload
```

The backend will be running at `http://localhost:8000`
- API Documentation: `http://localhost:8000/api/docs`
- Alternative Docs: `http://localhost:8000/api/redoc`

### 4. Frontend Setup

```bash
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be running at `http://localhost:5173`

## Environment Configuration

### Backend (.env file)

Copy `.env.example` to `.env` and configure:

```env
DATABASE_URL=sqlite:///./iamshield.db
SECRET_KEY=replace-with-a-long-random-value
DEBUG=False
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Verification

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "IAMShield AI",
  "version": "1.0.0"
}
```

### 2. Check API Documentation
Visit `http://localhost:8000/api/docs` in your browser

### 3. Check Frontend
Visit `http://localhost:5173` in your browser

## Development Workflow

### Backend Development
1. Activate virtual environment
2. Make changes to files in `backend/app/`
3. The server reloads automatically (with `--reload`)
4. Check API docs at `http://localhost:8000/api/docs`

### Frontend Development
1. Files in `frontend/src/` auto-reload
2. Open browser DevTools (F12) to check for errors
3. Use Tailwind CSS classes for styling

## Troubleshooting

### Database Connection Error
- Check that `DATABASE_URL` points to a writable SQLite path.
- Delete `backend/iamshield.db` only when you intentionally want a fresh demo database.

### Port Already in Use
```bash
# Change ports in docker-compose.yml or:
# Kill process using port
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

### Import Errors in Backend
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Node Modules Issues
```bash
# Clear and reinstall
rm -rf frontend/node_modules
npm cache clean --force
npm install
```

## Next Steps

1. Review the [API Documentation](API.md)
2. Check the [Database Schema](DATABASE.md)
3. Read the [Architecture Guide](ARCHITECTURE.md)
4. Start developing!

---

**Last Updated**: 2026-11-19
