# Natural Language MongoDB Interface

A backend-first project that lets users interact with MongoDB using **plain English**, without writing database queries or code.  
The system focuses on **safety**, **clarity**, and **non-technical usability**.

Example:
> “Show employees earning more than 50k”

The backend understands the intent and converts it into **safe MongoDB queries** with guardrails like query preview and permissions.

---

## Features (Under Implementation)

- Natural language → MongoDB query conversion  
- Safety-first design (no blind execution)  
- Query preview before execution  
- Role-based permission checks  
- Audit-friendly logging  
- Backend-first (frontend can evolve independently)

---

## Project Structure

```
.
├── apps
│   ├── backend                  # FastAPI + NLP backend
│   │   ├── app
│   │   │   ├── api               # API routes and dependencies
│   │   │   │   ├── deps.py
│   │   │   │   └── routes.py
│   │   │   ├── audit             # Audit logging
│   │   │   │   └── logger.py
│   │   │   ├── auth              # Permissions and access control
│   │   │   │   └── permissions.py
│   │   │   ├── core              # Shared backend utilities
│   │   │   │   ├── config.py
│   │   │   │   └── utils.py
│   │   │   ├── db                # MongoDB connection and models
│   │   │   │   ├── models.py
│   │   │   │   └── mongo.py
│   │   │   ├── nlp               # Natural language processing
│   │   │   │   ├── intents.py
│   │   │   │   └── parser.py
│   │   │   ├── query             # Query builder, preview, safety rules
│   │   │   │   ├── builder.py
│   │   │   │   ├── preview.py
│   │   │   │   └── safety.py
│   │   │   └── main.py            # FastAPI entry point
│   │   ├── tests                 # Backend tests
│   │   ├── requirements.txt
│   │   └── README.md
│   │
│   └── frontend                  # SvelteKit frontend
│       ├── src
│       │   ├── routes             # Pages and layouts
│       │   │   ├── +layout.svelte
│       │   │   └── +page.svelte
│       │   ├── lib                # Reusable frontend code
│       │   │   ├── assets
│       │   │   │   └── favicon.svg
│       │   │   └── index.ts
│       │   ├── app.d.ts
│       │   └── app.html
│       ├── static
│       │   └── robots.txt
│       ├── package.json
│       ├── package-lock.json
│       ├── svelte.config.js
│       ├── tsconfig.json
│       ├── vite.config.ts
│       └── README.md
│
├── core                           # Shared logic (future use)
│   ├── shared-types
│   └── utils
├── docker                         # Docker-related configs
├── docs                           # Documentation
└── README.md                      # Main project README

```

---

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Setup

1. Clone the repository
```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
```

2. Create environment file
```bash
cp .env.example .env
```

Edit the `.env` file with your configuration:
```env
MONGO_URI=mongodb://localhost:27017/example
APP_ENV=development
```

3. Start the development environment
```bash
docker-compose -f docker-compose.dev.yml up --build
```

### Services

The following services will be available:

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:5173

### Stopping Services

```bash
docker-compose -f docker-compose.dev.yml down
```

### Development Features

- Hot reload for both backend and frontend
- Isolated environment with all dependencies managed
- Volume mounting for live code synchronization

---

## Philosophy

- Human-first: built for non-technical users  
- Safety-first: no destructive actions without confirmation  
- Backend-first: frontend is optional and replaceable  
- Rule-based before AI: avoids blind execution and hallucinations

---

## Status

This project is in **early development**.  
Structure and foundations are intentionally kept simple and extensible.

---

## License

[MIT License](LICENSE) - See the [LICENSE](LICENSE) file for details.
