# SkateMap

SkateMap is a backend API for a web app that lets skateboarders discover and share street skate spots. Built with FastAPI and PostgreSQL.

---

## Features

- Browse all skate spots
- Add a spot with a name, description, and coordinates
- Upload and delete images for a spot (deleting removes the file from disk)
- Spot locations sourced from OpenStreetMap
- Bounding box queries for loading spots visible on a map viewport

---

## Tech Stack

- **FastAPI** — API framework with automatic OpenAPI docs
- **PostgreSQL** — primary database
- **SQLAlchemy 2.x** — ORM with typed mapped columns
- **Pydantic v2** — request/response validation and settings management
- **Uvicorn** — ASGI server
- **pytest** — test suite with a dedicated PostgreSQL test database

See [`docs/architecture.md`](docs/architecture.md) for a full breakdown of the project structure, layer diagram, request lifecycle, and data model.

---

## Local Setup

### Prerequisites

- Python 3.11+
- PostgreSQL 16

### 1. Install PostgreSQL

#### Windows — Installer (includes pgAdmin UI)

1. Download the installer from [postgresql.org/download/windows](https://www.postgresql.org/download/windows/)
2. Run the installer. When prompted, set a password for the `postgres` user — note it down, you'll need it for `.env`
3. The installer includes **pgAdmin 4**, a browser-based GUI for managing databases
4. PostgreSQL runs as a Windows service automatically after install

#### macOS — Postgres.app (GUI, recommended)

1. Download from [postgresapp.com](https://postgresapp.com/)
2. Move it to Applications and open it
3. Click **Initialize** to create a local server, then **Start**
4. Postgres.app lives in your menu bar and starts automatically at login
5. It creates a default superuser matching your macOS username with no password

To also get the CLI tools (`psql`, `createdb`) on your PATH, follow the instructions on the Postgres.app site (adds `/Applications/Postgres.app/Contents/Versions/latest/bin` to your shell profile).

#### macOS — Homebrew (CLI)

```bash
brew install postgresql@16
brew services start postgresql@16
```

---

### 2. Create the databases

You need two databases: one for the app and one for tests.

#### Using pgAdmin (Windows / any platform)

1. Open pgAdmin and connect to your local server
2. Right-click **Databases** → **Create** → **Database**
3. Name it `skatemap_db`, save
4. Repeat for `skatemap_test_db`

#### Using Postgres.app (macOS)

Click the **Open psql** button in the Postgres.app window, then run:

```sql
CREATE DATABASE skatemap_db;
CREATE DATABASE skatemap_test_db;
```

#### Using the CLI

**Windows** (run in Command Prompt or PowerShell):
```cmd
psql -U postgres -c "CREATE DATABASE skatemap_db;"
psql -U postgres -c "CREATE DATABASE skatemap_test_db;"
```

**macOS (Homebrew)** — Homebrew creates a superuser matching your macOS username, so first create a `postgres` role:
```bash
psql -U $(whoami) postgres -c "CREATE USER postgres WITH PASSWORD 'yourpassword' SUPERUSER;"
createdb -U postgres skatemap_db
createdb -U postgres skatemap_test_db
```

---

### 3. Install Python dependencies

```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Configure

Create a `.env` file at the project root:

```
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=skatemap_db
```

Set `POSTGRES_PASSWORD` to whatever you chose during install (or in step 2 for Homebrew).

### 5. Run

```bash
python run.py
```

Tables are created automatically on first run via SQLAlchemy's `create_all`. The Swagger UI is at `http://127.0.0.1:8000/docs`.

---

## Running Tests

The test database (`skatemap_test_db`) was created in the setup above. Tables are created and dropped around each test for full isolation — no manual schema management needed.

```bash
pytest
```

---

### Docker

Make sure Docker Desktop is running, then from the project root:

**Start everything (app + database):**
```bash
docker compose up -d
```

**Rebuild after code or dependency changes:**
```bash
docker compose up -d --build
```

**Run the tests:**
```bash
docker compose run --rm -e MODE=test app
```

**View logs:**
```bash
docker compose logs app
```

**Stop everything:**
```bash
docker compose down
```

The database and test database are created automatically on first run. Tables are created on app startup via SQLAlchemy's `create_all`.

---

## API

Full interactive documentation is available at `/docs` once the server is running. A static OpenAPI schema is at `/openapi.json`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/spots/` | List all spots |
| POST | `/spots/` | Create a spot |
| GET | `/spots/{id}` | Get a spot by ID |
| GET | `/spots/{id}/images` | List images for a spot |
| POST | `/spots/{id}/images` | Upload an image to a spot |
| DELETE | `/spots/{id}/images/{image_id}` | Delete an image (also removes file from disk) |
