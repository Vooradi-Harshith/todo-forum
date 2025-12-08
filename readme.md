# 🛠️ ForumApp Backend

A high-performance, asynchronous microservice backend built with **FastAPI** and **PostgreSQL**. It provides a robust REST API and WebSocket services to power the ForumApp frontend.

The architecture follows strict **Clean Code** principles, ensuring modularity, scalability, and maintainability.

---

## 🚀 Key Features

* **FastAPI Core**:
    * Asynchronous request handling for high concurrency
    * Automatic **Swagger UI** and **ReDoc** documentation
    * **Pydantic** data validation for all inputs/outputs
* **Authentication & Security**:
    * **OAuth2** with Password Flow + **JWT** (JSON Web Tokens)
    * **Role-Based Access Control (RBAC)** (Admin, Moderator, Member)
    * Password hashing using **Bcrypt**
* **Data Management**:
    * **PostgreSQL** relational database
    * **SQLAlchemy ORM** for database abstraction
    * Normalized schema for Users, Threads, Posts, Comments, and Roles
* **Real-Time Engine**:
    * **WebSockets** for live notification delivery using a Pub/Sub pattern
    * In-memory connection manager (upgradeable to Redis)
* **Content Management**:
    * Recursive/Nested comment structures
    * Full CRUD for Threads and Posts
    * Search filtering and Pagination

---

## 🛠️ Tech Stack

* **Framework**: FastAPI (Python 3.10+)
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Validation**: Pydantic
* **Server**: Uvicorn (ASGI)
* **Containerization**: Docker & Docker Compose
* **Testing**: Pytest

---

## ⚙️ Prerequisites

* **Python**: v3.10 or higher
* **PostgreSQL**: v14 or higher (or use Docker)
* **Docker Desktop** (Recommended)

---

## 📦 Installation & Local Development

1. **Navigate to the backend directory:**
   ```bash
   cd backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables:**
   Create a `.env` file in the root directory (see `.env.example`):
   ```ini
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/forumdb
   SECRET_KEY=your_super_secret_key_here
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   ```

5. **Run the Server:**
   ```bash
   uvicorn app.main:app --reload
   ```

6. **Access API Docs:**
   Open `http://localhost:8000/docs` to see the interactive Swagger UI.

---

## 🐳 Docker Deployment

The backend is configured to run seamlessly with Docker Compose, orchestrating the App, Database, and PgAdmin.

### Build & Run

From the project root (where `docker-compose.yml` is located):

```bash
docker-compose up --build -d
```

### Services

* **API**: http://localhost:8000
* **PostgreSQL**: Port 5432
* **PgAdmin**: http://localhost:5050 (admin@admin.com / admin123)

---

## 📂 Project Structure

```
app/
├── api/
│   ├── v1/             # API Route Handlers (Controllers)
│   │   ├── auth.py     # Login/Register
│   │   ├── threads.py  # Thread CRUD
│   │   └── ...
│   └── deps.py         # Dependency Injection (Auth Guard, DB Session)
├── core/               # App Configuration
│   ├── config.py       # Pydantic Settings
│   └── security.py     # JWT & Hashing logic
├── db/                 # Database
│   ├── session.py      # Engine connection
│   └── base.py         # Model imports
├── models/             # SQLAlchemy Models (Data Layer)
│   ├── user.py
│   ├── thread.py
│   └── ...
├── schemas/            # Pydantic Models (DTO Layer)
│   ├── user.py         # UserCreate, UserRead
│   └── ...
└── main.py             # App Entry Point
```

---

## 🧪 Testing

The project includes a comprehensive test suite using Pytest.

To run tests:

```bash
pytest
```
