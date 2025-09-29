# Migration Guide

Guide for migrating tasks to the v2025.09 schema and current best practices.

## Quick Migration Checklist

- [ ] Convert EOG configuration to full dict format with `eog_drop`
- [ ] Add `psd_fmax` to component rejection config
- [ ] Ensure all steps present (even if `enabled: False`)
- [ ] Remove custom `__init__` methods
- [ ] Remove deprecated imports (`save_raw_to_set`, `step_create_bids_path`)
- [ ] Use explicit method calls in `run()`
- [ ] Add `schema_version: "2025.09"` to config
- [ ] Update task naming to PascalCase_With_Underscores

## Step-by-Step Migration

### 1. EOG Configuration (Breaking Change)

**Before:**
```python
"eog_step": {
    "enabled": True,
    "value": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
}
```

**After:**
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
        "eog_drop": True,
    },
}
```

**Why?**
- Explicit control over channel removal
- Schema compliance
- Prevents AttributeError in pipeline

### 2. Add psd_fmax to Component Rejection

Match your filter cutoff frequency:

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
        "psd_fmax": 80.0,  # ← Add this, matching h_freq
    },
},
```

### 3. Complete Step Definitions

Include all steps even when disabled:

**Before:**
```python
config = {
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "resample_step": {"enabled": True, "value": 500},
    # Missing other steps
}
```

**After:**
```python
config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "move_flagged_files": False,
    "resample_step": {"enabled": True, "value": 500},
    "filtering": {"enabled": True, "value": {"l_freq": 1.0, "h_freq": 80.0, "notch_freqs": [60, 120]}},
    "drop_outerlayer": {"enabled": False, "value": []},
    "eog_step": {
        "enabled": True,
        "value": {
            "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
            "eog_drop": True,
        },
    },
    "trim_step": {"enabled": True, "value": 2},
    "crop_step": {"enabled": False, "value": {"start": 0, "end": 0}},
    "reference_step": {"enabled": True, "value": "average"},
    "ICA": {"enabled": True, "value": {...}},
    "component_rejection": {"enabled": True, "method": "iclabel", "value": {...}},
    "epoch_settings": {"enabled": True, "value": {...}, "event_id": {...}, ...},
    "ai_reporting": False,
}
```

### 4. Remove Custom __init__

**Before:**
```python
class MyTask(Task):
    def __init__(self, config: Dict[str, Any]):
        self.raw = None
        self.epochs = None
        super().__init__(config)
```

**After:**
```python
class MyTask(Task):
    """Task description."""

    # No __init__ needed - Task base class handles it
```

### 5. Use Explicit Method Calls

**Before:**
```python
def run(self) -> None:
    self.import_data()  # Custom method
    self.basic_steps()  # Wrapper method
    self._generate_reports()  # Private method
```

**After:**
```python
def run(self) -> None:
    self.import_raw()
    self.resample_data()
    self.filter_data()
    self.drop_outer_layer()
    self.assign_eog_channels()
    self.trim_edges()
    self.crop_duration()

    self.original_raw = self.raw.copy()

    self.clean_bad_channels()
    self.rereference_data()

    self.annotate_noisy_epochs()
    self.annotate_uncorrelated_epochs()
    self.detect_dense_oscillatory_artifacts()

    self.run_ica()
    self.classify_ica_components(method="iclabel")

    self.create_eventid_epochs()
    self.detect_outlier_epochs()
    self.gfp_clean_epochs()

    self.generate_reports()
```

### 6. Remove Deprecated Imports

**Before:**
```python
from autoclean.io.export import save_raw_to_set
from autoclean.step_functions.continuous import step_create_bids_path

def run(self):
    self.raw = import_eeg(self.config)
    save_raw_to_set(self.raw, self.config, "post_import")
    self.raw, self.config = step_create_bids_path(self.raw, self.config)
```

**After:**
```python
# No extra imports needed

def run(self):
    self.import_raw()  # Handles import and BIDS automatically
```

## Complete Example Migration

### Before (Old Format)

