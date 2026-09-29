# SmartERP — AI-Powered Enterprise ERP

A modular ERP system covering master data, inventory, procurement, sales, finance, reporting and document management, with an Ollama-backed AI assistant that answers questions from your ERP data using RAG.

> See [Development Phases](#development-phases) for what is implemented today and what is still upcoming.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic |
| Frontend | React, TypeScript, Vite, TanStack Query, Tailwind CSS |
| Database | MySQL 8+ (business data) |
| Cache/Queue | Redis |
| Vector DB | Qdrant (RAG, embedded local mode) |
| AI | Ollama (local LLM `llama3` + embeddings) |
| Storage | Local filesystem (Azure Blob configurable, not yet implemented) |
| Real-time | Socket.IO (planned, not yet implemented) |

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.12+
- Node.js 20+ LTS
- MySQL 8+
- Redis (Memurai for Windows, or WSL)
- [Ollama](https://ollama.com) with the `llama3` model pulled (only needed for the AI assistant / RAG)

### 1. Clone & Setup

```bash
git clone <repo-url>
cd SmartERP
cp .env.example .env
# Edit .env with your MySQL password and JWT secret
```

### 2. Database Setup

```sql
CREATE DATABASE smarterp CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smarterp'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON smarterp.* TO 'smarterp'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
pip install -r requirements-dev.txt   # for tests

# Run migrations
alembic upgrade head

# Seed initial data (super admin + permissions)
python -m app.utils.seed

# Start development server
uvicorn app.main:app --reload --port 8000
```

Backend: http://localhost:8000
API Docs: http://localhost:8000/docs (Swagger UI) · http://localhost:8000/redoc

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

### 5. Login

| Field | Value |
|-------|-------|
| Email | admin@smarterp.com |
| Password | Admin@12345! |

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

---

## Project Structure

```text
SmartERP/
├── backend/
│   ├── alembic/                 ← Database migrations
│   ├── app/
│   │   ├── main.py              ← FastAPI application entrypoint
│   │   ├── core/                ← Configuration, Security, DB session
│   │   ├── models/              ← SQLAlchemy ORM entities
│   │   ├── schemas/             ← Pydantic validation schemas
│   │   ├── repositories/        ← Database query abstractions
│   │   ├── services/            ← Business logic and orchestrations
│   │   ├── api/                 ← Route definitions
│   │   ├── workers/             ← Background job processors (planned; not yet created)
│   │   ├── rag/                 ← Reserved package (RAG logic currently lives in services/rag.py)
│   │   └── storage/             ← Reserved package (uploads are currently handled in services/documents.py)
│   ├── scripts/                 ← Admin & helper scripts
│   ├── tests/                   ← Backend test suite
│   ├── requirements.txt         ← Production dependencies
│   └── alembic.ini              ← Alembic configuration
│
├── frontend/
│   ├── public/                  ← Static assets
│   ├── src/
│   │   ├── api/                 ← API client setup and master-data/inventory clients
│   │   ├── services/            ← API clients for sales, procurement, finance, AI, etc.
│   │   ├── components/          ← Reusable UI building blocks
│   │   ├── features/            ← Feature-based pages (auth, dashboard, master-data, inventory)
│   │   ├── pages/               ← Module pages (procurement, sales, finance, reports, documents, ai, users)
│   │   ├── hooks/               ← Custom React hooks
│   │   ├── layouts/             ← Main layout wrapper components
│   │   ├── utils/               ← Formatting helpers
│   │   └── types/               ← Shared TypeScript typings
│   ├── package.json             ← Node dependencies
│   ├── tailwind.config.js       ← Tailwind styling configuration
│   └── vite.config.ts           ← Vite build settings
│
├── .env.example                 ← Template for environment variables
├── .gitignore                   ← Global git ignore rules
├── .gitattributes               ← Git repository settings
└── README.md                    ← Project documentation
```

---

## Development Phases

Status reflects an audit of the current codebase, not the original roadmap.

| Status | Meaning |
|--------|---------|
| ✅ **Implemented** | Working backend and, where applicable, frontend code exists |
| 🟡 **Partially Implemented** | Some parts exist; gaps are listed in the notes |
| 🔜 **Upcoming** | No functional implementation yet |

| Phase | Feature | Status | Notes |
|-------|---------|--------|-------|
| 1 | Foundation: Auth, Users, RBAC | ✅ **Implemented** | JWT login/refresh/logout, user management, permission checks (`require_permission`) |
| 2 | Master Data: Companies, Products, Suppliers, Customers | ✅ **Implemented** | Products, categories, suppliers and customers have API and UI. Company is a data model used for multi-tenant scoping; there is no company management endpoint |
| 3 | Inventory & Stock Movements | ✅ **Implemented** | Warehouses, stock levels, stock movements |
| 4 | Procurement Workflow | ✅ **Implemented** | Purchase orders and goods receipt |
| 5 | Sales, Invoices, Payments | ✅ **Implemented** | Sales orders and shipments, invoices with PDF download, payments. Reminder emails are mocked (logged only) |
| 6 | Azure Blob / Local File Storage | 🟡 **Partially Implemented** | Local filesystem upload, download and delete via Documents. Azure settings exist in config but no Azure Blob code |
| 7 | Redis & Background Workers | 🟡 **Partially Implemented** | Redis connection helper and config only. No workers, queues or task processing. `slowapi` is a dependency but is not wired in |
| 8 | Socket.IO Real-time | 🔜 **Upcoming** | Only the `socket.io-client` package is installed. No server or client usage |
| 9 | RAG Pipeline (Qdrant + Embeddings) | ✅ **Implemented** | `RAGService` indexes ERP data into Qdrant (embedded mode) using Ollama embeddings and supports search. Uploaded documents are not indexed yet |
| 10 | AI Assistant | ✅ **Implemented** | `POST /api/v1/ai/chat` uses RAG context with an Ollama `llama3` chat model, plus an AI page in the frontend |
| 11 | Tests & Security Hardening | 🟡 **Partially Implemented** | Integration tests for auth, master data, inventory, procurement, sales, finance, reports, documents and AI; Argon2 password hashing; JWT. Rate limiting is not enabled and some endpoints have a pending permission TODO |
| 12 | Production Readiness | 🔜 **Upcoming** | No Dockerfile, CI workflow or deployment configuration in the repository |

### Project Progress

> Several features originally listed as upcoming are already implemented in the codebase.

| Area | Status |
|------|--------|
| Core Platform (Auth, Users, RBAC) | ✅ |
| Master Data & Inventory | ✅ |
| Procurement | ✅ |
| Sales & Finance | ✅ |
| Reports & Dashboard | ✅ |
| Documents (local storage) | ✅ |
| RAG & AI Assistant | ✅ |
| Background Workers | 🟡 |
| Real-time Communication (Socket.IO) | 🔜 |
| Production Readiness | 🔜 |

---

## Environment Variables

See `.env.example` for all configuration options. Key variables:

```env
DATABASE_URL=mysql+aiomysql://smarterp:password@localhost:3306/smarterp
JWT_SECRET=your-secret-key-here
REDIS_URL=redis://localhost:6379/0
OLLAMA_BASE_URL=http://localhost:11434
```

---

## API Documentation

Interactive API documentation is available at http://localhost:8000/docs (Swagger UI) and http://localhost:8000/redoc. The raw schema is served at `/openapi.json`.

Endpoints are grouped under `/api/v1` by tag: Auth, Users, Dashboard, Products, Partners, Inventory, Procurement, Sales, Finance, Reports, Documents and AI.

---

## License

MIT
