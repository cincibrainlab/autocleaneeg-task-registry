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

## Adding New Tasks

1. Create a new Python file in the appropriate category folder.
2. Add the task entry to `registry.json` (matching name and relative path).
3. Implement the task following the standard task interface.

Downstream tooling (e.g. `autocleaneeg-pipeline task builtins install RestingEyesOpen`) consumes the registry to fetch and materialize tasks for local customization.
