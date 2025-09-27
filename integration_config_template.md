# Integration Config Template

## Project Summary
- Integration name: TaskWizard Registry Bridge
- Primary contacts (Eng / Ops): Ernest Pedapati (Engineering Lead) – ernest.pedapati@cchmc.org; Ops TBD
- Target environment(s) (dev / staging / prod) & URLs:

## GitHub App
- App name:
- App ID:
- Client ID:
- Client secret (storage location / rotation plan):
- Private key file (path in secret store / rotation cadence):
- Installation ID(s) by environment:
- Webhook secret (if used):
- Sandbox repo for tests:

## OAuth Flow
- Authorized callback URL(s):
- Session storage mechanism (cookie settings / KV namespace):
- Token lifetime & refresh policy:
- Scopes requested from users:

## GitHub Access for Local Dev
- Personal access token owner:
- PAT scopes:
- Storage method (e.g., `.env.local`, 1Password vault):
- Test repository URL:

## Cloudflare Pages/Workers
- Account ID:
- Project name:
- API token with `Pages:Edit` / `Pages:Read` / `Workers KV` (token label & storage):
- KV namespace IDs (if caching library data):
- Deployment command / pipeline reference:

## Backend Secrets in Cloudflare
- `GITHUB_APP_ID`:
- `GITHUB_CLIENT_ID`:
- `GITHUB_CLIENT_SECRET`:
- `GITHUB_PRIVATE_KEY` (encoded format):
- `GITHUB_INSTALLATION_ID`:
- Additional env vars (e.g., `SESSION_SECRET`, `SENTRY_DSN`):

## CI / Registry
- Repository CI updates required (branch protections, labels, workflows):
- Secrets added to GitHub Actions:
- Webhook endpoints (if notifying wizard):

## Observability & Alerts
- Logging destination (Cloudflare logs / external):
- Error tracking service & DSN:
- Alert channels (Slack / email) & thresholds:

## Usage Analytics (optional)
- Provider & API key:
- Event/metric naming conventions:
- Opt-in handling:

## Security & Compliance
- Key rotation schedule:
- Access control (who can view/update secrets):
- Audit logging approach:

## Outstanding Questions
- Pending decisions:
- External approvals needed:
- Next review date:
