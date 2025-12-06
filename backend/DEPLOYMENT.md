# TaskCLI Deployment Guide
==========================

TaskCLI is a task management application with two interfaces:
1. **Web Application** - HTML/CSS/JS frontend with Django backend
2. **CLI Interface** - Interactive terminal-based task manager

Both share the **same SQLite database**, ensuring data consistency.

---

## Option 1: Deploy Web App Only (Recommended for Beginners)

### A) Deploy to Railway (Free Tier)

1. **Install Railway CLI**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

2. **Prepare for Deployment**
   ```bash
   cd /Users/ishitatiwari/Desktop/ojt-v2/taskcli_backend
   
   # Create Procfile
   echo "web: gunicorn taskcli.wsgi --log-file -" > Procfile
   
   # Update requirements.txt
   echo "Django>=4.0
   gunicorn
   whitenoise" > requirements.txt
   ```

3. **Add WhiteNoise for static files** in `taskcli/settings.py`:
   ```python
   MIDDLEWARE = [
       'django.middleware.security.SecurityMiddleware',
       'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
       ...
   ]
   
   STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
   ```

4. **Deploy**
   ```bash
   railway init
   railway up
   ```

5. **Set Environment Variables** (in Railway dashboard):
   ```
   DJANGO_SECRET_KEY=your-secure-key
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=your-app.railway.app
   DJANGO_CSRF_TRUSTED_ORIGINS=https://your-app.railway.app
   ```

---

### B) Deploy to Render (Free Tier)

1. Push code to GitHub
2. Go to [render.com](https://render.com) and create a new Web Service
3. Connect your GitHub repo
4. Set build command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
5. Set start command: `gunicorn taskcli.wsgi`
6. Add environment variables as above

---

### C) Deploy to Vercel (Serverless)

You already have a `vercel.json` file. Just run:
```bash
cd /Users/ishitatiwari/Desktop/ojt-v2/taskcli_backend
vercel --prod
```

**Note:** Vercel is serverless, so SQLite won't persist between deployments. Use PostgreSQL for production.

---

## Option 2: Deploy with PostgreSQL (Production)

For production, replace SQLite with PostgreSQL:

1. **Install psycopg2**
   ```bash
   pip install psycopg2-binary dj-database-url
   ```

2. **Update settings.py**
   ```python
   import dj_database_url
   
   DATABASES = {
       'default': dj_database_url.config(
           default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}"
       )
   }
   ```

3. **Set DATABASE_URL** environment variable:
   ```
   DATABASE_URL=postgresql://user:pass@host:5432/dbname
   ```

---

## Option 3: CLI Distribution (PyPI)

Since CLI uses Django ORM, it needs a running database. Options:

### A) CLI as Part of Deployed App

Users can SSH into the server and run:
```bash
python manage.py task_cli
```

### B) Create Standalone CLI with API

For a truly standalone CLI (PyPI distribution), you need to:

1. **Create a REST API** in Django:
   ```python
   # accounts/views.py - Add API endpoints
   from django.http import JsonResponse
   
   def api_list_tasks(request):
       tasks = Task.objects.filter(user=request.user)
       return JsonResponse({'tasks': list(tasks.values())})
   ```

2. **Create a separate CLI package** that calls the API:
   ```python
   # taskcli_cli/main.py
   import requests
   
   API_URL = "https://your-deployed-app.com/api"
   
   def list_tasks():
       response = requests.get(f"{API_URL}/tasks/")
       return response.json()
   ```

3. **Publish to PyPI**:
   ```bash
   pip install build twine
   python -m build
   twine upload dist/*
   ```

---

## Recommended Architecture for Your Project

```
┌─────────────────────────────────────────────────────────────┐
│                      PRODUCTION SETUP                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   ┌──────────────┐         ┌──────────────────────┐         │
│   │  Web App     │         │  PostgreSQL DB       │         │
│   │  (Railway/   │◄───────►│  (Railway/Render     │         │
│   │   Render)    │         │   or Supabase)       │         │
│   └──────────────┘         └──────────────────────┘         │
│          ▲                           ▲                       │
│          │                           │                       │
│   ┌──────┴──────┐           ┌────────┴────────┐             │
│   │   Browser   │           │  CLI (via SSH   │             │
│   │   Users     │           │  or API calls)  │             │
│   └─────────────┘           └─────────────────┘             │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Quick Start Deployment Checklist

- [ ] Update `requirements.txt` with all dependencies
- [ ] Set `DEBUG=False` in production
- [ ] Generate a secure `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`
- [ ] Run `python manage.py collectstatic`
- [ ] Set up PostgreSQL for production (optional but recommended)
- [ ] Deploy to Railway, Render, or Vercel

---

## Environment Variables Reference

| Variable | Example | Description |
|----------|---------|-------------|
| `DJANGO_SECRET_KEY` | `abc123...` | Secret key for Django |
| `DJANGO_DEBUG` | `False` | Debug mode (False in production) |
| `DJANGO_ALLOWED_HOSTS` | `myapp.com` | Comma-separated hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `https://myapp.com` | CSRF origins |
| `DATABASE_URL` | `postgresql://...` | Database connection URL |

---

## Need Help?

- [Django Deployment Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
