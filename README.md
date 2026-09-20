# 🌟 Datastraw Support CRM — Full-Stack AI Customer Operations Platform

> **Candidate Assignment**: Full Stack AI Developer Intern Assessment  
> **Live Deployed Application**: [https://web-production-1071.up.railway.app](https://web-production-1071.up.railway.app)  
> **Demo Video Walkthrough (Google Drive)**: [Watch 1080p Demo Video](https://drive.google.com/file/d/116WJ7o2vi8Mf0d4gzCwVIReKft7xIVhB/view?usp=sharing)  
> **Interactive API Docs (Swagger)**: [https://web-production-1071.up.railway.app/docs](https://web-production-1071.up.railway.app/docs)  
> **Backend**: FastAPI • SQLAlchemy ORM • SQLite • Groq Cloud AI Engine (`groq/compound-mini` / Llama 3)  
> **Frontend**: React 19 • Vite • Dual Theme (Day Mode Default / Dark Mode) • Glassmorphism SaaS UI  

---

## 🚀 Overview

**Datastraw Support CRM** is a production-grade multi-channel Customer Support Operations system tailored for fast-growing D2C e-commerce brands. It combines robust backend system design with real-time AI automation:

1. **Multi-Channel Ingestion Pipeline**: Ingestion for `Email`, `WhatsApp`, `Shopify`, and `Web Form` channels with a dedicated webhook endpoint (`POST /api/webhooks/inbound`).
2. **Multi-Tenant Brand Separation**: Support operations across brands (`Aura D2C`, `UrbanKicks`, `GlowCare`) with isolated filtering.
3. **Decoupled AI Engine (Groq Cloud)**:
   - **Autonomous Triage Agent**: Real-time ticket classification for Urgency (`Urgent`, `High`, `Medium`, `Normal`), Category detection, and concise 1-sentence TL;DR summary.
   - **1-Click AI Draft Copilot**: Personalized, empathetic resolution replies synthesized using customer history, simulated live Shopify order tracking, and team notes.
   - **Deterministic Offline Fallback**: Graceful heuristic degradation ensuring zero downtime when external networks or API keys are unavailable.
4. **Simulated D2C Order Context**: Real-time courier tracking (Shiprocket/BlueDart), order fulfillment status, and items breakdown.
5. **Modern React Frontend**: High-performance React 19 single-page application with dual theme support (**Dark Mode** & **Light Mode**), search-as-you-type, instant status cycling, CSV export, and power-agent keyboard shortcuts (`/`, `C`, `J`, `K`, `D`, `?`).

---

## 🛠️ Tech Stack & Architecture

```
                       ┌─────────────────────────────────────────┐
                       │     React 19 + Vite Frontend App        │
                       │  (Dual Themes, Glassmorphism, Hotkeys)  │
                       └────────────────────┬────────────────────┘
                                            │ HTTP / JSON
                                            ▼
                       ┌─────────────────────────────────────────┐
                       │         FastAPI Backend Server          │
                       │   (Port 8000, CORS, Auto-Migrations)    │
                       └───┬─────────────┬─────────────────┬─────┘
                           │             │                 │
            ┌──────────────▼───┐   ┌─────▼──────────┐   ┌──▼──────────────────┐
            │   SQLite DB      │   │  Order Service │   │   Groq AI Engine    │
            │ (SQLAlchemy ORM) │   │ (Shopify D2C)  │   │(compound-mini/Llama)│
            └──────────────────┘   └────────────────┘   └─────────────────────┘
```

- **Backend**: Python 3.13, FastAPI, Pydantic v2, SQLAlchemy, Uvicorn, Pytest.
- **AI**: Groq Cloud API, OpenAI SDK client, JSON Structured Outputs, deterministic regex fallback.
- **Frontend**: React 19, Vite, Vanilla CSS tokens, Google Fonts (`Plus Jakarta Sans`, `Inter`, `JetBrains Mono`).

---

## 📦 Quick Start & Setup Guide

### 1. Prerequisites
- Python 3.10+ (Python 3.13 supported)
- Node.js 18+ (Node 22 LTS verified)
- Windows PowerShell, macOS, or Linux terminal

### 2. Environment Configuration
Create a `.env` file in the root directory (a `.env.example` template is provided):
```env
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=groq/compound-mini
DATABASE_URL=sqlite:///./support_crm.db
PORT=8000
HOST=127.0.0.1
```

### 3. Backend Setup
```powershell
# Activate existing virtual environment (or create with python -m venv venv)
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run backend server
python run.py
```
Backend API will start at: `http://127.0.0.1:8000`  
Interactive Swagger API Docs: `http://127.0.0.1:8000/docs`

### 4. Frontend Setup
```powershell
cd frontend
npm install
npm run dev
```
Frontend development server will start at: `http://localhost:5173/`

> **Note**: If you run `npm run build` in `frontend/`, FastAPI will automatically mount and serve the production React dashboard directly at `http://127.0.0.1:8000/` with a single command!

### 5. Running Automated Tests
The backend test suite verifies health endpoints, CRUD operations, Groq triage, D2C context, and multi-channel webhooks:
```powershell
pytest backend/tests/test_api.py -v
```
**Test Result**: 9 passed, 100% pass rate.

---

## 📑 API Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/tickets` | Create ticket with autonomous Groq AI triage |
| `GET` | `/api/tickets` | List tickets with search, filtering, and pagination |
| `GET` | `/api/tickets/{id}` | Detailed ticket view with internal notes thread |
| `PUT` | `/api/tickets/{id}` | Update status, priority, or append team notes |
| `POST` | `/api/tickets/{id}/ai-triage` | Re-analyze ticket urgency and summary via Groq |
| `POST` | `/api/tickets/{id}/ai-draft` | Generate context-aware 1-click suggested reply |
| `GET` | `/api/tickets/{id}/order-context` | Fetch simulated Shopify order & carrier tracking |
| `POST` | `/api/tickets/seed` | Seed 7 realistic multi-tenant demo tickets |
| `GET` | `/api/analytics/metrics` | Real-time support KPI metrics (SLA, volume, rate) |
| `POST` | `/api/webhooks/inbound` | Ingestion webhook for WhatsApp/Email/Shopify |
| `GET` | `/api/health` | Service health status |

---

## ⌨️ Power-Agent Keyboard Shortcuts

Press **`?`** or **`⌘K`** in the React application to view shortcuts:
- **`/`**: Focus global search-as-you-type input
- **`C`**: Open New Ticket ingestion modal
- **`J`**: Select next ticket down the queue
- **`K`**: Select previous ticket up the queue
- **`D`**: Toggle Dark Mode / Day Mode theme
- **`Esc`**: Close modals or clear search

---

## 💡 What We Added, Why, and Tradeoffs

### 1. What We Added
- **Multi-Tenant Brand Separation**: Real-world support setups handle multiple brands or client stores. We built tenant tags (`Aura D2C`, `UrbanKicks`, `GlowCare`) into ticket models, schemas, filters, and seeds.
- **Groq Cloud AI Integration**: Using `groq/compound-mini` / Llama 3 via Groq's high-speed inference cloud to deliver sub-second auto-triage (Urgency, Category, TL;DR) and personalized resolution drafts.
- **D2C Order Context Service**: E-commerce support requires order lookup (items, shipping courier, tracking). Simulated live context is injected into AI prompts and displayed to agents.
- **Multi-Channel Webhook Pipeline**: Provides standard endpoints for inbound ingestion from WhatsApp (Meta Cloud API), Email (SendGrid), and Shopify webhooks.
- **Dual-Theme React Architecture**: Dark mode is standard for support agents working extended hours, while light/day mode provides maximum daylight legibility.

### 2. Tradeoffs & Engineering Decisions
- **SQLite with ORM vs PostgreSQL**: SQLite was chosen for zero-dependency local evaluator evaluation. To ensure production readiness, indexes were explicitly added on `(status, created_at)`, `priority`, `channel`, and `customer_email`.
- **Hybrid AI Fallback**: Groq Cloud inference is lightning-fast, but network drops or expired API keys can fail external calls. We engineered a heuristic fallback so the system remains 100% operational offline without crashing.
- **Vanilla CSS Tokens vs Tailwind**: Used CSS custom properties for dual-theme switching (`[data-theme="dark"]` and `[data-theme="light"]`). This avoids Tailwind bundle overhead and provides complete control over animations, glassmorphism, and accessibility.
