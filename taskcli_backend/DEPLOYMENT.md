# TaskCLI Deployment (Vercel)

These steps explain how to run the **entire project on Vercel**, including the Django backend. Because Vercel’s filesystem is read-only and serverless instances are short-lived, you must rely on external services for state (for example, Vercel Postgres, Neon, Supabase, or Render PostgreSQL). SQLite is not suitable for production on Vercel.

## 1. Prepare the codebase

1. Keep the backend inside `taskcli_backend/`. Vercel will treat this folder as the project root when deploying the backend.
2. Ensure `requirements.txt` lists every Python dependency (already present).
3. The repo now contains `api/index.py`, which bootstraps Django’s WSGI application for Vercel’s Python runtime. If you move files around, update the `BASE_DIR` calculation inside that file.
4. (Optional but recommended) Add `whitenoise` to `INSTALLED_APPS` and `MIDDLEWARE` if you want Django to serve its own static files. Alternatively, upload static assets to Vercel storage or another CDN.

## 2. Configure environment variables

1. Copy the sample file and customise it locally:
   ```bash
   cd /Users/ishitatiwari/Desktop/ojt-v2/taskcli_backend
   cp env.example .env
   ```
2. Fill in the values:
   - `DJANGO_SECRET_KEY`
   - `DJANGO_ALLOWED_HOSTS` (include the Vercel domain, e.g. `your-project.vercel.app`)
   - `DJANGO_CSRF_TRUSTED_ORIGINS` (include `https://your-project.vercel.app`)
   - Database credentials (e.g. `DATABASE_URL`) once you point Django at Postgres.
3. In the Vercel dashboard (Project → Settings → Environment Variables) add the same keys. Vercel injects them at build and runtime.

## 3. Create `vercel.json`

`vercel.json` already lives at the repo root and contains:
```json
{
  "buildCommand": "cd taskcli_backend && pip install -r requirements.txt && python manage.py collectstatic --noinput",
  "functions": {
    "api/index.py": {
      "runtime": "python3.11",
      "maxDuration": 10,
      "memory": 512
    }
  },
  "rewrites": [
    { "source": "/(.*)", "destination": "/api/index.py" }
  ]
}
```
Edit this file if you introduce a dedicated frontend (for example, route `/` to a Next.js build and `/api` to Django).

## 4. Deploy with the Vercel CLI or dashboard

1. Install the CLI once: `npm i -g vercel`.
2. From the repo root run `vercel` (first-time setup) and then `vercel --prod` when you are ready for production.
3. During the prompts select `taskcli_backend` as the root directory, unless you plan to split frontend and backend into different Vercel projects.
4. Confirm the build command if prompted (it should match the `buildCommand` from `vercel.json`), and verify that `outputDirectory` is correct for your static assets.

## 5. Database & migrations

1. Provision a Postgres database (Neon/Supabase/Vercel Postgres/etc.).
2. Update `taskcli_backend/taskcli/settings.py` to read `DATABASE_URL` and configure `dj-database-url` or manual settings.
3. Set the DB URL in Vercel environment variables.
4. Run migrations via `vercel env pull` and `python manage.py migrate` locally against the production database, or use `vercel deploy --prebuilt` with a script that runs migrations on cold start (be cautious to avoid race conditions).

## 6. Frontend alignment

If your frontend stays on Vercel:

- Point its API base URL (e.g. `NEXT_PUBLIC_API_URL`) to the same Vercel deployment that runs Django (`https://your-project.vercel.app/api` by default).
- Redeploy the frontend after changing environment variables.

## 7. Testing & maintenance

- Use `vercel dev` locally to emulate the platform (it will spin up the Python function and serve static files).
- Monitor cold-start time and adjust `maxDuration`/`memory` in `vercel.json` if requests are heavy.
- Keep dependencies in `requirements.txt` up to date and rerun `vercel --prod` whenever you merge backend changes.

