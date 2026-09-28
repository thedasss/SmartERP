# SmartERP Codebase Analysis

## 1. Overview
**SmartERP** is a full-stack modern enterprise resource planning application tailored for **AI-Powered Procurement, Inventory & Document Management**. The architecture consists of a robust asynchronous Python backend and a responsive, dynamic React frontend.

## 2. Technology Stack

### Backend Stack
Located in the `backend/` directory, the backend relies on modern, asynchronous Python technologies:
- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) - High-performance web framework.
- **Database & ORM**: 
  - [SQLAlchemy 2.0 (Async)](https://docs.sqlalchemy.org/) - For relational data modeling.
  - SQLite/MySQL (via `aiosqlite` & `aiomysql`) - Asynchronous database drivers.
  - [Alembic](https://alembic.sqlalchemy.org/) - Database migration management.
- **AI & Vector DB**:
  - [Qdrant Client](https://qdrant.tech/) - Vector database for embeddings and AI search.
  - [Ollama](https://ollama.ai/) - Local LLM integration.
- **Caching & Real-Time**: 
  - [Redis (Async)](https://redis.io/) - Used for caching, background workers, and possibly web-socket pub-sub.
- **Security & Validation**: 
  - [Pydantic V2](https://docs.pydantic.dev/) - For environment configurations and data schemas.
  - `python-jose` & `passlib` - JWT token generation and password hashing (Argon2).
- **Other Utils**: `structlog` for structured logging, `slowapi` for rate-limiting, and `pytest-asyncio` for testing.

### Frontend Stack
Located in the `frontend/` directory, the frontend is built as a Single Page Application (SPA):
- **Core**: React 19 + TypeScript.
- **Build Tool**: [Vite](https://vitejs.dev/) - Lightning-fast build environment.
- **State Management & Fetching**: 
  - [Zustand](https://github.com/pmndrs/zustand) - Lightweight global state management.
  - [TanStack React Query v5](https://tanstack.com/query/latest) - Asynchronous state, data fetching, and caching.
- **Routing**: [React Router v7](https://reactrouter.com/) - Client-side routing.
- **Styling**: [Tailwind CSS v3](https://tailwindcss.com/) + Headless UI + PostCSS for utility-first styling and accessible UI components.
- **Real-Time & Data Visualization**: 
  - [Socket.io Client](https://socket.io/) - For real-time ERP updates from the backend.
  - [Recharts](https://recharts.org/) - For dashboard analytics and charts.
- **Icons**: `lucide-react`.

---

## 3. Architecture & Directory Structure

### Backend Architecture (`backend/app/`)
The backend follows a layered Domain-Driven Design (DDD) pattern, making it highly modular:
- `api/`: Controllers and routers (v1), grouped by feature.
- `core/`: Core application configs, database connection logic, security, and logging settings.
- `models/`: SQLAlchemy ORM definitions for database tables.
- `schemas/`: Pydantic models used for request/response validation.
- `repositories/`: Database abstraction layer handling queries to the DB.
- `services/`: Core business logic that utilizes repositories and external tools.
- `rag/`: Retrieval-Augmented Generation logic integrating Qdrant and Ollama.
- `storage/`: Local or cloud file storage handlers (e.g., document management).
- `websocket/`: Socket.IO or FastAPI WebSocket handlers for real-time notifications.
- `workers/`: Background task processing (likely with Redis/Celery or RQ).

### Frontend Architecture (`frontend/src/`)
The frontend is feature-driven and strictly componentized:
- `features/` & `pages/`: Groups domain-specific screens (e.g., `auth`, `dashboard`, `master-data`, `inventory`, `procurement`, `sales`, `finance`, `reports`, `ai`).
- `components/`: Shared reusable UI elements (e.g., tables, buttons, inputs).
- `layouts/`: Master page wrappers (e.g., `DashboardLayout`, `ProtectedRoute`).
- `api/` & `services/`: Axios instances and logic for API calls.
- `hooks/`: Custom React hooks, heavily used with React Query.
- `store/` *(implied by Zustand)*: Global application state management.
- `utils/` & `types/`: Helper functions and global TypeScript definitions.

---

## 4. Key Features & Modules
Based on the frontend routing and backend dependencies, the system supports:
1. **Master Data Management**: Users, Products, Suppliers, and Customers.
2. **Inventory & Warehouse**: Stock tracking, multi-warehouse support.
3. **Sales & Procurement**: End-to-end management of Purchase Orders and Sales Orders.
4. **Finance**: Invoice generation and tracking.
5. **Smart / AI Capabilities**: Real-time insights, document intelligence (RAG), and smart querying via local LLMs (Ollama) and Vector Search (Qdrant).
6. **Real-Time Dashboards**: Web-socket enabled UI for instantaneous ERP state updates and dynamic charts.

## 5. Development Workflow
- Frontend runs via `npm run dev` (Vite on port 5173).
- Backend runs via `uvicorn app.main:app --reload` (FastAPI).
- `alembic` is used to manage database migrations, ensuring seamless DB schema evolution.
