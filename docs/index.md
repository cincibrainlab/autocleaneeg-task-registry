# Installation

If you already have Python available, install the pipeline CLI globally:

```sh
pipx install autocleaneeg-pipeline
# or, with uv
uv tool install autocleaneeg-pipeline
```

Then pull the latest tasks and install the one you need:

```sh
autocleaneeg-pipeline task library update
autocleaneeg-pipeline task library install P300_Grael4K
```

Inside your project, start with a minimal task config. This example time-locks to events 13 and 14, strips other annotations, and keeps BAD_* markers for rejection:

```python
config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "standard_1020"},
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -0.5, "tmax": 1.0},
        "event_id": {"13": 1, "14": 2},
        "strip_other_events": True,
        "allowed_events": ["13", "14"],
        "remove_baseline": {"enabled": False, "window": [-0.2, 0.0]},
        "threshold_rejection": {
            "enabled": False,
            "volt_threshold": {"eeg": 0.000125},
        },
    },
    # Add other steps (filtering, ICA, component_rejection, etc.) as needed
}
```

Now you’re ready to process a file:

```sh
autocleaneeg-pipeline process --task-file tasks/auditory/P300_Grael4K.py \
  --file /path/to/your_file.set \
  --output ./output \
  --yes
```

This will:
- Import your EEG file and create a BIDS-compliant output structure
- Run preprocessing (filtering, EOG handling, ICA, component rejection)
- Strip non-target annotations before epoching (keeps BAD_* markers)
- Create epochs on events 13/14 and export derivatives plus reports

Voila! If you’re just processing a single file, you’re done. For batches, point `--dir` at a folder and rerun the same command. For subsequent runs, update the registry as needed:

```sh
autocleaneeg-pipeline task library update
```
