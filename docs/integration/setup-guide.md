# Integration Config Template Instructions

Use this guide to fill `integration_config_template.md`. Provide concrete values for each prompt; if unknown, write `TBD` and add context.

## Project Summary
- **Integration name:** Provide the codename or project title the team recognizes.
- **Primary contacts (Eng / Ops):** List names, roles, and preferred contact (email/slack) for engineering and operations leads.
- **Target environment(s) & URLs:** Enumerate each environment (development, staging, production) plus canonical URL or Cloudflare page.

## GitHub App
1. Navigate to **GitHub → Settings → Developer settings → GitHub Apps** (organization scope) and either create a new app or open the existing Task Wizard integration.
2. On the **General** tab copy these values directly into the template:
   - **App name:** The display name shown at the top of the page.
   - **App ID:** The numeric ID under "About".
   - **Client ID:** Shown under the "Client ID" heading.
3. Generate a **Client secret** by selecting "Generate a new client secret". Store the raw value immediately in your password manager, then add a note in the template describing the Cloudflare secret binding and planned rotation (minimum quarterly).
4. Scroll to **Private keys**, click "Generate a private key" to download the PEM. Base64-encode it, upload into your secret store (e.g., Cloudflare Pages secret `GITHUB_PRIVATE_KEY`), document the storage path in the template, and schedule a rotation reminder.
5. Under **Install App**, install it on `cincibrainlab/autocleaneeg-task-registry` (and sandbox repo if applicable). On the confirmation page capture the **Installation ID** (visible in the URL or via the API) and record per environment.
6. If you enable webhooks, set a **Webhook secret** and note where it is stored; otherwise record `N/A`.
7. For testing, create or reference a sandbox repository (e.g., `cincibrainlab/autocleaneeg-task-registry-sandbox`) and enter its full slug in the template.
8. There is no `gh` CLI support for GitHub App management; all the above steps must be done through the web UI or direct REST API calls.

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
1. Log into Cloudflare and select the Cincibrainlab account; the **Account ID** appears on the Overview page (right sidebar). Copy it into the template.
2. Confirm the Pages/Workers project name (e.g., `taskwizard`) from the Pages dashboard and record it.
3. Create an API token:
   - Navigate to **My Profile → API Tokens → Create Token → Custom Token**.
   - Grant permissions: `Pages · Edit`, `Pages · Read`, and `Workers KV Storage · Edit` (add others like `Pages · Create` only if required by CI).
   - Under Account Resources choose the Cincibrainlab account, then finalize.
   - Name the token `TaskWizard Pages Deployer`, copy the value once, store it in 1Password (or your secret manager), and bind it in Cloudflare as `CF_API_TOKEN`. Set a rotation reminder (every 6 months recommended).
4. If you use KV caching, create the namespace(s) from **Workers → KV** and list each namespace ID in the template; otherwise mark `N/A`.
5. Document the deployment command or CI job (e.g., `npm run deploy:pages` or GitHub Actions workflow) that publishes to Cloudflare.

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
