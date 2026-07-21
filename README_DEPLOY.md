# Deploying AI Twist

This repo includes a Flask backend (`server.py`) and a Vite React frontend in `src/`.

## Deploy options

### Render / Heroku / any container platform
1. Use the existing `Dockerfile`.
2. Build and run the container:
```bash
docker build -t ai-twist .
docker run -p 3000:3000 ai-twist
```

### Heroku
1. Ensure `Procfile` is present.
2. Push to Heroku Git remote.
3. Deploy from the `main` branch.

### GitHub Codespaces / GitHub Container Registry
- The `Dockerfile` is ready to build the full app.

## Important notes
- The app serves the static React build from `dist/`.
- The backend port is `3000`.
- If using Render, set the health check path to `/api/health`.
