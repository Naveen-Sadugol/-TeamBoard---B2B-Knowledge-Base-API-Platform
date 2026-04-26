<<<<<<< HEAD
# -TeamBoard---B2B-Knowledge-Base-API-Platform
TeamBoard is a Django REST API for a B2B knowledge base platform. Companies can register, authenticate with JWT, query the knowledge base, and admins can view usage analytics.
=======
# TeamBoard Backend

TeamBoard is a Django REST API for a B2B knowledge base platform. Companies can register, authenticate with JWT, query the knowledge base, and admins can view usage analytics.

## Stack

- Django 5
- Django REST Framework
- SimpleJWT
- PostgreSQL via Docker

## Setup

1. Create a `.env` file from `.env.example`.
2. Start PostgreSQL:

```bash
docker compose up -d
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Apply migrations:

```bash
python manage.py migrate
```

5. Seed the knowledge base:

```bash
python manage.py seed_kb_entries
```

6. Run the server:

```bash
python manage.py runserver
```

## Endpoints

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/kb/query/`
- `GET /api/admin/usage-summary/`

## Notes

- The `Company` profile and `api_key` are created automatically by a signal when a new `User` is saved for the first time.
- All endpoints require JWT authentication by default except register and login.
- Promote a company to admin by updating `role` to `admin` in PostgreSQL or the Django shell, then log in again for a fresh token.

## Postman

The exported collection is available at `postman/TeamBoard.postman_collection.json`.
>>>>>>> 46466b8 (Initial TeamBoard backend implementation)
