# SmartERP — AI-Powered Enterprise ERP

A production-ready, modular ERP system with AI assistant, RAG document search, and real-time updates.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy 2.x, Alembic |
| Frontend | React, TypeScript, Vite, TanStack Query, Tailwind CSS |
| Database | MySQL 8+ (business data) |
| Cache/Queue | Redis |
| Vector DB | Qdrant (RAG) |
| AI | Ollama (local LLM + embeddings) |
| Storage | Local filesystem (dev) / Azure Blob (prod) |
| Real-time | Socket.IO |

---

## Quick Start (Local Development)

### Prerequisites

- Python 3.12+
- Node.js 20+ LTS
- MySQL 8+
- Redis (Memurai for Windows, or WSL)

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
API Docs: http://localhost:8000/docs

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
│   │   ├── workers/             ← Background job processors
│   │   ├── rag/                 ← Document search/RAG pipelines
│   │   └── storage/             ← Cloud/Local file storage logic
│   ├── scripts/                 ← Admin & helper scripts
│   ├── tests/                   ← Backend test suite
│   ├── requirements.txt         ← Production dependencies
│   └── alembic.ini              ← Alembic configuration
│
├── frontend/
│   ├── public/                  ← Static assets
│   ├── src/
│   │   ├── api/                 ← API client setup
│   │   ├── components/          ← Reusable UI building blocks
│   │   ├── features/            ← Feature-based structure (pages)
│   │   ├── layouts/             ← Main layout wrapper components
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

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Foundation | Auth, Users, RBAC, Project structure |
| 2 | 🔜 | Companies, Products, Suppliers, Customers |
| 3 | 🔜 | Inventory & Stock movements |
| 4 | 🔜 | Procurement workflow |
| 5 | 🔜 | Sales, Invoices, Payments |
| 6 | 🔜 | Azure Blob / Local file storage |
| 7 | 🔜 | Redis & Background workers |
| 8 | 🔜 | Socket.IO real-time |
| 9 | 🔜 | RAG pipeline (Qdrant + embeddings) |
| 10 | 🔜 | AI Assistant |
| 11 | 🔜 | Tests & Security hardening |
| 12 | 🔜 | Production readiness |

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

Full interactive API documentation available at: http://localhost:8000/docs

---

## License

MIT
