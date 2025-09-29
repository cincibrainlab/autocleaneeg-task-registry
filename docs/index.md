# AutoCleanEEG Task Registry

**Official task catalog for the AutoCleanEEG pipeline**

> **Note:** This is the task registry documentation. For main pipeline documentation, visit [docs.autocleaneeg.org](https://docs.autocleaneeg.org)

---

## What is the Task Registry?

The AutoCleanEEG Task Registry is a curated collection of production-ready EEG preprocessing tasks. Each task represents a complete preprocessing pipeline optimized for specific experimental paradigms (resting-state, ASSR, MMN, VEP, etc.).

**Key Features:**
- ✅ **Schema-compliant** - All tasks follow v2025.09 standard
- ✅ **Production-tested** - Validated with real EEG data
- ✅ **Well-documented** - Comprehensive parameter descriptions
- ✅ **Easy installation** - One command via CLI
- ✅ **Open source** - MIT licensed, community-driven

---

## Quick Start

### 1. Use the Task Wizard (Recommended)

Create and configure tasks visually at **[taskwizard.autocleaneeg.org](https://taskwizard.autocleaneeg.org)**

- Start from official templates or create from scratch
- Configure with plain-language options
- Preview generated Python code
- Publish directly to registry

### 2. Install via CLI

```bash
# Update task registry
autocleaneeg-pipeline task library update

# List available tasks
autocleaneeg-pipeline task library list

# Install a task
autocleaneeg-pipeline task library install RestingEyesOpen

# Process your data
autocleaneeg-pipeline process RestingEyesOpen /path/to/data.raw
```

### 3. Download Directly

Browse [`tasks/`](https://github.com/cincibrainlab/autocleaneeg-task-registry/tree/main/tasks) and download individual `.py` files:

```bash
curl -O https://raw.githubusercontent.com/cincibrainlab/autocleaneeg-task-registry/main/tasks/resting/RestingEyesOpen.py
```

---

## Available Tasks

See **[Task Catalog](TASKS.md)** for complete directory with quick reference table.

### By Category

**[Resting State](TASKS.md#resting-state-tasksresting)** (5 tasks)
- RestingEyesOpen, RestingEyesClosed, RestingState_WaveletOnly, etc.

**[Auditory](TASKS.md#auditory-tasksauditory)** (5 tasks)
- ASSR_40Hz, MMN_Standard, Chirp_Default, BB_Long, HBCD_MMN

**[Visual](TASKS.md#visual-tasksvisual)** (1 task)
- HBCD_VEP

**[Rodent](TASKS.md#rodent-tasksrodent)** (3 tasks)
- Mouse_XDAT_ASSR, Mouse_XDAT_Chirp, Mouse_XDAT_Resting

---

## Documentation

### User Guides
- **[Task Catalog](TASKS.md)** - Complete task directory with parameters and use cases
- **[EOG Channel Reference](EOG_CHANNEL_REFERENCE.md)** - Montage-specific EOG channel mappings
- **[Migration Guide](MIGRATION.md)** - Upgrading tasks to v2025.09 schema
- **[FAQ](FAQ.md)** - Common questions and troubleshooting

### Developer Guides
- **[Best Practices](BEST_PRACTICES.md)** - Task development guidelines
- **[Testing](development/testing.md)** - CI/CD and validation testing
- **[Architecture](development/architecture.md)** - Infrastructure overview

### Integration
- **[Task Wizard Overview](integration/overview.md)** - Integration architecture and workflow
- **[Config Template](integration/config-template.md)** - GitHub App configuration
- **[Setup Guide](integration/setup-guide.md)** - Step-by-step integration setup

---

## Contributing

### Quick Contribution

**Via Task Wizard:**
1. Create your task at [taskwizard.autocleaneeg.org](https://taskwizard.autocleaneeg.org)
2. Test with dry run
3. Click "Publish to Registry" → automatic PR

**Manual Submission:**
1. Fork repository
2. Create `tasks/<category>/<TaskName>.py`
3. Add entry to `registry.json`
4. Update `docs/TASKS.md`
5. Open pull request

### Contribution Checklist
- [ ] Task follows v2025.09 schema
- [ ] EOG uses full dict format with `eog_drop`
- [ ] All steps present in config (even if disabled)
- [ ] Tested with real data
- [ ] Added to `registry.json` with metadata
- [ ] Documented in `TASKS.md`

See **[Best Practices](BEST_PRACTICES.md)** for detailed guidelines.

---

## Schema Version

All tasks follow **v2025.09** schema:
- Module-level `config` dictionary
- No custom `__init__` methods
- Explicit method calls in `run()`
- Complete step definitions
- Full EOG dict format

**Example:**
```python
"""Task description."""

from __future__ import annotations
from autoclean.core.task import Task

config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "eog_step": {
        "enabled": True,
        "value": {
            "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
            "eog_drop": True,
        },
    },
    # ... complete configuration
}

class TaskName(Task):
    def run(self) -> None:
        self.import_raw()
        self.resample_data()
        # ... explicit processing steps
```

---

## Resources

- **Pipeline Docs**: [docs.autocleaneeg.org](https://docs.autocleaneeg.org)
- **Task Wizard**: [taskwizard.autocleaneeg.org](https://taskwizard.autocleaneeg.org)
- **GitHub**: [cincibrainlab/autocleaneeg-task-registry](https://github.com/cincibrainlab/autocleaneeg-task-registry)
- **Issues**: [Report bugs or request features](https://github.com/cincibrainlab/autocleaneeg-task-registry/issues)

---

**Schema Version**: 2025.09 | **Last Updated**: 2025-09-29
