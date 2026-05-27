# Architecture

## Stack

| Layer | Technology |
|---|---|
| API framework | FastAPI |
| Data validation | Pydantic v2 |
| ORM | SQLAlchemy 2.x |
| Database | PostgreSQL |
| ASGI server | Uvicorn |
| Configuration | Pydantic Settings (reads from `.env`) |
| Testing | pytest + FastAPI TestClient |

---

## Project Structure

```
skatemap/
├── main.py              # Creates the FastAPI app and registers routers
├── run.py               # Dev runner — starts uvicorn and opens the browser
├── config.py            # Central config, reads from environment / .env
│
├── api/                 # HTTP layer
│   ├── schemas.py       # Pydantic request and response models
│   ├── spots.py         # /spots router and endpoint handlers
│   └── auth.py          # /auth router (stub — not yet implemented)
│
├── core/                # Shared application utilities
│   └── security.py      # Password hashing and JWT utilities (stub — not yet implemented)
│
├── database/            # Data access layer
│   ├── db.py            # Engine, session factory, declarative Base, get_db dependency
│   ├── models.py        # SQLAlchemy ORM models (Spot, Image)
│   ├── utils.py         # Shared query helpers (get_or_404)
│   ├── spot_db.py       # Spot CRUD operations
│   ├── images_db.py     # Image CRUD operations
│   └── users_db.py      # User operations (stub — not yet implemented)
│
├── static/images/       # Uploaded spot images, organised by spot UUID
│
└── tests/
    ├── conftest.py      # Shared fixtures — test DB, client, spot
    ├── test_api/        # Tests against the HTTP layer via TestClient
    └── test_db/         # Tests against the database layer directly
```

---

## Layer Diagram

```mermaid
graph TD
    Client([HTTP Client])

    subgraph API Layer
        Router[Routers\nspots.py / auth.py]
        Schemas[Schemas\napi/schemas.py]
        Router <-->|validated by| Schemas
    end

    subgraph Data Layer
        SpotDB[spot_db.py]
        ImagesDB[images_db.py]
        UsersDB[users_db.py]
        Utils[utils.py]
        Models["models.py — Spot, Image"]
    end

    subgraph Core
        Security[security.py]
    end

    Config[config.py]
    DB[(PostgreSQL)]
    FileStore[static/images/]

    Client -->|HTTP| Router
    Router --> SpotDB & ImagesDB
    SpotDB & ImagesDB --> Utils
    SpotDB & ImagesDB & UsersDB --> Models
    Models -->|SQLAlchemy ORM| DB
    Router -->|file upload / delete| FileStore
    Config -.-> Router & Models
    Security -.-> UsersDB
```

---

## Request Lifecycle

Example — `GET /spots/{id}`:

```mermaid
sequenceDiagram
    participant Client
    participant FastAPI
    participant spots.py
    participant spot_db.py
    participant PostgreSQL

    Client->>FastAPI: GET /spots/{spot_id}
    FastAPI->>FastAPI: validate spot_id as UUID
    FastAPI->>FastAPI: open db session via get_db()
    FastAPI->>spots.py: get_spot(spot_id, db)
    spots.py->>spot_db.py: get_spot(db, spot_id)
    spot_db.py->>spot_db.py: get_or_404(db, Spot, spot_id)
    spot_db.py->>PostgreSQL: SELECT * FROM spots WHERE id = ?
    PostgreSQL-->>spot_db.py: row or 404
    spot_db.py-->>spots.py: Spot
    spots.py-->>FastAPI: Spot ORM object
    FastAPI->>FastAPI: serialise to SpotRead
    FastAPI-->>Client: 200 JSON
```

---

## Data Model

```mermaid
erDiagram
    spots {
        UUID id PK
        VARCHAR(50) name
        TEXT description
        FLOAT latitude
        FLOAT longitude
        DATETIME created_at
    }

    images {
        UUID id PK
        UUID spot_id FK
        VARCHAR file_path
        DATETIME uploaded_at
    }

    spots ||--o{ images : "has many"
```

Deleting a spot cascades to its images (`cascade="all, delete-orphan"`).

---

## Database Session

`get_db()` in `database/db.py` is a FastAPI dependency injected into route handlers. It opens a session before the handler runs and closes it once the response is sent.

In tests, `app.dependency_overrides[get_db]` replaces this with a session bound to the test database, keeping test data completely isolated from development data.

---

## Configuration

All settings are defined in `config.py` as a Pydantic `Settings` class. Values are read from environment variables, falling back to the defaults defined in the class. A `.env` file at the project root is loaded automatically.

`DATABASE_URL` is a computed property assembled from the individual `POSTGRES_*` fields. `BASE_DIR` and `UPLOAD_DIR` are `ClassVar` path constants, excluded from Pydantic's field handling.

---

## Image Storage

Uploaded images are saved to `static/images/{spot_id}/{filename}` on the local filesystem. The path is stored in the `images` table. Deleting an image via the API removes both the database record and the file from disk.
