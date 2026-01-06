# Tech Stack - MoneyMind v5.0

## Stack Overview

### Frontend Layer
| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15.x | React framework with App Router |
| **React** | 19.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 4.x | Utility-first CSS |
| **shadcn/ui** | latest | Component library |
| **React Query** | 5.x | Server state management |
| **Lucide React** | latest | Icons |

### Backend Layer
| Technology | Version | Purpose |
|------------|---------|---------|
| **FastAPI** | 0.115+ | REST API framework |
| **Pydantic** | 2.x | Schema validation |
| **Uvicorn** | 0.34+ | ASGI server |

### Data Layer
| Technology | Version | Purpose |
|------------|---------|---------|
| **SQLite** | 3.x | Local persistence |
| **Pandas** | 2.0+ | CSV/Excel parsing |
| **openpyxl** | 3.1+ | Illimity XLSX parsing |

### AI Layer
| Technology | Model | Purpose |
|------------|-------|---------|
| **Anthropic SDK** | 0.18+ | Claude API integration |
| **Claude Haiku** | - | Low-cost batch categorization |
| **Claude Opus 4.5** | - | Extended thinking for insights |
| **Claude Sonnet** | - | Monthly report generation |

### Legacy (Deprecato v5.0)
| Technology | Version | Purpose |
|------------|---------|---------|
| **Streamlit** | 1.28+ | [LEGACY] UI (sostituito da Next.js) |
| **Plotly** | 5.18+ | [LEGACY] Charts (migrazione a Recharts) |

## Rationale per Scelte Tecnologiche

### Next.js + React (v5.0)
**Perché**:
- App Router per routing file-based
- React 19 con Server Components
- Ottima DX con TypeScript e Tailwind
- Facile deployment su Vercel

**Migrazione da Streamlit**:
- Streamlit limitato per UI complesse e mobile
- Next.js offre maggiore controllo su UX
- Performance migliorata con React Query caching
- PWA ready per installazione mobile

### FastAPI Backend
**Perché**:
- Automatic OpenAPI/Swagger documentation
- Type safety con Pydantic
- Async support per chat streaming (SSE)
- Facile integrazione con Python esistente

**Alternative considerate**:
- Django REST: Troppo pesante per questo use case
- Flask: Manca validazione automatica schemas

### shadcn/ui
**Perché**: Componenti copiabili e personalizzabili, non una dependency. Stile moderno e dark-mode ready.

### React Query
**Perché**:
- Caching automatico delle API calls
- Stale-while-revalidate pattern
- Mutation handling con optimistic updates
- DevTools per debugging

### SQLite (Mantenuto)
**Perché**: Zero setup, file locale portabile, nessun server da gestire. Sufficiente per migliaia di transazioni.

### Claude API (Multi-Model)
**Perché**: Strategia ottimizzata per costo/qualità:

| Use Case | Model | Cost/1M tokens | Rationale |
|----------|-------|----------------|-----------|
| Categorization | Haiku | ~$0.25 | Alto volume, task semplice |
| Daily Insights | Opus 4.5 | ~$15 | Extended thinking, decisioni critiche |
| Monthly Reports | Sonnet | ~$3 | Generazione testo, buon balance |

**Costo stimato**: ~$10/mese per uso tipico (200 tx/mese, insights giornalieri)

## Environment Setup

### Frontend Requirements
```json
{
  "dependencies": {
    "next": "^15.0.0",
    "react": "^19.0.0",
    "@tanstack/react-query": "^5.0.0",
    "tailwindcss": "^4.0.0",
    "lucide-react": "latest"
  }
}
```

### Backend Requirements
```
fastapi>=0.115.0
uvicorn>=0.34.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
```

### Python Core Requirements
```
pandas>=2.0.0
openpyxl>=3.1.0
anthropic>=0.18.0
python-dotenv>=1.0.0
```

### Environment Variables
```bash
# .env file
ANTHROPIC_API_KEY=sk-ant-xxx
```

## Architettura Deployment

```
┌───────────────────────────────────────────────────────────────┐
│                      Local Machine (Windows)                   │
│                                                               │
│  ┌─────────────┐         ┌─────────────┐   ┌─────────────┐   │
│  │   Next.js   │  REST   │   FastAPI   │   │   SQLite    │   │
│  │   :3000     │ ──────► │   :8001     │───│  data/*.db  │   │
│  └─────────────┘         └──────┬──────┘   └─────────────┘   │
│         │                       │                             │
│         │                       │ HTTPS                       │
│         │                       ▼                             │
│         │                ┌─────────────┐                      │
│         │                │ Claude API  │                      │
│         │                │ (External)  │                      │
│         │                └─────────────┘                      │
│         │                                                     │
│         │ Browser                                             │
│         ▼                                                     │
│  ┌─────────────┐                                              │
│  │   Chrome    │                                              │
│  │  localhost  │                                              │
│  └─────────────┘                                              │
└───────────────────────────────────────────────────────────────┘
```

### Development Servers
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --port 8001 --reload

# Terminal 2: Frontend
cd frontend && npm run dev
```

### Production (Future)
```
Frontend: Vercel
Backend: Railway/Render
Database: SQLite → PostgreSQL (optional)
```

## Performance Considerations

- **API Caching**: React Query with staleTime: 5min
- **Categorization**: Batch di 10 transazioni per chiamata API
- **DB Queries**: Indici su date, category_id, status
- **AI Latency**: Insights pre-generati, non real-time
- **SSE Streaming**: Chat responses streamed in real-time

## Security

- API key in `.env`, mai committata
- Database locale, nessun dato su cloud
- Solo descrizioni transazioni inviate a Claude (no IBAN, numeri conto)
- CORS configurato per localhost only (dev)
- `.gitignore` include: `.env`, `data/*.db`, `__pycache__`, `node_modules/`
