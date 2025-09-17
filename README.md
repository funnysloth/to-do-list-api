# To‑Do List API

A RESTful API built with FastAPI for managing to‑do lists and their items. This API supports user management, list and item CRUD operations, and paginated responses. It uses PostgreSQL by default but can be adapted to use SQLite for local development.

## Features

- **User Management:** Register, log in, view, update, and delete user accounts.
- **To‑Do Lists:** Create, retrieve, update, and delete lists.
- **List Items:** Add, update, retrieve, and delete items within lists.
- **JWT Authentication:** Secure endpoints with JWT tokens.

## Installation

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database (or SQLite for dev/test)
- [Git](https://git-scm.com/)

### Cloning and Setting Up Locally

1. **Clone the repository:**

   ```sh
   git clone https://github.com/yourusername/to-do-list-api.git
   cd to-do-list-api
   ```

2. **Create and activate a virtual environment:**

   On Windows:
   ```sh
   python -m venv venv
   venv\Scripts\activate
   ```
   On macOS/Linux:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```sh
   pip install -r requirements.txt
   ```

## Environment Variables and Pydantic Settings

This project uses a `.env` file to manage environment variables. The configuration is loaded using Pydantic settings (typically in `app/config.py`). **Make sure that the path to your `.env` file is correctly specified** in your Pydantic settings. For example:

```python
# Example snippet from app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8") # Ensure this "env_file" is the correct .env file path

    DB_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_MINUTES: int
    REFRESH_TOKEN_EXPIRATION_DAYS: int
    REFRESH_TOKEN_SECRET: str

settings = Settings()
```

Create a `.env` file in the root directory (next to README.md) with the following variables, and update them as needed:

```
# .env file example
DATABASE_URL=postgresql+asyncpg://username:password@localhost/todo_db
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
# Additional configuration variables can be added here
```

## Database Setup

### Using PostgreSQL

1. **Install PostgreSQL:**  
   Follow the instructions at [PostgreSQL Downloads](https://www.postgresql.org/download/).

2. **Create a Database:**  
   Create a new database (e.g., `todo_db`).

3. **Configure the Database:**  
    Ensure your `.env` file has the correct connection string in the corresponding variable (`DATABASE_URL`).

### Using Docker

You can run PostgreSQL in a Docker container:

```sh
docker run --name postgres-todo -e POSTGRES_USER=username -e POSTGRES_PASSWORD=password -e POSTGRES_DB=todo_db -p 5432:5432 -d postgres
```

Then, update your `.env` file with the appropriate connection string.

### Using SQLite (Optional)

For local development or testing, switch to SQLite by updating your configuration (in `app/config.py`):

```python
DATABASE_URL = "sqlite+aiosqlite:///./todo_db.sqlite"
```

## Running the Application

Start the FastAPI application with **uvicorn**:

```sh
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at [http://localhost:8000](http://localhost:8000).

## API Documentation

FastAPI generates interactive documentation automatically:

- **Swagger UI:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc:** [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Endpoints Overview

### User Routes

- `POST /register` – Register a new user.
- `POST /login` – Authenticate and retrieve JWT tokens.
- `GET /me` – Retrieve the authenticated user’s profile.
- `PATCH /users` – Update authenticated user data.
- `DELETE /users` – Delete the user account.
- `POST /refresh-token` – Refresh JWT tokens.

### List Routes

- `POST /lists` – Create a new to‑do list.
- `GET /lists` – Retrieve paginated to‑do lists.
- `GET /lists/{list_id}` – Retrieve a specific list.
- `PATCH /lists/{list_id}` – Update list details.
- `DELETE /lists/{list_id}` – Delete a list.

### List Item Routes

- `POST /lists/{list_id}/items` – Create list items.
- `GET /lists/{list_id}/items` – Retrieve paginated list items.
- `GET /lists/{list_id}/items/{list_item_id}` – Retrieve a specific list item.
- `PATCH /lists/{list_id}/items/{list_item_id}` – Update a list item.
- `DELETE /lists/{list_id}/items/{list_item_id}` – Delete a list item.

## Contact

For questions or further information, please contact [your.email@example.com](mailto:your.email@example.com).