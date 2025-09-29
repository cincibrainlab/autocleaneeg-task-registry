# Integration Config Template

## Project Summary
- Integration name: TaskWizard Registry Bridge
- Primary contacts (Eng / Ops): Ernest Pedapati (Engineering Lead) – ernest.pedapati@cchmc.org; Ops TBD
- Target environment(s) (dev / staging / prod) & URLs:
  - Development: Cloudflare Pages preview (branch `dev`)
  - Production: https://taskwizard.autocleaneeg.org
  - Staging: TBD

## GitHub App
- App name: TaskWizard Registry Publisher
- Owner: @drpedapati
- App ID: 2026174
- Client ID: Iv23liVGBbRdBUGhuBfz
- Client secret (storage location / rotation plan): Stored as Cloudflare secret `GITHUB_CLIENT_SECRET`; rotate quarterly or on personnel changes
- Private key file (path in secret store / rotation cadence): Cloudflare secret `GITHUB_PRIVATE_KEY` (base64 PEM); rotate quarterly
- Installation ID(s) by environment: Org installation 87783786 (repos: `cincibrainlab/autocleaneeg-task-registry`, sandbox TBD)
- Webhook secret (if used): N/A (enable later if status callbacks required)
- Sandbox repo for tests: cincibrainlab/autocleaneeg-task-registry-sandbox

## OAuth Flow
- Authorized callback URL(s): https://taskwizard.autocleaneeg.org/api/auth/github/callback
- Session storage mechanism (cookie settings / KV namespace): Secure HttpOnly cookies (SameSite=Lax) backed by Workers KV `taskwizard_sessions`
- Token lifetime & refresh policy: Installation tokens valid 1 hour; no refresh tokens—new login prompted on expiry
- Scopes requested from users: repo, read:user

## GitHub Access for Local Dev
- Personal access token owner:
- PAT scopes:
- Storage method (e.g., `.env.local`, 1Password vault):
- Test repository URL:

## Cloudflare Pages/Workers
- Account ID: e69caec9e2154819eb699abd40c63387
- Project name: autoclean-configwizard
- API token with `Pages:Edit` / `Pages:Read` / `Workers KV` (token label & storage): Token label `TaskWizard Pages Deployer`; stored in 1Password vault → sync into Cloudflare secret `CF_API_TOKEN` (rotate every 6 months)
- KV namespace IDs (if caching library data):
- Deployment command / pipeline reference: GitHub Actions `deploy-pages.yml` in `cincibrainlab/Autoclean-ConfigWizard`

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
