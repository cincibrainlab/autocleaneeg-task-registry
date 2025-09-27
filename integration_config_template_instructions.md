# Integration Config Template Instructions

Use this guide to fill `integration_config_template.md`. Provide concrete values for each prompt; if unknown, write `TBD` and add context.

## Project Summary
- **Integration name:** Provide the codename or project title the team recognizes.
- **Primary contacts (Eng / Ops):** List names, roles, and preferred contact (email/slack) for engineering and operations leads.
- **Target environment(s) & URLs:** Enumerate each environment (development, staging, production) plus canonical URL or Cloudflare page.

## GitHub App
- **App name:** Official name registered in GitHub Apps settings.
- **App ID:** Numeric identifier visible in the GitHub App settings.
- **Client ID:** The OAuth client identifier; copy from GitHub App > General.
- **Client secret:** Describe where the secret is stored (e.g., Cloudflare env var) and how often it rotates.
- **Private key file:** Note the storage path or secret name holding the PEM, plus planned rotation cadence.
- **Installation ID(s):** Map each environment to the installation ID associated with that repo.
- **Webhook secret:** If webhooks are enabled, record the secret value location; otherwise mark `N/A`.
- **Sandbox repo for tests:** Provide the GitHub repository used for dry runs (e.g., `org/repo-sandbox`).

## OAuth Flow
- **Authorized callback URL(s):** List every callback URL registered for the app, separated per environment.
- **Session storage mechanism:** Specify cookie settings (domain, SameSite) or KV namespace name used for session persistence.
- **Token lifetime & refresh policy:** Document expiration times, refresh strategy, and whether refresh tokens are used.
- **Scopes requested from users:** List GitHub scopes (e.g., `repo`, `read:user`) and justify unusual scopes.

## GitHub Access for Local Dev
- **Personal access token owner:** Name the maintainer whose PAT is used for local or CI testing.
- **PAT scopes:** Enumerate scopes granted to the PAT.
- **Storage method:** Describe how the PAT is stored securely (password manager, `.env.local` excluded from git, etc.).
- **Test repository URL:** Provide the URL of the repository used for local integration tests.

## Cloudflare Pages/Workers
- **Account ID:** Record the Cloudflare account identifier (available in dashboard).
- **Project name:** Name of the Cloudflare Pages or Workers project hosting the backend.
- **API token:** Include token label, granted permissions (`Pages:Edit`, `Pages:Read`, `Workers KV Write`), and storage location.
- **KV namespace IDs:** List namespace IDs for any KV stores used (e.g., caching registry data) or mark `N/A`.
- **Deployment command / pipeline:** Document the command or CI job that triggers deployment.

## Backend Secrets in Cloudflare
- **`GITHUB_APP_ID`:** Note the actual value or secret binding name.
- **`GITHUB_CLIENT_ID`:** Provide the stored value or binding.
- **`GITHUB_CLIENT_SECRET`:** Reference the secret binding name and rotation policy.
- **`GITHUB_PRIVATE_KEY`:** Describe the encoding (PEM base64) and where it's stored.
- **`GITHUB_INSTALLATION_ID`:** Provide the ID value or per-environment mapping.
- **Additional env vars:** Enumerate other required secrets (e.g., `SESSION_SECRET`, `SENTRY_DSN`), each with storage details.

## CI / Registry
- **Repository CI updates required:** List new workflow files, branch protection changes, or required status checks.
- **Secrets added to GitHub Actions:** Document names of new repository or organization secrets added for CI.
- **Webhook endpoints:** Specify endpoints or services notified when wizard publishes occur; use `N/A` if not applicable.

## Observability & Alerts
- **Logging destination:** Identify where logs are shipped (Cloudflare logs UI, Logpush, external aggregator).
- **Error tracking service & DSN:** Provide service name (e.g., Sentry) and stored DSN reference.
- **Alert channels & thresholds:** Document channels (Slack room, email list) and alerting rules or runbooks.

## Usage Analytics (optional)
- **Provider & API key:** Name analytics platform and secret location; mark `N/A` if none.
- **Event/metric naming:** Outline naming conventions or link to the analytics schema.
- **Opt-in handling:** Explain how user consent is obtained or stored.

## Security & Compliance
- **Key rotation schedule:** Provide rotation cadence and owner responsible.
- **Access control:** List who can read/update secrets and how access is audited.
- **Audit logging approach:** Describe tools or processes capturing access and deployment logs.

## Outstanding Questions
- **Pending decisions:** Capture unresolved items needing stakeholder input.
- **External approvals needed:** Note security, legal, or IT approvals required before launch.
- **Next review date:** Set the date for revisiting this configuration.

Mark any unknown entries as `TBD`, and include context or blockers so they can be resolved.
