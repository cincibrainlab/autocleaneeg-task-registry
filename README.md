# autocleaneeg-task-registry

Public registry of EEG task templates for the AutocleanEEG pipeline. This repo is the source of truth for the Task Wizard web app and the `autocleaneeg-pipeline` CLI.

## Who this is for

- **Scientists and analysts** who want to start from lab-approved templates, publish new tasks, or install tasks locally.
- **Maintainers** who operate the Task Wizard backend or review incoming templates.

## Quick start for scientists

1. **Open the Task Wizard** → <https://taskwizard.autocleaneeg.org>
2. **Pick a template** from Step 1 (the list mirrors `registry.json`).
3. Configure, preview, and optionally download the generated Python file.
4. When ready, use the **Publish to Task Registry** panel in Step 9:
   - `Validate (Dry Run)` first to make sure the task passes naming and schema checks.
   - Toggle off dry run and hit `Publish to Registry` to open a GitHub pull request via the wizard.
5. After the PR is merged, install the task locally:

   ```bash
   autocleaneeg-pipeline task library update
   autocleaneeg-pipeline task library install <TaskName>
   ```

   Replace `<TaskName>` with the PascalCase name you published.

## Repository layout

```
├── registry.json          # Index of all published tasks (name/path pairs)
├── tasks/                 # Task implementations organised by category
│   ├── resting/
│   ├── auditory/
│   └── …
└── src/                   # Cloudflare Worker powering the Task Wizard API
```

## Publishing a task

### Preferred path (Task Wizard)

1. Complete your configuration in the wizard.
2. Fill out the publish form (task name, category, optional summary, GitHub handle).
3. Run a dry run to confirm validation succeeds.
4. Publish; reviewers receive a pull request with your generated task and metadata.

### Manual path (expert users)

1. Add `tasks/<category>/<TaskName>.py` (PascalCase, matches class name).
2. Add `{ "name": "TaskName", "path": "tasks/<category>/<TaskName>.py" }` to `registry.json` (keep entries alphabetised).
3. Run `npm run check && npm test`.
4. Open a GitHub PR targeting `main`.

## Installing and using tasks locally

- Update the local registry snapshot: `autocleaneeg-pipeline task library update`
- List tasks: `autocleaneeg-pipeline task library list`
- Install a task: `autocleaneeg-pipeline task library install <TaskName>`

The CLI will download the task file from this repository and place it in your project’s task library.

## Maintainer notes (Cloudflare Worker)

The Task Wizard backend lives in `src/` and is deployed as a Cloudflare Worker.

- Install dependencies: `npm install`
- Type check: `npm run check`
- Unit tests: `npm test`
- Deploy: `npx wrangler deploy`

### Required environment/secret variables

| Variable | Purpose |
| --- | --- |
| `REGISTRY_OWNER`, `REGISTRY_REPO`, `REGISTRY_DEFAULT_BRANCH` | GitHub repo metadata |
| `ALLOWED_ORIGINS` | Comma-separated list of trusted Task Wizard origins; wildcard suffixes are handled in code |
| `CACHE_TTL_SECONDS` | Cache lifetime for `/library/index` |
| `GITHUB_APP_ID`, `GITHUB_INSTALLATION_ID`, `GITHUB_PRIVATE_KEY` | Credentials for the Task Wizard GitHub App |
| `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET` | OAuth values if user sign-in is enabled |
| `SESSION_SECRET` | Optional session signing secret |

### API endpoints

- `GET /library/index` – returns the current `registry.json` with caching and CORS.
- `POST /publish` – validates payloads and opens PRs (supports `dryRun`).
- `POST /export/python` – generates a Python task server-side for the wizard’s download button.

### CORS

The worker allows the production domain (`https://taskwizard.autocleaneeg.org`) and any Cloudflare Pages preview that ends with `.autoclean-configwizard.pages.dev`. Add additional origins via `ALLOWED_ORIGINS` if you spin up new environments.

## Need help?

Open an issue or contact the AutocleanEEG team on Slack. Let us know which task you’re working on and whether you’re using the wizard or the CLI so we can assist quickly.
