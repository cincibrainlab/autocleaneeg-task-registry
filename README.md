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

## Usage

The `registry.json` file provides a simple index of all available tasks with their paths. Each task is implemented as a Python module in the `tasks/` directory.

## Task Categories

- **resting**: Resting state tasks (eyes open, eyes closed, etc.)
- **auditory**: Auditory paradigms (ASSR, MMN, etc.)

## Adding New Tasks

1. Create a new Python file in the appropriate category folder
2. Add the task entry to `registry.json`
3. Implement the task following the standard task interface