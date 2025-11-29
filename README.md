# AutocleanEEG Task Registry

This repository is the public catalogue of EEG task templates for the AutocleanEEG ecosystem. Each task describes a complete preprocessing pipeline – the same collection of templates you see inside the Task Wizard and can install with the AutocleanEEG command‑line tools.

📚 **Documentation**: [https://cincibrainlab.github.io/autocleaneeg-task-registry/](https://cincibrainlab.github.io/autocleaneeg-task-registry/)

## Quick Start

### 1. Use the Task Wizard (recommended)
- Go to **https://taskwizard.autocleaneeg.org**.
- Step 1 shows the official templates from this registry – pick one or start from scratch.
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
- Or fetch from raw GitHub:
  ```bash
  curl -O https://raw.githubusercontent.com/cincibrainlab/autocleaneeg-task-registry/main/tasks/resting/RestingEyesOpen.py
  ```

## Repository Structure

```
├── registry.json              # Master index of task names and locations
├── CHANGELOG.md               # Version history and breaking changes
├── docs/                      # Documentation (GitHub Pages)
│   ├── index.md               # Documentation landing page
│   ├── TASKS.md               # Comprehensive task directory
│   ├── EOG_CHANNEL_REFERENCE.md # Montage-specific EOG mappings
│   ├── MIGRATION.md           # Migration guide for v2025.09
│   ├── BEST_PRACTICES.md      # Development guidelines
│   ├── FAQ.md                 # Frequently asked questions
│   ├── integration/           # Task Wizard integration docs
│   └── development/           # Infrastructure and testing docs
└── tasks/                     # Task implementations grouped by category
    ├── resting/               # Resting-state paradigms
    ├── auditory/              # Auditory paradigms (ASSR, MMN, chirp)
    ├── visual/                # Visual paradigms (VEP)
    └── rodent/                # Preclinical/rodent paradigms
```

## Available Tasks

See **[Task Catalog](https://cincibrainlab.github.io/autocleaneeg-task-registry/TASKS.html)** for comprehensive directory with quick reference table.

### Resting State (`tasks/resting/`)
- **RestingEyesOpen** - Baseline eyes-open resting-state with FastICA
- **RestingEyesClosed** - Eyes-closed variant with alpha rhythm analysis
- **RestingState_WaveletOnly** - Wavelet-based denoising without ICA
- **RestingEyesQuickCheck** - Quick quality check for resting data
- **BiotrialResting1020** - Standard 10-20 montage workflow
- **RestingState_SourcePSD** - Complete pipeline with MNE source localization and ROI PSD analysis

### Auditory (`tasks/auditory/`)
- **ASSR_40Hz** - Auditory steady-state response at 40 Hz
- **MMN_Standard** - Mismatch negativity (oddball paradigm)
- **Chirp_Default** - Chirp auditory stimulation
- **BB_Long** - Long-duration broadband stimulation
- **HBCD_MMN** - HBCD consortium mismatch negativity protocol

### Visual (`tasks/visual/`)
- **HBCD_VEP** - HBCD consortium visual evoked potential protocol

### Rodent (`tasks/rodent/`)
- **Mouse_XDAT_ASSR** - Mouse ASSR with correlation-based artifact rejection
- **Mouse_XDAT_Chirp** - Mouse chirp with correlation-based artifact rejection
- **Mouse_XDAT_Resting** - Mouse resting-state with correlation-based artifact rejection
- **Mouse_ASSR_40Hz** - Mouse 40Hz ASSR with TTL pulse event detection (MEA30 montage)
- **Mouse_ASSR_80Hz** - Mouse 80Hz ASSR with TTL pulse event detection (MEA30 montage)

## Task Schema Version

All tasks follow the **v2025.09** schema with:
- Module-level `config` dictionary
- No custom `__init__` methods
- Explicit method calls in `run()`
- Complete step definitions (even if `enabled: False`)
- Full EOG dict format with explicit `eog_drop` control

Example task structure:
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
    # ... complete config
}

class TaskName(Task):
    """Task description."""

    def run(self) -> None:
        self.import_raw()
        self.resample_data()
        # ... explicit method calls
```

## Documentation

Full documentation available at **[cincibrainlab.github.io/autocleaneeg-task-registry](https://cincibrainlab.github.io/autocleaneeg-task-registry/)**

- **[Task Catalog](docs/TASKS.md)** - Complete task directory with parameters
- **[EOG Reference](docs/EOG_CHANNEL_REFERENCE.md)** - Montage-specific EOG channels
- **[Migration Guide](docs/MIGRATION.md)** - Upgrading to v2025.09 schema
- **[Best Practices](docs/BEST_PRACTICES.md)** - Task development guidelines
- **[FAQ](docs/FAQ.md)** - Common questions and troubleshooting
- **[CHANGELOG](CHANGELOG.md)** - Version history and breaking changes

## Contributing a New Task

### Via Task Wizard (Recommended)
1. Configure your task at https://taskwizard.autocleaneeg.org
2. Run a **dry run** to test
3. Click **Publish to Registry** to open a pull request

### Manual Submission
1. Create `tasks/<category>/<TaskName>.py` (PascalCase_With_Underscores)
2. Follow v2025.09 schema (see `docs/BEST_PRACTICES.md`)
3. Test with real data
4. Add entry to `registry.json` with category and description
5. Update `docs/TASKS.md` with task details
6. Open pull request with validation notes

### Contribution Checklist
- [ ] Task follows v2025.09 schema pattern
- [ ] EOG configuration uses full dict format with `eog_drop`
- [ ] All steps present in config (even if disabled)
- [ ] Tested with real data
- [ ] Added to `registry.json` with category/description
- [ ] Documented in `docs/TASKS.md`
- [ ] Includes comprehensive docstring

## Common Use Cases

### Research Workflow
```bash
# Install pipeline
pip install autocleaneeg-pipeline

# Update task registry
autocleaneeg-pipeline task library update

# Install specific task
autocleaneeg-pipeline task library install RestingEyesOpen

# Process data
autocleaneeg-pipeline process RestingEyesOpen /path/to/data.raw
```

### Custom Task Development
```bash
# Copy reference task
cp tasks/resting/RestingEyesOpen.py ~/my_workspace/tasks/MyCustomTask.py

# Edit configuration
# ... modify config dict as needed

# Test with sample data
autocleaneeg-pipeline process ~/my_workspace/tasks/MyCustomTask.py /path/to/test.raw
```

## Need Help?

- **Questions?** Open an issue on GitHub or reach out on lab Slack
- **Bug reports?** Include task name, pipeline version, and error message
- **Feature requests?** Describe your use case and proposed changes

## Resources

- **Task Registry Docs**: https://cincibrainlab.github.io/autocleaneeg-task-registry/
- **Pipeline Documentation**: https://cincibrainlab.github.io/autoclean_pipeline/
- **Task Wizard**: https://taskwizard.autocleaneeg.org
- **GitHub Issues**: https://github.com/cincibrainlab/autocleaneeg-task-registry/issues

---

**Schema Version**: 2025.09
**Last Updated**: 2025-09-29

Happy preprocessing! 🧠