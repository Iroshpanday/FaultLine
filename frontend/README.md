# Faultline frontend

Customer chat page for the Faultline store agent (Next.js 16, TypeScript, Tailwind).

The browser only talks to this app. Requests to `/api/*` are proxied to the
Django backend (see `next.config.ts`), so no CORS setup is needed.

## Run locally

1. Start the backend first (from `backend/`):

   ```bash
   python manage.py seed_demo   # fake demo store and orders
   python manage.py runserver   # http://127.0.0.1:8000
   ```

2. Start the frontend (from `frontend/`):

   ```bash
   npm install
   npm run dev                  # http://localhost:3000
   ```

To point at a different backend, set `BACKEND_URL` (default `http://127.0.0.1:8000`).

## Checks

```bash
npx tsc --noEmit
npm run lint
npm run build
```
