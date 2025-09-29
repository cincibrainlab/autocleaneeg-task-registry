# Best Practices for Task Development

Guidelines for creating high-quality, maintainable task files.

## Task Structure

### 1. Module-Level Configuration

Always define config at module level, not in class:

```python
# ✅ Correct
config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    # ... rest of config
}

class MyTask(Task):
    """Task description."""
    pass

# ❌ Wrong
class MyTask(Task):
    def __init__(self):
        self.config = {...}  # Don't do this
```

### 2. No Custom __init__

Let the Task base class handle initialization:

```python
# ✅ Correct
class MyTask(Task):
    """Task description."""

    def run(self) -> None:
        self.import_raw()

# ❌ Wrong
class MyTask(Task):
    def __init__(self, config):
        self.raw = None
        super().__init__(config)  # Unnecessary
```

### 3. Explicit Method Calls

Use explicit method names instead of wrapper functions:

```python
# ✅ Correct - Transparent, easy to understand
def run(self) -> None:
    self.import_raw()
    self.resample_data()
    self.filter_data()
    self.drop_outer_layer()
    self.assign_eog_channels()

# ❌ Wrong - Hidden complexity
def run(self) -> None:
    self.import_data()  # What does this do?
    self.basic_steps()  # What steps?
```

### 4. Preserve original_raw Reference

Always keep a copy of pre-cleaned data for comparison:

```python
def run(self) -> None:
    self.import_raw()
    # ... basic preprocessing

    self.original_raw = self.raw.copy()  # ← Important!

    # ... artifact removal
    self.clean_bad_channels()
    self.run_ica()

    # Now can compare original vs cleaned
    self.generate_reports()

def generate_reports(self) -> None:
    if self.raw is None or self.original_raw is None:
        return

    self.plot_raw_vs_cleaned_overlay(self.original_raw, self.raw)
    self.step_psd_topo_figure(self.original_raw, self.raw)
```

## Configuration Best Practices

### 1. Complete Step Definitions

Include all steps even if disabled:

```python
config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "move_flagged_files": False,
    "resample_step": {"enabled": True, "value": 500},
    "filtering": {
        "enabled": True,
        "value": {"l_freq": 1.0, "h_freq": 80.0, "notch_freqs": [60, 120]},
    },
    "drop_outerlayer": {"enabled": False, "value": []},  # ← Include even if disabled
    "eog_step": {
        "enabled": False,  # ← Even disabled steps need full structure
        "value": {
            "eog_indices": [],
            "eog_drop": False,
        },
    },
    # ... all other steps
}
```

### 2. EOG Configuration Patterns

**Human EEG (with EOG):**
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
        "eog_drop": True,  # Remove after ICA
    },
}
```

**Rodent/Animal (no EOG):**
```python
"eog_step": {
    "enabled": False,
    "value": {
        "eog_indices": [],
        "eog_drop": False,
    },
}
```

**Keep EOG channels (rare):**
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
        "eog_drop": False,  # Keep in final dataset
    },
}
```

### 3. Match psd_fmax to Filter Cutoff

```python
"filtering": {
    "enabled": True,
    "value": {"l_freq": 1.0, "h_freq": 80.0, "notch_freqs": [60, 120]},
},
"component_rejection": {
    "enabled": True,
    "method": "iclabel",
    "value": {
        "ic_flags_to_reject": ["muscle", "heart", "eog", "ch_noise", "line_noise"],
        "ic_rejection_threshold": 0.3,
        "psd_fmax": 80.0,  # ← Matches h_freq
    },
},
```

### 4. ICA Method Selection

**FastICA (default, most common):**
```python
"ICA": {
    "enabled": True,
    "value": {
        "method": "fastica",
        "n_components": None,
        "fit_params": {"tol": 0.0001},
        "temp_highpass_for_ica": 1.0,
    },
}
```

**Infomax (better for muscle artifacts):**
```python
"ICA": {
    "enabled": True,
    "value": {
        "method": "infomax",
        "n_components": None,
        "fit_params": {"extended": True},
        "temp_highpass_for_ica": 1.0,
    },
}
```

### 5. Epoch Settings Patterns

**Event-Related (stimulus-locked):**
```python
"epoch_settings": {
    "enabled": True,
    "value": {"tmin": -0.2, "tmax": 0.8},
    "event_id": {"stimulus": 1, "deviant": 2},
    "remove_baseline": {"enabled": True, "window": [-0.2, 0.0]},
    "threshold_rejection": {
        "enabled": True,
        "volt_threshold": {"eeg": 0.00015},  # 150 µV
    },
}
```

**Resting-State (regular epochs):**
```python
"epoch_settings": {
    "enabled": True,
    "value": {"tmin": -1.0, "tmax": 1.0},  # 2-second epochs
    "event_id": None,  # ← No events for resting
    "remove_baseline": {"enabled": False, "window": [None, 0]},
    "threshold_rejection": {
        "enabled": False,
        "volt_threshold": {"eeg": 0.000125},
    },
}
```

