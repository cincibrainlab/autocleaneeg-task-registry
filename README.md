# autocleaneeg-task-registry

Task registry for the AutoCleanEEG pipeline. Provides standardized task definitions and metadata for EEG experiments.

## Structure

```
├── README.md
├── registry.json              # Task index (name -> path mapping)
└── tasks/                     # Task definitions organized by category
    ├── resting/
    ├── auditory/
    └── ...
```

## Built-in Tasks

Currently the registry exposes the same built-in templates that ship with the pipeline package:

| Task | Category | Notes |
| ---- | -------- | ----- |
| `RestingEyesOpen`  | resting  | Baseline resting-state configuration tuned for eyes-open EEG |
| `RestingEyesClosed`| resting  | Variant for eyes-closed recordings with identical preprocessing stages |
| `ASSR_40Hz`        | auditory | Auditory steady-state response paradigm |
| `MMN_Standard`     | auditory | Classic mismatch negativity paradigm |

> The `commit` field in `registry.json` is intentionally left as a placeholder. A lightweight CI job can stamp it with the merge commit hash to keep local caches traceable.

## Usage

The `registry.json` file provides a simple index of all available tasks with their paths. Each task is implemented as a Python module in the `tasks/` directory.

## Task Wizard Backend

This repository also ships a Cloudflare Worker that powers the Task Wizard → Registry integration. The service is defined in `src/` and exposed via `wrangler.toml`.

- Install dependencies: `npm install`
- Start a local worker (requires Cloudflare secrets): `npm run dev`
- Run unit tests: `npm test`
- Type-check: `npm run check`

### Environment

Set the following variables in Cloudflare (or via `wrangler secret`/`--var` when running locally):

| Variable | Description |
| --- | --- |
| `REGISTRY_OWNER` | GitHub organization or user for the registry (`cincibrainlab`) |
| `REGISTRY_REPO` | Repository name (`autocleaneeg-task-registry`) |
| `REGISTRY_DEFAULT_BRANCH` | Base branch for pull requests (usually `main`) |
| `ALLOWED_ORIGINS` | Comma-separated list of origins allowed to call the API |
| `CACHE_TTL_SECONDS` | Cache duration for `/library/index` responses |
| `GITHUB_APP_ID` | GitHub App identifier |
| `GITHUB_INSTALLATION_ID` | Installation ID covering the registry repo |
| `GITHUB_PRIVATE_KEY` | Base64-encoded or PEM private key for the app |
| `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET` | OAuth identifiers for user sign-in |
| `SESSION_SECRET` | Secret for signing wizard sessions (if using session storage) |

### Endpoints

- `GET /library/index` — Returns the latest `registry.json` (with short-lived caching).
- `POST /publish` — Accepts a task payload and opens a GitHub pull request via the Task Wizard app. Supports a `dryRun` flag for validation-only checks.

## Adding New Tasks

1. Create a new Python file in the appropriate category folder.
2. Add the task entry to `registry.json` (matching name and relative path).
3. Implement the task following the standard task interface.

Downstream tooling (e.g. `autocleaneeg-pipeline task builtins install RestingEyesOpen`) consumes the registry to fetch and materialize tasks for local customization.