```python
from typing import Any, Dict
from autoclean.core.task import Task
from autoclean.io.export import save_raw_to_set

class OldTask(Task):
    def __init__(self, config: Dict[str, Any]):
        self.raw = None
        self.epochs = None
        super().__init__(config)

    def run(self) -> None:
        self.import_data()
        self.basic_steps()
        self.create_eventid_epochs()
        self._generate_reports()

    def import_data(self):
        from autoclean.io.import_ import import_eeg
        self.raw = import_eeg(self.config)
        save_raw_to_set(self.raw, self.config, "post_import")
```

### After (New Format)

```python
"""Task description.

This task implements X protocol with Y processing.
"""

from __future__ import annotations

from autoclean.core.task import Task

config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "move_flagged_files": False,
    "resample_step": {"enabled": True, "value": 500},
    "filtering": {
        "enabled": True,
        "value": {"l_freq": 1.0, "h_freq": 80.0, "notch_freqs": [60, 120]},
    },
    "drop_outerlayer": {"enabled": False, "value": []},
    "eog_step": {
        "enabled": True,
        "value": {
            "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
            "eog_drop": True,
        },
    },
    "trim_step": {"enabled": True, "value": 2},
    "crop_step": {"enabled": False, "value": {"start": 0, "end": 0}},
    "reference_step": {"enabled": True, "value": "average"},
    "ICA": {
        "enabled": True,
        "value": {
            "method": "fastica",
            "n_components": None,
            "fit_params": {"tol": 0.0001},
            "temp_highpass_for_ica": 1.0,
        },
    },
    "component_rejection": {
        "enabled": True,
        "method": "iclabel",
        "value": {
            "ic_flags_to_reject": ["muscle", "heart", "eog", "ch_noise", "line_noise"],
            "ic_rejection_threshold": 0.3,
            "psd_fmax": 80.0,
        },
    },
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -0.2, "tmax": 0.8},
        "event_id": {"stimulus": 1},
        "remove_baseline": {"enabled": True, "window": [-0.2, 0.0]},
        "threshold_rejection": {
            "enabled": True,
            "volt_threshold": {"eeg": 0.00015},
        },
    },
    "ai_reporting": False,
}


class NewTask(Task):
    """Task description."""

    def run(self) -> None:
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.drop_outer_layer()
        self.assign_eog_channels()
        self.trim_edges()
        self.crop_duration()

        self.original_raw = self.raw.copy()

        self.clean_bad_channels()
        self.rereference_data()

        self.annotate_noisy_epochs()
        self.annotate_uncorrelated_epochs()
        self.detect_dense_oscillatory_artifacts()

        self.run_ica()
        self.classify_ica_components(method="iclabel")

        self.create_eventid_epochs()
        self.detect_outlier_epochs()
        self.gfp_clean_epochs()

        self.generate_reports()

    def generate_reports(self) -> None:
        if self.raw is None or self.original_raw is None:
            return

        self.plot_raw_vs_cleaned_overlay(self.original_raw, self.raw)
        self.step_psd_topo_figure(self.original_raw, self.raw)
```

## Troubleshooting

### Schema Validation Fails

**Error:** Task config doesn't validate against schema

**Solution:** Use `autocleaneeg-pipeline task schema export` to get current schema, compare your config

### EOG AttributeError

**Error:** `AttributeError: 'list' object has no attribute 'get'`

**Solution:** Convert EOG to full dict format (see section 1)

### Missing Methods

**Error:** `AttributeError: 'MyTask' object has no attribute 'some_method'`

**Solution:** Check that method names match Task mixin methods exactly (case-sensitive)

## Testing Your Migration

```bash
# Validate schema compliance
autocleaneeg-pipeline task schema export -o schema.json
# Then manually compare your task config

# Test with sample data
autocleaneeg-pipeline process YourTask /path/to/test/data.raw

# Verify output structure
ls -R /path/to/output/
```

## Need Help?

- See `BEST_PRACTICES.md` for development guidelines
- See `TASKS.md` for working examples
- See `EOG_CHANNEL_REFERENCE.md` for montage-specific channels
- Check pipeline docs: https://cincibrainlab.github.io/autoclean_pipeline/