# Vue 3 + TypeScript Migration Guide

This document describes the migration of the web interface from simple HTML templates to a modern Vue 3 + TypeScript stack.

## What Changed

### Frontend Architecture
- **Old**: Simple HTML template wrapper (`templates/report_wrapper.html`) that displayed generated HTML reports
- **New**: Full Vue 3 + TypeScript SPA with Vite build system, component-based architecture, and modern styling with Pico CSS

### Backend Changes
- **New API Endpoints**:
  - `GET /api/grib-files` - Lists all GRIB files with metadata
  - `GET /api/latest-report/{route_id}` - Public endpoint for fetching forecast reports (no auth required)
- **Static File Serving**: Vue build output served from root path `/`
- **Backward Compatibility**: Legacy `/web/{route_id}` HTML viewer still works

### Deployment
- **Docker**: Multi-stage build now includes Node.js for frontend compilation
- **GitHub Actions**: Updated workflow to build and test frontend before Docker image creation
- **Narduk Cloud**: Automatic deployment on push to main branch (unchanged workflow endpoint)

## Development Workflow

### Local Development

1. **Backend Development**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   uvicorn server.api:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Frontend Development** (in separate terminal):
   ```bash
   cd frontend
   npm install
   npm run dev  # Runs on http://localhost:5173
   ```

   The Vite dev server proxies API requests to the backend at `localhost:8000`.

3. **Access the application**:
   - Vue dev server: http://localhost:5173 (with hot reload)
   - Backend API: http://localhost:8000

### Production Build

```bash
cd frontend
npm run build  # Output to frontend/dist/
cd ..
uvicorn server.api:app --host 0.0.0.0 --port 8000
```

Access at http://localhost:8000

## Docker Deployment

The Dockerfile uses multi-stage builds:

1. **frontend-builder**: Builds Vue app with Node.js 20
2. **python-builder**: Installs Python dependencies
3. **runtime**: Combines both outputs into slim production image

```bash
docker build -t chatgpt-weather .
docker run -p 8000:8000 --env-file .env chatgpt-weather
```

## Narduk Cloud Deployment

The application automatically deploys to Narduk Cloud when:
1. Code is pushed to the `main` branch
2. GitHub Actions workflow builds Docker image
3. Image is pushed to GitHub Container Registry (ghcr.io)
4. Deployment API is called with authentication token

The app will be available at: `https://cloud.nard.uk/app/loganrenz/chatgpt-weather/`

## Testing

### Unit Tests
Currently, there are no unit tests. The workflow runs:
- Python compilation check: `python -m compileall server wx_engine`
- TypeScript compilation: `npm run build` in frontend directory
- CodeQL security scan

### Manual Testing
1. Test forecast viewer with route/model selection
2. Test GRIB file browser (will show empty until GRIB files are downloaded)
3. Test responsive design on mobile devices
4. Verify backward compatibility with `/web/{route_id}` endpoint

## File Structure

```
chatgpt-weather/
├── frontend/                  # Vue 3 + TypeScript frontend
│   ├── src/
│   │   ├── components/        # Vue components
│   │   │   ├── ForecastViewer.vue
│   │   │   └── GribList.vue
│   │   ├── api.ts            # API service layer
│   │   ├── types.ts          # TypeScript type definitions
│   │   ├── App.vue           # Main app component
│   │   ├── main.ts           # App entry point
│   │   └── style.css         # Custom styles
│   ├── dist/                 # Build output (gitignored)
│   ├── package.json          # Node dependencies
│   ├── vite.config.ts        # Vite configuration
│   └── tsconfig.json         # TypeScript configuration
├── server/
│   └── api.py                # FastAPI backend (updated)
├── templates/
│   └── report_wrapper.html   # Legacy HTML wrapper
├── Dockerfile                # Multi-stage build
├── .github/workflows/
│   └── deploy.yml            # CI/CD pipeline (updated)
└── README.md                 # Updated documentation
```

## Migration Benefits

1. **Modern Tech Stack**: Vue 3 with Composition API and TypeScript
2. **Developer Experience**: Hot reload, TypeScript type safety, component reusability
3. **User Experience**: Faster page loads, no full page refreshes, better mobile support
4. **Maintainability**: Component-based architecture, clear separation of concerns
5. **Extensibility**: Easy to add new features like real-time updates, charts, maps

## Security Improvements

- Path traversal protection in static file serving
- Input validation on all API endpoints
- CodeQL security scanning in CI/CD pipeline
- All alerts resolved (0 security vulnerabilities)

## Future Enhancements

Potential improvements for future iterations:
1. Add real-time GRIB data visualization with charts/maps
2. Implement WebSocket for live forecast updates
3. Add user authentication and saved preferences
4. Create mobile PWA with offline support
5. Add automated E2E tests with Playwright
6. Implement GRIB file upload and management UI
