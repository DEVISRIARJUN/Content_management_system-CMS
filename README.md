# NovaCMS &mdash; Modern Visual Content Management System

> **A decoupled, block-based Content Management Engine built with Django REST Framework, MySQL 8, and an interactive Studio Dashboard.**

---

## Architecture Overview

NovaCMS is built on modern decoupled CMS principles. Instead of storing rigid HTML strings in traditional blog tables, NovaCMS structures document layouts into **reorderable, typed JSON blocks** (Headings, Paragraphs, Quotes, Code snippets, Alerts, Images, and Dividers).

```
                        [ Content Creators & Readers ]
                                      │
                                      ▼
               [ Studio Dashboard (Interactive SPA / React) ]
               - Visual Block Builder with Live Split-Preview
               - AI Heuristics & Readability (Flesch Score)
               - Real-Time SEO Analyzer & Search Snippet Preview
               - Media Library & S3 Presigned Uploads
               - Document Revision Rollback Engine
                                      │
                                      ▼ REST API (JWT/Token Auth)
                       [ Django REST Framework Core ]
                                      │
              ┌───────────────────────┴───────────────────────┐
              ▼                                               ▼
      [ Database Layer ]                             [ Storage & Cache ]
   - MySQL 8 (JSON columns & UTF8mb4)             - Local & AWS S3 Presigned Uploads
   - Auto-failover to SQLite for zero-friction    - Redis Cache-Aside Layer
```

---

## Key Features

1. **Visual Block Builder (JSON Schema)**
   - Reorderable component blocks: Heading, Paragraph, Code, Quote, Alert, and Image.
   - Saves clean block arrays in `blocks_data` JSONField and pre-renders `content_html` for lightning-fast public delivery.

2. **Embedded AI Writing Heuristics**
   - **Readability Meter**: Real-time Flesch Reading Ease algorithm calculation ($0\text{--}100$) evaluating sentence lengths and syllable counts.
   - **SEO Health Scorer**: Analyzes title length, meta description character count, and keyword density with Google search preview simulation.
   - **Smart Tag & Topic Suggester**: Evaluates text contents and extracts topical taxonomies.
   - **Auto-Summarizer**: Compiles key sentences into a 2-sentence social share excerpt.

3. **Document Versioning & One-Click Rollback**
   - Every significant edit automatically creates a snapshot in `PostRevision`.
   - Authors and editors can inspect historical snapshots and restore any prior version with one click.

4. **Media Management & AWS S3 Presigned Support**
   - Supports local uploads and S3 presigned URLs (`/api/media/presigned-url/`), enabling browsers to upload files directly into AWS S3 buckets without exhausting application server bandwidth.

5. **Traffic Telemetry & Analytics Dashboard**
   - Tracks real-time page views, 7-day traffic velocity with Chart.js, category distribution, and average read-time metrics.

6. **Dual Database Support with Graceful Failover**
   - Configured for **MySQL 8** using `pymysql`.
   - If MySQL credentials need configuration or if the MySQL server is temporarily offline, it automatically falls back to an embedded SQLite database (`db.sqlite3`) so the application **never crashes on launch**.

---

## Project Structure

```text
New_project/
├── run.bat                     # Windows one-click start script
├── README.md                   # Complete architectural guide
├── backend/                    # Django REST Framework application
│   ├── manage.py               # Django CLI utility
│   ├── requirements.txt        # Frozen Python dependencies
│   ├── seed_data.py            # Initial database seeder script
│   ├── setup_mysql.py          # MySQL connection diagnostic tool
│   ├── test_api.py             # End-to-end API integration tests
│   ├── .env                    # Environment configuration
│   ├── .env.example            # Environment template
│   ├── config/                 # Project configuration
│   │   ├── settings.py         # Database, CORS, and REST settings
│   │   ├── urls.py             # Route registry & SPA fallback
│   │   └── wsgi.py
│   ├── apps/
│   │   ├── accounts/           # User authentication & RBAC roles
│   │   ├── posts/              # Block-based posts, categories, revisions
│   │   ├── media_manager/      # File uploads & S3 presigned tokens
│   │   ├── analytics/          # Traffic logs & dashboard aggregations
│   │   └── ai_assistant/       # Readability, SEO, and NLP helpers
│   └── templates/
│       └── index.html          # High-performance Studio Dashboard (Tailwind + Lucide)
└── frontend/                   # Decoupled React 19 + Vite frontend project
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx             # React dashboard component
        └── services/api.js     # API client functions
```

---

## Quickstart Guide

### Option 1: One-Click Launch (Windows)
Double-click `run.bat` in the project root.

### Option 2: Command Line Launch
```bash
# 1. Navigate to backend directory
cd backend

# 2. Run migrations
python manage.py migrate

# 3. Seed initial demo data (optional, already seeded)
python seed_data.py

# 4. Start the server
python manage.py runserver 127.0.0.1:8000
```

Open your browser and visit:
* **Studio Dashboard**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
* **REST API Root**: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

### Default Accounts
* **Superuser**: `admin` / `admin123`
* **Author / Editor**: `sarah_dev` / `author123`

---

## Configuring MySQL

1. Open `backend/.env`.
2. Update your credentials:
   ```env
   DB_ENGINE=mysql
   DB_NAME=cms_db
   DB_USER=root
   DB_PASSWORD=your_mysql_password
   DB_HOST=127.0.0.1
   DB_PORT=3306
   ```
3. Run the diagnostic script:
   ```bash
   python backend/setup_mysql.py
   ```
4. Run migrations:
   ```bash
   python backend/manage.py migrate
   python backend/seed_data.py
   ```

---

## Running Integration Tests

To verify all REST endpoints and AI heuristics:
```bash
cd backend
python test_api.py
```
Expected output:
```text
[ALL TESTS PASSED SUCCESSFULLY!]
```
