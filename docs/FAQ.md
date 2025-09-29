# Frequently Asked Questions

Common questions about task development and the registry.

## General Questions

### What is the task registry?

The task registry is a separate repository containing validated, production-ready task files for AutoClean EEG. It provides:
- Schema-compliant task configurations
- Tested processing pipelines for common paradigms
- Reference implementations for custom task development

### What's the difference between the registry and pipeline repos?

- **Pipeline** (`autocleaneeg_pipeline`): Core processing engine, mixins, CLI tools
- **Registry** (`autocleaneeg-task-registry`): Validated task files, documentation, examples

Users typically install the pipeline and use/customize tasks from the registry.

### What schema version should I use?

Always use `"schema_version": "2025.09"` for new tasks. This is the current stable schema.

## Configuration Questions

### Why do I need the full dict format for EOG?

**Short answer:** Schema compliance and explicit control.

**Long answer:** The dict format with `eog_drop` lets you:
1. Explicitly control whether EOG channels are removed after ICA
2. Comply with pipeline schema validation
3. Avoid AttributeError when pipeline expects dict format

See `MIGRATION.md` for examples.

### What's the difference between FastICA and Infomax?

- **FastICA**: Fast, deterministic, good for most applications
- **Infomax (Extended)**: Better for super-Gaussian sources (muscle artifacts), takes longer

Recommendation: Use FastICA unless you have heavy muscle contamination.

### Why include disabled steps in config?

Schema compliance requires all steps to be defined. This:
1. Makes configs self-documenting (you can see all available options)
2. Simplifies schema validation
3. Prevents KeyError when pipeline checks step existence

### What's psd_fmax and why does it matter?

`psd_fmax` sets the frequency ceiling for PSD (power spectral density) plots in ICA component visualization.

Match it to your filter cutoff:
```python
"filtering": {"value": {"h_freq": 80.0}},
"component_rejection": {"value": {"psd_fmax": 80.0}},
```

This ensures visualizations show the full frequency range of your filtered data.

### When should I use event_id vs None?

- **Event-Related (with triggers)**: Use `event_id` dict
  ```python
  "event_id": {"standard": 1, "deviant": 2}
  ```
  Then call `self.create_eventid_epochs()`

- **Resting-State (continuous)**: Use `None`
  ```python
  "event_id": None
  ```
  Then call `self.create_regular_epochs()`

## Task Development Questions

### Do I need a custom __init__ method?

**No.** The Task base class handles initialization. Just define your config and run() method:

```python
config = {...}

class MyTask(Task):
    def run(self) -> None:
        self.import_raw()
        # ... processing steps
```

### Can I add custom methods to my task?

Yes, but prefer using existing mixin methods when possible:

```python
class MyTask(Task):
    def run(self) -> None:
        self.import_raw()
        self.my_custom_preprocessing()  # ← Custom method OK
        self.filter_data()  # ← Prefer mixin methods

    def my_custom_preprocessing(self) -> None:
        # Your custom logic here
        pass
```

### How do I know what mixin methods are available?

Check the pipeline documentation or look at existing tasks in the registry. Common methods:
- `import_raw()`, `resample_data()`, `filter_data()`
- `assign_eog_channels()`, `trim_edges()`, `crop_duration()`
- `clean_bad_channels()`, `rereference_data()`
- `run_ica()`, `classify_ica_components()`
- `create_eventid_epochs()`, `create_regular_epochs()`
- `detect_outlier_epochs()`, `gfp_clean_epochs()`

### Should I use create_eventid_epochs() or create_regular_epochs()?

- **create_eventid_epochs()**: Stimulus-locked epochs (ERPs, MMN, VEP, etc.)
  - Requires `event_id` dict in config
  - Creates epochs around stimulus onsets

- **create_regular_epochs()**: Fixed-duration non-overlapping epochs (resting-state)
  - Uses `event_id: None` in config
  - Creates regular 1-2 second epochs for continuous data

### Why should I keep original_raw?

For quality control comparisons. Many reporting functions need both pre- and post-cleaned data:

```python
def run(self) -> None:
    self.import_raw()
    # ... basic preprocessing

    self.original_raw = self.raw.copy()  # ← Keep original

    # ... artifact removal
    self.clean_bad_channels()
    self.run_ica()

def generate_reports(self) -> None:
    # Compare original vs cleaned
    self.plot_raw_vs_cleaned_overlay(self.original_raw, self.raw)
    self.step_psd_topo_figure(self.original_raw, self.raw)
```

## Montage Questions

### What montages are supported?

