# 🚀 AI Notes & Translation Microservice

A clean, minimal, production-ready backend service built with **Django**, **Django REST Framework**, **PostgreSQL**, **Redis**, and **Docker**.  
This project satisfies requirements from the assignment while keeping the codebase simple and human-readable.

---

##  Project Structure

```
ai_notes/
│   manage.py
│   requirements.txt
│   Dockerfile
│   docker-compose.yml
│
├── ai_notes_proj/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
└── notes/
    ├── models.py
    ├── api.py
    └── migrations/
```

All notes logic (CRUD, upload, translate, stats, serializers, router) lives in **notes/api.py** to keep the service minimal.

---

##  Tech Stack

- **Python 3.11**
- **Django + Django REST Framework**
- **PostgreSQL** (database)
- **Redis** (caching)
- **Docker** (containerization)
- **Docker Compose** (orchestration)

### Why PostgreSQL?

PostgreSQL is selected because it is:

- reliable and production-grade
- ACID-compliant
- excellent for structured CRUD workloads
- stable with Django ORM

SQLite is removed in favor of Postgres for the assignment.

---

##  Features

###  Notes CRUD

`/api/notes/` supports create, list, retrieve, update, delete.

###  Upload `.txt` Files

`POST /api/notes/upload/` creates a note from a text file.

###  Translate Notes

`POST /api/notes/<id>/translate/`  
Stores translated text + language in the same note.

A deterministic translation stub is used for self-containment:

```
TRANSLATED(<lang>): <reversed_text>
```

###  Stats Endpoint

`GET /api/stats/` returns:

- total notes
- translations performed
- language breakdown

Cached for 60 seconds in Redis.

###  Fully Dockerized

One command spins up the entire stack:

- Django (web)
- Postgres (db)
- Redis (cache)

---

##  Running the Project with Docker

From the project root:

```bash
docker-compose up --build
```

Run migrations:

```bash
docker-compose run --rm web python manage.py migrate
```

API is available at:

```
http://localhost:8000/api/
```

---

##  API Endpoints

### Notes CRUD

```
GET   /api/notes/
POST  /api/notes/
GET   /api/notes/<id>/
PUT   /api/notes/<id>/
PATCH /api/notes/<id>/
DELETE /api/notes/<id>/
```

### Upload Text File

```
POST /api/notes/upload/
```

Form-data fields:

- `file`: required `.txt` file
- `title`: optional
- `language`: optional

### Translate Note

```
POST /api/notes/<id>/translate/
```

Body:

```json
{ "target_language": "hi" }
```

### Stats

```
GET /api/stats/
```

---

##  High-Level Design (HLD)

```
            ┌────────────┐
            │   Client    │
            └──────┬─────┘
                   │ REST
            ┌──────▼────────┐
            │ Django / DRF   │  <-- Main service
            └───┬───────────┘
                │
        ┌───────▼────────┐
        │   PostgreSQL    │  <-- Persistent data
        └───────┬────────┘
                │
        ┌───────▼────────┐
        │     Redis       │  <-- Cache layer (stats)
        └─────────────────┘
```

---

##  Low-Level Design (LLD)

### Model: `Note`

- title
- text
- language
- translated_text
- translated_language
- created_at
- updated_at

### Key Logic (notes/api.py)

- CRUD via DRF ViewSet
- Upload endpoint using Django's file handling
- Translation endpoint
- Stats aggregation + Redis caching
- Router registration

---

##  AWS Deployment

### Option A — EC2 Deployment (simple)

1. Launch Ubuntu EC2 instance
2. Install Docker + Docker Compose
3. Clone repository
4. Run:
   ```bash
   docker-compose up --build -d
   ```
5. Expose port **8000** in the security group

### Option B — EKS (optional)

- Push Docker image to ECR
- Apply Deployment + Service YAML
- Use AWS Load Balancer Controller

---

##  Environment Variables

The service supports `.env` or environment-based configuration:

```
DATABASE_URL=postgres://...
REDIS_URL=redis://...
DJANGO_SECRET_KEY=yourkey
```

---

##  Example Requests

### Create a Note

```bash
curl -X POST http://localhost:8000/api/notes/   -H "Content-Type: application/json"   -d '{"title":"Test","text":"Hello","language":"en"}'
```

### Upload File (CMD example)

```cmd
curl -X POST http://localhost:8000/api/notes/upload/ ^
  -F "file=@C:\path	o
ote.txt" ^
  -F "title=FromFile" ^
  -F "language=en"
```

### Translate a Note

```bash
curl -X POST http://localhost:8000/api/notes/1/translate/   -H "Content-Type: application/json"   -d '{"target_language":"hi"}'
```

---

##  Notes

- Kept intentionally minimal (few files).
- All optional assignment components (JWT, Celery, GraphQL) are not included because they were explicitly optional.
- The deterministic translation stub removes external API dependencies.
- Redis caching significantly improves performance of stats endpoint.

---

##  Conclusion

The solution is lightweight, readable, and fully functional—ideal for review and deployment.
