# Django Polls App & REST API

A full-stack Django polling application featuring a fast, self-contained **Bootstrap 5** and **HTMX** frontend alongside a **Django REST Framework (DRF)** API. Built on top of the official Django tutorial and extended with interactive partial page swaps, local static assets, repeatable database fixtures, and automated test coverage.

## Features

- **Modern, Self-Contained UI:** Styled with Bootstrap 5.3 and powered by HTMX 2.0 served locally from `polls/static/polls/`—zero external CDN dependencies and instant page loads.
- **Interactive Voting:** Submits votes and displays validation errors or animated progress bar results via HTMX partial swaps (`_detail_form_partial.html` and `_results_partial.html`) without full-page reloads, with standard HTTP redirects as a fallback.
- **RESTful API:** Separate `api` app built with Django REST Framework (`DefaultRouter`, `QuestionViewSet`, and `ChoiceViewSet`) supporting CRUD operations and custom voting actions.
- **Repeatable Test Data:** Includes a pre-configured `polls_seed.json` fixture and a custom `reset_polls` management command that wipes poll records, resets SQLite auto-increment sequences, and reloads seed data without deleting admin superusers.
- **Automated Test Suite:** Comprehensive unit and integration tests covering models, standard views, HTMX partial responses, and DRF endpoints.

## Tech Stack

- **Backend:** Python 3.13, Django, Django REST Framework
- **Frontend:** Bootstrap 5.3 (local), HTMX 2.0 (local)
- **Database:** SQLite (`db.sqlite3`)
- **Package & Environment Management:** `uv`

## Project Structure

```text
django-tutorial/
├── README.md
├── api/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations/
│   │   └── __init__.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── mysite/
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── polls/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── fixtures/
│   │   └── polls_seed.json
│   ├── management/
│   │   ├── __init__.py
│   │   └── commands/
│   │       ├── __init__.py
│   │       └── reset_polls.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   └── __init__.py
│   ├── models.py
│   ├── static/
│   │   └── polls/
│   │       ├── css/
│   │       │   └── bootstrap.min.css
│   │       └── js/
│   │           ├── bootstrap.bundle.min.js
│   │           └── htmx.min.js
│   ├── templates/
│   │   └── polls/
│   │       ├── _detail_form_partial.html
│   │       ├── _results_partial.html
│   │       ├── base.html
│   │       ├── detail.html
│   │       ├── index.html
│   │       └── results.html
│   ├── tests/
│   │   ├── __init__.py
│   │   └── test_views_and_models.py
│   ├── urls.py
│   └── views.py
├── pyproject.toml
├── templates/
│   └── admin/
│       └── base_site.html
└── uv.lock
```

## Getting Started

### Prerequisites

- Python 3.13+
- [`uv`](https://docs.astral.sh/uv/) installed

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd django-tutorial
   ```

2. **Install dependencies with `uv`:**
   ```bash
   uv sync
   ```

3. **Apply database migrations:**
   ```bash
   uv run manage.py migrate
   ```

4. **Load the initial seed data:**
   ```bash
   uv run manage.py loaddata polls_seed.json
   ```

5. **(Optional) Create an admin superuser:**
   ```bash
   uv run manage.py createsuperuser
   ```

6. **Start the development server:**

   Settings default to production (`DEBUG` off, secret key required), so turn on development mode explicitly:
   ```bash
   cp .env.example .env      # then set DJANGO_DEBUG=True
   uv run --env-file .env manage.py runserver
   ```

Visit **`http://127.0.0.1:8000/polls/`** for the web interface or **`http://127.0.0.1:8000/api/`** for the browsable REST API.

## Useful Commands

### Resetting Poll Data
To clear all existing questions and choices, reset SQLite's `sqlite_sequence` auto-increment counters, and reload `polls_seed.json` while preserving your admin user accounts:
```bash
uv run manage.py reset_polls
```

### Running Tests
Run the full test suite (models, standard views, HTMX partial responses, and REST API endpoints):
```bash
uv run manage.py test -v 2
```

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/questions/` | List all poll questions |
| `POST` | `/api/questions/` | Create a new poll question |
| `GET` | `/api/questions/<id>/` | Retrieve a specific question |
| `GET` | `/api/choices/` | List all choices |
| `POST` | `/api/choices/<id>/vote/` | Increment the vote count for a specific choice |

Reads and voting are public. Creating, updating and deleting questions or choices requires a logged-in user. `votes` is read-only except through the vote action.

## Deployment

```bash
cp .env.example .env    # set a real DJANGO_SECRET_KEY and your host name
docker compose up -d --build
```

The `web` container applies migrations and seeds demo data on first boot; Caddy proxies to Gunicorn.

