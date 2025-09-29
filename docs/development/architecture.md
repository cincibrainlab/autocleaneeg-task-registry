# Architecture Overview

Technical architecture of the AutoCleanEEG Task Registry and Task Wizard integration.

## Repository Structure

```
autocleaneeg-task-registry/
├── tasks/                       # Task implementations (Python files)
│   ├── resting/
│   ├── auditory/
│   ├── visual/
│   └── rodent/
├── registry.json                # Task index (name, path, category, description)
├── scripts/                     # CI automation scripts
│   ├── validate_registry.py    # Validates registry.json against tasks/
│   └── stamp_registry_commit.py # Updates commit hash in registry.json
├── src/                         # Cloudflare Worker (Task Wizard backend)
│   ├── index.ts                # Main worker entry point
│   ├── routes/                 # API route handlers
│   ├── utils/                  # Helper functions
│   └── types/                  # TypeScript type definitions
├── docs/                        # Documentation (GitHub Pages)
└── .github/workflows/           # CI/CD workflows
```

## Core Components

### 1. Task Registry (registry.json)

Central index mapping task names to file paths.

**Schema:**
```json
{
  "version": 1,
  "commit": "git-commit-hash",
  "tasks": [
    {
      "name": "TaskName",
      "path": "tasks/category/TaskName.py",
      "category": "category",
      "description": "Brief description"
    }
  ]
}
```

**Properties:**
- `version`: Registry format version (currently 1)
- `commit`: Git commit hash (auto-stamped by CI)
- `tasks`: Array of task metadata

**Access patterns:**
- Pipeline CLI reads registry to list/install tasks
- Task Wizard reads registry to show available templates
- CI validates registry matches task files

### 2. Task Files (tasks/)

Python task implementations following v2025.09 schema.

**Structure:**
```python
"""Task description."""

from __future__ import annotations
from autoclean.core.task import Task

config = {
    "schema_version": "2025.09",
    # ... configuration
}

class TaskName(Task):
    def run(self) -> None:
        # Processing pipeline
```

**Organization:**
- `resting/` - Resting-state paradigms
- `auditory/` - Auditory paradigms (ASSR, MMN, chirp)
- `visual/` - Visual paradigms (VEP)
- `rodent/` - Preclinical/animal studies

### 3. Cloudflare Worker (src/)

Backend API for Task Wizard integration.

**Technology Stack:**
- Runtime: Cloudflare Workers (edge computing)
- Router: itty-router v5
- Language: TypeScript
- Validation: Zod schemas
- GitHub Integration: Octokit

**API Endpoints:**

**GET /api/registry**
```typescript
// Returns registry.json with task metadata
Response: {
  version: number
  commit: string
  tasks: TaskEntry[]
}
```

**POST /api/tasks/pr**
```typescript
// Creates PR with new/updated task
Request: {
  taskName: string
  taskContent: string
  category: string
  description: string
}
Response: {
  prUrl: string
  prNumber: number
}
```

**Configuration (wrangler.toml):**
```toml
name = "taskwizard-registry-backend"
main = "src/index.ts"
compatibility_date = "2024-12-01"

[vars]
REGISTRY_OWNER = "cincibrainlab"
REGISTRY_REPO = "autocleaneeg-task-registry"
REGISTRY_DEFAULT_BRANCH = "main"
ALLOWED_ORIGINS = "https://taskwizard.autocleaneeg.org,..."
CACHE_TTL_SECONDS = "300"
```

**GitHub App Authentication:**
- App ID and Installation ID in environment variables
- Private key stored in Cloudflare secrets
- Creates PRs on behalf of Task Wizard

### 4. CI/CD Pipeline

**GitHub Actions Workflows:**

**registry-ci.yml** (Main validation workflow)
```yaml
Triggers: Pull requests, pushes to main
Steps:
  1. Checkout repository (fetch-depth: 0)
  2. Set up Python 3.11
  3. Run scripts/validate_registry.py
  4. Run scripts/stamp_registry_commit.py (main only)
  5. Auto-commit updated registry.json (main only)
```

**Validation checks:**
- Registry format correctness
- Task file existence
- No duplicate names/paths
- All task files registered

**Commit stamping:**
- Updates `commit` field in registry.json
- Enables version tracking
- Used by CLI for cache invalidation

## Data Flow

### Task Installation (CLI)

```
User runs: autocleaneeg-pipeline task library install TaskName
    ↓
CLI fetches: https://raw.githubusercontent.com/.../registry.json
    ↓
CLI parses registry, finds task path
    ↓
CLI downloads: https://raw.githubusercontent.com/.../tasks/category/TaskName.py
    ↓
CLI saves to: workspace/tasks/TaskName.py
```

### Task Wizard Integration

```
User creates task in Task Wizard UI
    ↓
User clicks "Publish to Registry"
    ↓
Frontend sends POST to /api/tasks/pr
    ↓
Worker authenticates with GitHub App
    ↓
Worker creates branch, commits file, updates registry.json
    ↓
Worker opens PR in repository
    ↓
CI validates PR (registry-ci.yml)
    ↓
Maintainer reviews and merges
    ↓
CI stamps commit hash
    ↓
Task available via CLI
```

## Deployment

### Cloudflare Worker

**Development:**
```bash
npm install
npm run dev          # Local development server
npm run check        # TypeScript type checking
```

**Production:**
```bash
npm run deploy       # Deploy to Cloudflare
```

**Environments:**
- Production: `taskwizard-registry-backend.workers.dev`
- Preview: Auto-deployed on PR

### GitHub Pages

**Documentation site:** `https://cincibrainlab.github.io/autocleaneeg-task-registry/`

**Configuration:**
- Source: main branch, `/docs` folder
- Theme: Jekyll (minimal or cayman)
- Build: Automatic on push to main

## Security

### GitHub App Permissions

**Required permissions:**
- Contents: Read & Write (create branches, files, PRs)
- Pull requests: Read & Write (create and update PRs)
- Metadata: Read (repository info)

**Installation:**
- Installed on: `cincibrainlab/autocleaneeg-task-registry`
- Installation ID stored in Cloudflare env vars

### API Security

**CORS:**
- Allowed origins configured in wrangler.toml
- Production: `https://taskwizard.autocleaneeg.org`
- Preview: `*` (development only)

**Rate Limiting:**
- Cloudflare Workers default rate limits
- Cache TTL: 300 seconds (5 minutes)

### Secrets Management

**Cloudflare Secrets:**
- `GITHUB_PRIVATE_KEY` - GitHub App private key (PEM format)
- `GITHUB_APP_ID` - GitHub App ID
- `GITHUB_INSTALLATION_ID` - Installation ID for repository

**Rotation policy:**
- Quarterly minimum
- After suspected compromise
- During team changes

## Monitoring

**Cloudflare Dashboard:**
- Worker invocations
- Error rates
- Response times
- Request volume

**GitHub Insights:**
- CI workflow runs
- PR velocity
- Registry commit frequency

## Scalability

**Current limits:**
- Registry size: ~100 tasks (comfortable)
- Worker: 100k requests/day (free tier)
- GitHub API: 5000 requests/hour per app

**Future considerations:**
- CDN caching for registry.json
- Pagination for large task lists
- Webhook-based cache invalidation
- Premium Cloudflare tier if needed

## Related Documentation

- [Testing Guide](testing.md) - CI/CD and validation testing
- [Integration Overview](../integration/overview.md) - Task Wizard integration details
- [Setup Guide](../integration/setup-guide.md) - GitHub App configuration