Common montages in the registry:
- `GSN-HydroCel-129` - EGI 129-channel net
- `GSN-HydroCel-124` - EGI 124-channel net
- `standard_1020` - Standard 10-20 clinical system
- `Grael_4K` - TMSi Grael system
- `MEA30` - Rodent 30-channel microelectrode array

See `EOG_CHANNEL_REFERENCE.md` for EOG channel mappings per montage.

### How do I find EOG channel indices for my montage?

Check `EOG_CHANNEL_REFERENCE.md` in the registry. Examples:

**EGI GSN-129:**
```python
"eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128]
```

**Standard 10-20:**
```python
"eog_indices": [31, 32]  # Fp1, Fp2
```

**Rodent systems:**
```python
"eog_indices": []  # Usually no EOG for animal recordings
```

### What if my montage isn't listed?

1. Use `raw.ch_names` to inspect channel names
2. Identify channels near eyes (Fp1, Fp2, or periocular positions)
3. Add those indices to `eog_indices`
4. Test with sample data
5. Consider submitting to registry with documentation

## Error Troubleshooting

### AttributeError: 'list' object has no attribute 'get'

**Cause:** Using deprecated bare list for EOG

**Fix:** Convert to full dict format:
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [1, 32, ...],
        "eog_drop": True,
    },
}
```

### "Specified EOG channels not found in data"

**Cause:** Channel indices don't match your montage

**Fix:**
1. Check `EOG_CHANNEL_REFERENCE.md`
2. Verify montage name matches your data
3. Use `raw.ch_names` to inspect actual channel names

### Schema validation fails

**Cause:** Missing required fields or incorrect structure

**Fix:**
1. Export current schema: `autocleaneeg-pipeline task schema export -o schema.json`
2. Compare your config to schema
3. Ensure all steps present (even if disabled)

### EOG channels not being removed after ICA

**Cause:** Missing or incorrect `eog_drop` flag

**Fix:**
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [...],
        "eog_drop": True,  # ← Ensure this is True
    },
}
```

## Workflow Questions

### How do I test my task?

```bash
# 1. Validate schema (manual check for now)
autocleaneeg-pipeline task schema export -o schema.json

# 2. Test with single file
autocleaneeg-pipeline process YourTask /path/to/test.raw

# 3. Check output structure
ls -R /path/to/output/

# 4. Verify BIDS derivatives
tree /path/to/output/derivatives/
```

### How do I contribute a task to the registry?

1. Create task following v2.0 pattern (see `BEST_PRACTICES.md`)
2. Ensure schema compliance
3. Test with real data
4. Add to appropriate category directory
5. Update `TASKS.md` and `registry.json`
6. Submit pull request with documentation

### Can I use tasks from the registry directly?

Yes! Tasks in the registry are production-ready:

```bash
# Option 1: Reference by name (if installed)
autocleaneeg-pipeline process RestingEyesOpen /path/to/data.raw

# Option 2: Direct file path
autocleaneeg-pipeline process /path/to/registry/tasks/resting/RestingEyesOpen.py /path/to/data.raw
```

### How do I customize an existing task?

1. Copy task file from registry to your workspace
2. Rename class and update config
3. Modify parameters as needed
4. Test thoroughly

**Don't modify registry tasks directly** - copy and customize instead.

## Performance Questions

### How many ICA components should I use?

**Auto (recommended):**
```python
"n_components": None  # Pipeline selects optimal number
```

**Manual (for very high-density):**
```python
"n_components": 60  # Cap at 60 for faster processing
```

### Why is ICA taking so long?

Factors affecting ICA speed:
1. Number of channels (more = slower)
2. Number of samples (longer recording = slower)
3. ICA method (FastICA faster than Infomax)
4. Number of components

Tips to speed up:
- Use `"n_components": 60` to cap component count
- Use FastICA instead of Infomax if possible
- Ensure adequate filtering (esp. temp_highpass_for_ica)

### Should I epoch before or after ICA?

**Always run ICA on continuous data** (before epoching). The pipeline handles this automatically:

```python
def run(self):
    self.import_raw()
    # ... preprocessing on continuous data

    self.run_ica()  # ← ICA on continuous
    self.classify_ica_components()

    self.create_eventid_epochs()  # ← Epoch after ICA
```

## Resources

- **Task Examples**: See `TASKS.md`
- **Migration Guide**: See `MIGRATION.md`
- **Best Practices**: See `BEST_PRACTICES.md`
- **EOG Reference**: See `EOG_CHANNEL_REFERENCE.md`
- **Pipeline Docs**: https://cincibrainlab.github.io/autoclean_pipeline/