## Documentation Best Practices

### 1. Comprehensive Docstrings

```python
"""Task name and brief description.

This task implements the X protocol with Y processing for Z use case.
Includes comprehensive artifact rejection and quality control visualizations.

Montage: GSN-HydroCel-129 (129-channel EGI net)
EOG Channels: E1, E32, E8, E14, E17, E21, E25, E125, E126, E127, E128 (11 channels)
"""
```

### 2. Naming Conventions

- **Task Classes**: PascalCase_With_Underscores
  - ✅ `HBCD_VEP`, `Mouse_XDAT_ASSR`, `Chirp_Default`
  - ❌ `HBCDVep`, `mouseXDATassr`, `chirpdefault`

- **Config Keys**: snake_case
  - ✅ `resample_step`, `eog_indices`, `psd_fmax`
  - ❌ `ResampleStep`, `EOGIndices`, `PSDFmax`

- **Event IDs**: lowercase or UPPERCASE
  - ✅ `{"standard": 1, "deviant": 2}` or `{"ASSR": 1}`
  - ❌ `{"Standard": 1}` (mixed case)

### 3. File Organization

```
tasks/
├── resting/
│   ├── RestingEyesOpen.py
│   ├── RestingEyesClosed.py
│   └── RestingState_WaveletOnly.py
├── auditory/
│   ├── ASSR_40Hz.py
│   ├── MMN_Standard.py
│   └── Chirp_Default.py
├── visual/
│   └── HBCD_VEP.py
└── rodent/
    ├── Mouse_XDAT_ASSR.py
    └── Mouse_XDAT_Chirp.py
```

## Testing Best Practices

### 1. Validate Schema Compliance

```bash
# Export current schema
autocleaneeg-pipeline task schema export -o schema.json

# Manually verify your task config matches schema
```

### 2. Test with Real Data

```bash
# Test on single file first
autocleaneeg-pipeline process YourTask /path/to/test/data.raw

# Check output structure
ls -R /path/to/output/

# Verify BIDS derivatives
tree /path/to/output/derivatives/
```

### 3. Verify Channel Indices During Development

```python
def run(self) -> None:
    self.import_raw()

    # Temporary validation (remove after verification)
    eog_indices = [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128]
    max_channels = len(self.raw.ch_names)
    for idx in eog_indices:
        if idx > max_channels:
            print(f"Warning: EOG index {idx} exceeds channel count {max_channels}")

    # Continue with processing...
```

## Common Pitfalls

### ❌ Don't: Mix Import Styles

```python
# Wrong - mixing old and new imports
from autoclean.core.task import Task
from autoclean.io.export import save_raw_to_set  # Deprecated
```

### ❌ Don't: Use Wrapper Methods

```python
# Wrong - hides what's actually happening
def run(self):
    self.preprocessing()  # What does this do?
    self.artifact_removal()  # What methods are called?
```

### ❌ Don't: Skip Disabled Steps

```python
# Wrong - missing disabled steps
config = {
    "resample_step": {"enabled": True, "value": 500},
    # Missing drop_outerlayer, crop_step, etc.
}
```

### ✅ Do: Be Explicit and Complete

```python
# Correct - clear, explicit, complete
config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "move_flagged_files": False,
    "resample_step": {"enabled": True, "value": 500},
    "drop_outerlayer": {"enabled": False, "value": []},
    "crop_step": {"enabled": False, "value": {"start": 0, "end": 0}},
    # ... all steps included
}

def run(self) -> None:
    self.import_raw()
    self.resample_data()
    self.filter_data()
    # ... all methods explicit
```

## Performance Tips

### 1. ICA Component Count

```python
# Auto-select (recommended for most cases)
"n_components": None  # Uses min(n_channels, n_samples)

# Manual selection (for very high-density arrays)
"n_components": 60  # Cap at 60 for faster processing
```

### 2. Temporary Highpass for ICA

```python
# Standard (recommended)
"temp_highpass_for_ica": 1.0  # Remove slow drifts

# Aggressive (for very noisy data)
"temp_highpass_for_ica": 2.0  # More aggressive drift removal
```

### 3. Epoch Rejection Thresholds

```python
# Conservative (keeps more data)
"volt_threshold": {"eeg": 0.0002}  # 200 µV

# Standard (balanced)
"volt_threshold": {"eeg": 0.00015}  # 150 µV

# Aggressive (stricter quality)
"volt_threshold": {"eeg": 0.0001}  # 100 µV
```

## Resources

- **Task Examples**: See `TASKS.md` for complete task catalog
- **Migration Guide**: See `MIGRATION.md` for upgrading old tasks
- **EOG Reference**: See `EOG_CHANNEL_REFERENCE.md` for montage channels
- **Pipeline Docs**: https://cincibrainlab.github.io/autoclean_pipeline/