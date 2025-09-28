# AutocleanEEG Task Registry

This repository is the public catalogue of EEG task templates for the AutocleanEEG ecosystem. Each task describes a complete preprocessing pipeline – the same collection of templates you see inside the Task Wizard and can install with the AutocleanEEG command‑line tools.

## How this registry helps you

### 1. Use the Task Wizard (recommended)
- Go to **https://taskwizard.autocleaneeg.org**.
- Step 1 shows the official templates from this registry – pick one or start from scratch.
- Configure the task, preview the Python output, then either download it or publish it back here with a single click.

### 2. Install templates with the AutocleanEEG CLI
Once a task is published (or updated) in this registry, you can pull it straight into your local pipeline:
```bash
autocleaneeg-pipeline task library update
autocleaneeg-pipeline task library list            # optional, view what is available
autocleaneeg-pipeline task library install <TaskName>
```
This saves `tasks/<TaskName>.py` into your project, ready for import.

### 3. Download a task directly
Prefer to grab a file manually?
- Browse `tasks/<category>/<TaskName>.py` in this repo and download the file.
- Or fetch from raw GitHub, e.g.:
  ```bash
  curl -O https://raw.githubusercontent.com/cincibrainlab/autocleaneeg-task-registry/main/tasks/resting/RestingEyesOpen.py
  ```

### 4. Inspect the index
All published tasks are listed in [`registry.json`](registry.json). Each entry maps a task name to its file path; downstream tools (Task Wizard, CLI) read this file to stay in sync.

## What’s inside the repository?
```
├── registry.json          # master index of task names and locations
└── tasks/                 # task implementations grouped by category
    ├── resting/
    ├── auditory/
    └── …
```
Sample tasks include:

| Task | Category | Notes |
| ---- | -------- | ----- |
| `RestingEyesOpen`  | resting  | Baseline eyes-open resting-state pipeline |
| `RestingEyesClosed`| resting  | Eyes-closed variant with matching preprocessing |
| `ASSR_40Hz`        | auditory | Auditory steady-state response experiment |
| `MMN_Standard`     | auditory | Mismatch negativity paradigm |
| `BiotrialResting1020` | resting | Resting-state workflow tuned for 10-20 layouts |

## Contributing a new task
The simplest path is through the Task Wizard: configure your task, run a **dry run**, then **Publish to Registry**. The wizard will open a pull request here for review.

If you need to submit manually:
1. Add `tasks/<category>/<TaskName>.py` (PascalCase, matches the class name).
2. Add the corresponding entry to `registry.json`.
3. Open a pull request targeting `main` with a short description of the task and any validation notes.

## Need help?
Reach out on the lab Slack or open an issue on GitHub. Let us know which task you’re working with and whether you’re using the Task Wizard or the CLI so we can point you in the right direction quickly.

Happy preprocessing! 🧠
