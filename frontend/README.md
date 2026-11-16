# Faultline frontend

Demo storefront for **Momo Mart**, a momo kitchen in Lalitpur, with an AI **order help** chat
(Next.js 16, TypeScript).

Shoppers enter the email they used at checkout, then ask about their orders. The assistant
only ever sees orders placed with that email.

- Demo email: `demo.customer@example.com` (orders #123 to #126)
- A second shopper, `sita.sharma@example.com`, owns #127, so the demo can show that one
  customer can't see another's order.
- `http://localhost:3000/#order-help` opens the chat straight away.

## How the page is built

- **Design system:** [tasteskill](https://github.com/Leonxlnx/taste-skill) (MIT), copied
  unchanged into `public/assets` (CSS, motion layer, layout script and two scroll moments).
  The page in `app/page.tsx` uses its markup and classes; `app/kit-scripts.tsx` loads its
  scripts after React hydrates, so React and the kit never fight over the DOM.
- **Scroll moments:** a statement whose words light up as you scroll (`word-highlight`), and
  a pinned photo story where each photograph replaces the last (`photo-chapters`).
- **The chat** (`app/chat-widget.tsx`) is our own React component, styled in `app/globals.css`
  with the design system's tokens.
- **Photographs** are licensed stand-ins from Wikimedia Commons, listed on `/credits`.
  Hours and prices are made up for the demo and marked `data-assumed` in the markup.

The browser only talks to this app. Requests to `/api/*` are proxied to the Django backend
(see `next.config.ts`), so no CORS setup is needed.

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
