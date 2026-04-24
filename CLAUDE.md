# Wayfare API — Claude Code session context

## Project
- Django 5 + DRF backend for Wayfare, a geotagged storytelling app (React/Vite client lives in a sibling repo).
- Stack: Django, DRF (Token auth), Cloudinary for media, django-cors-headers.
- DB: SQLite in dev (`db.sqlite3`, gitignored). Postgres env vars (`DB_ENGINE`, `DB_NAME`, `DB_USER`, etc.) are wired in `wayfareproject/settings.py` but unused locally.
- Single app: `wayfareapi/` (models, views, migrations, fixtures).

## Running locally
- Venv: `source .venv/bin/activate` (Python 3.12).
- Install deps: `pip install -r requirements.txt` — `requirements.txt` is the working manifest today (pyproject.toml is missing runtime packages). Consolidation unresolved, see FOLLOWUPS.md.
- `.env` must set `SECRET_KEY` (settings.py raises if missing) plus the three `CLOUDINARY_*` vars.
- Migrate: `python manage.py migrate`.
- Seed demo data: `./seed_database.sh` — **destructive**: removes `db.sqlite3` and `wayfareapi/migrations/` before re-running migrate + loaddata. Dev only.
- Run: `python manage.py runserver` (default port 8000; CORS whitelist includes 3000/5173).

## Architecture notes
- `Traveler` has `OneToOneField(User)` (not `username`/`name`). All ORM filters on user data must traverse `traveler__user__*` (e.g. `traveler__user__username`, `traveler__user__first_name`).
- `post_save` signal on `User` auto-creates a `Traveler` row (`wayfareapi/models/traveler.py`). Don't create Travelers manually in register flow.
- Nested comments: `Comment.parent` is a self-FK (migration `0003_comment_add_parent.py`). `PostSerializer.comments` returns only top-level comments, each with a nested `replies` array, prefetched.
- Pagination: global `PageNumberPagination` with `page_size=20` in `REST_FRAMEWORK` settings. Applies to any viewset using default `list()`. `PostViewSet.list` overrides `list()` and does NOT call `paginate_queryset` — it still returns a raw array. Known, tracked in FOLLOWUPS.md.
- Serializers live inline in `wayfareapi/views/*.py` (no `serializers.py` module). Known layout quirk.

## Conventions
- `/likes`, `/bookmarks`, `/comments` list endpoints are user-scoped via `get_queryset()` filtering on `traveler__user=self.request.user`. **Don't remove that filter** — it was added to close a data leak.
- Post detail comments are served via `PostSerializer.comments` (nested on `/posts/:id`), NOT via the `/comments` list endpoint. Keep that split; the list endpoint is for "my comments" only.
- Ownership checks on mutating endpoints use inline `if obj.traveler.user != request.user: 403`. Duplicated across viewsets — refactor to a permission class is out of scope unless asked.
- Don't touch `wayfareapi/migrations/0003_comment_add_parent.py` or any earlier migrations.
- Cloudinary secrets live in `.env` (not tracked). Don't commit `.env`.

## Known tech debt
See [FOLLOWUPS.md](FOLLOWUPS.md). Don't duplicate here.

## Out of scope without asking
- Python dep manifest consolidation (5 overlapping: Pipfile, Pipfile.lock, pyproject.toml, poetry.lock, requirements.txt). Unresolved.
- Writing tests. `wayfareapi/tests.py` is empty boilerplate; no test infra decision yet.
- Auth system changes. DRF TokenAuthentication is intentional for now — no JWT/session migration.
