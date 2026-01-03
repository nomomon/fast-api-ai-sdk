# AI Chatbot Template

A clean, modular template for building AI chatbot applications with FastAPI backend and Next.js frontend. 

## Features

- **FastAPI Backend**: Modern Python web framework with async support
- **Next.js Frontend**: React framework with App Router and TypeScript
- **AI Integration**: OpenAI SDK integration with streaming support
- **UI Components**: shadcn/ui for beautiful, accessible components
- **Docker Support**: Full containerization with docker-compose
- **Turborepo**: Fast monorepo build system for local development
- **Biome**: Fast formatter and linter for JavaScript/TypeScript
- **Ruff**: Fast Python linter and formatter
- **pnpm**: Fast, disk space efficient package manager
- **Modular Architecture**: Well-structured codebase with clear separation of concerns

## Project Structure

```
fast-api-ai-sdk/
├── backend/          # FastAPI backend
│   ├── app/         # Application code
│   │   ├── routes/  # API routes
│   │   ├── services/# Business logic
│   │   └── models/  # Data models
│   └── Dockerfile
├── frontend/        # Next.js frontend
│   ├── app/         # Next.js App Router
│   ├── components/  # React components
│   └── lib/         # Utilities and API client
└── docker-compose.yml
```

## Prerequisites

- Docker and Docker Compose (for deployment)
- Node.js 20+ (for local development)
- Python 3.11+ (for local development)
- pnpm 8+ (for package management)

## Quick Start

### Using Turborepo (Recommended for Local Development)

Turborepo provides fast, cached builds and parallel task execution for local development.

1. **Install pnpm (if not already installed):**
   ```bash
   npm install -g pnpm
   ```

2. **Install dependencies:**
   ```bash
   pnpm install
   ```

3. **Set up environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```
   Update `.env` files with your API keys and configuration.

4. **Set up Python virtual environment:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   cd ..
   ```

5. **Start development servers:**
   ```bash
   pnpm dev
   ```
   This runs both backend and frontend in parallel with hot reload.

6. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

**Available commands:**
- `pnpm dev` - Start development servers
- `pnpm build` - Build all packages
- `pnpm lint` - Lint all packages (Biome for frontend, Ruff for backend)
- `pnpm format` - Format all code (Biome for frontend, Ruff for backend)
- `pnpm check` - Format, lint, and organize imports (Biome for frontend, Ruff for backend)
- `pnpm type-check` - Type check all packages
- `pnpm clean` - Clean build artifacts

### Using Docker (Recommended for Deployment)

1. **Set up environment variables:**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.example frontend/.env
   ```
   Update `.env` files with your API keys and configuration.

2. **Start services:**
   ```bash
   docker-compose up
   ```

3. **Access the application:**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Manual Local Development

#### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

#### Frontend

```bash
cd frontend
pnpm install
pnpm dev
```

## Environment Variables

### Backend (.env)

```env
OPENAI_API_KEY=your_openai_api_key
ENVIRONMENT=development
```

## Development

### Turborepo Workflow

- **Local Development**: Use `pnpm dev` to run both services with Turborepo
- **Deployment**: Use `docker-compose up` for containerized deployment
- **Caching**: Turborepo caches build outputs for faster subsequent builds
- **Parallel Execution**: Tasks run in parallel when possible

### Code Quality Tools

#### Frontend (Biome)

- **Formatting**: `pnpm format` - Format all JavaScript/TypeScript files
- **Linting**: `pnpm lint` - Lint all JavaScript/TypeScript files
- **Check**: `pnpm check` - Format, lint, and organize imports
- Configuration: `biome.json` in the root directory

#### Backend (Ruff)

- **Formatting**: `pnpm --filter backend format` - Format all Python files
- **Linting**: `pnpm --filter backend lint` - Lint all Python files
- **Check**: `pnpm --filter backend check` - Format and lint all Python files
- Configuration: `backend/ruff.toml`

### Ports

- Backend runs on port 8000 with hot reload
- Frontend runs on port 3000 with hot reload
- API documentation available at `/docs` (Swagger UI)

### Turborepo Configuration

The `turbo.json` file configures:
- Task dependencies and execution order
- Environment variables for caching
- Build outputs and cache keys
- Development vs production configurations

See [Turborepo documentation](https://turbo.build/repo/docs) for more details.

### Package Management

This project uses **pnpm** for package management:
- Faster installs with content-addressable storage
- Disk space efficient with shared dependencies
- Strict dependency resolution
- Workspace support for monorepos

See [pnpm documentation](https://pnpm.io/) for more details.

## License

MIT
