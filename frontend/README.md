# Frontend

React 19 + Vite + TypeScript SPA. Served as static files from an internal nginx image; routed through the gateway nginx at `/`.

## Tech Stack

- **Framework**: React 19, React Router v7.
- **Build**: Vite 7 + `@vitejs/plugin-react-swc`.
- **Language**: TypeScript 5.8 with `noUnusedLocals` / `noUnusedParameters`.
- **UI**: shadcn/ui (Radix primitives) + Tailwind CSS v4 via `@tailwindcss/vite`.
- **State**: React Context (`AuthContext`) + local component state. No global store.
- **Forms**: react-hook-form + Zod.
- **Data fetching**: Axios (single client at `src/lib/api/clientApi.ts`).
- **Video**: HLS.js with native Safari fallback (`<video canPlayType …>`).
- **Toasts**: `sonner` (mounted globally in `main.tsx`).
- **Testing**: Vitest + Testing Library (setup wired; tests still thin).

## Project layout

```
src/
├── components/      shadcn UI primitives + app components (VideoCard, VideoPlayer, …)
├── contexts/        AuthContext + useAuth hook
├── hooks/           useVideos, useReactions, useCategories, useSearch, useDownload
├── layouts/         AppLayout wrapping protected pages
├── lib/api/         per-domain API modules (auth, video, comment, search, …)
├── pages/           20+ lazy-loaded routes
├── routes/          AppRouter.tsx (single entry)
└── utils/           error.ts, timeAgo.ts
```

## API client

`clientApi.ts`:

- `baseURL = import.meta.env.VITE_API_BASE_URL ?? ""` — same-origin by default (works behind the nginx gateway in every env without an env file). Set `VITE_API_BASE_URL` only when running `vite dev` on `:5173` against bff on `:8000`.
- Attaches `Authorization: Bearer <token>` from `localStorage`.
- Response interceptor:
  - Parses the backend error envelope into `{ title, description, fieldIssues }`.
  - Toasts via `sonner.toast.error(...)` unless the call passes `{ silent: true }` (used by boot-time `/api/auth/me`).
  - On 401 outside auth pages: clears token, toasts "Session expired", redirects to `/login?next=<original-path>`.
  - Logs an expandable console group with URL/method/status/body/request-id and a materialized FormData preview — Chrome otherwise prints `FormData {}`.

`utils/error.ts → parseApiError(err)` handles three FastAPI shapes:

- This project's custom envelope: `{ status, code, message, errors[] }`.
- FastAPI default Pydantic 422: `{ detail: [{ loc, msg, type }] }`.
- Plain Axios `Error` / network failure.

## Routes

Public: `/`, `/watch?v=:id`, `/channel/:name`, `/search-results`, `/changelog`, `/pricing-table`, `/login`, `/register`, `/forgotpass`, `/reset-password`, `/auth/callback`.

Protected (via `ProtectedRoute`): `/upload`, `/profile`, `/your-videos`, `/studio`, `/playlists`, `/subscriptions`, `/liked`, `/watch-later`, `/history`.

### Notable pages

- **Studio**: 4-tab dashboard — Overview / Content / Audience / Comments. Comments tab is creator moderation (lists comments on the current user's videos, delete via `DELETE /api/comments/{id}`).
- **YourVideos**: list with multi-select + bulk actions (Make public / Make private / Delete). Optimistic local updates avoid refetch round-trips.
- **Watch**: HLS.js player + comment thread; comments shape mapped via `ApiCommentRaw → VideoComment` with a typed mapper (no `any`).

## Scripts

```bash
npm install      # one-time
npm run dev      # vite dev on :5173 (proxied through compose nginx on :80 in dev)
npm run build    # production build → dist/
npm run lint     # eslint --max-warnings=0
npm test         # vitest
```

## Env vars

| Var                 | Default            | When to set                                                          |
| ------------------- | ------------------ | -------------------------------------------------------------------- |
| `VITE_API_BASE_URL` | `""` (same-origin) | Only when frontend dev server is on a different origin than the API. |

Copy `frontend/.env.example` to `frontend/.env` if you need overrides.

## Image

The container build is two-stage:

1. `node:20-alpine` builds the static bundle with `npm ci --prefer-offline` (cached via BuildKit `--mount=type=cache`).
2. `nginx:1.27-alpine` serves `dist/` on port 8001 with SPA fallback (`try_files $uri /index.html`).

Final runtime image: ~25 MB.
