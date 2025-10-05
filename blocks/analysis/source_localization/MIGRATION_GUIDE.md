# Migration Guide: Source Localization v2.0.0

This guide explains how to migrate to version 2.0.0 of the source localization block, which now uses the `autocleaneeg-eeg2source` PyPI package.

## What Changed?

### Version 1.0.0 (Old)
- Custom implementation with duplicate code
- Optional conversion to 68 DK regions (`convert_to_eeg=True`)
- Returns STC objects by default
- Manual EOG channel handling

### Version 2.0.0 (New)
- Uses `autocleaneeg-eeg2source` PyPI package
- **Always** outputs 68 DK atlas regions
- No STC objects - streamlined output
- Automatic EOG channel handling
- Better memory management

## Installation Steps

### 1. Install the PyPI Package

```bash
pip install autocleaneeg-eeg2source
```

### 2. Replace Block Files

```bash
cd /Volumes/braindata/autocleaneeg-repos/autocleaneeg-task-registry/blocks/analysis/source_localization

# Backup old files
cp mixin.py mixin_old.py
cp algorithm.py algorithm_old.py
cp manifest.json manifest_old.json

# Replace with new files
mv mixin_new.py mixin.py
mv algorithm_new.py algorithm.py
mv manifest_new.json manifest.json
```

### 3. Update Your Task Config (if needed)

#### Old Config (v1.0.0)
```python
config = {
    "apply_source_localization": {
        "enabled": True,
        "value": {
            "method": "MNE",
            "lambda2": 0.111,
            "convert_to_eeg": True  # This parameter is REMOVED
        }
    }
}
```

#### New Config (v2.0.0)
```python
config = {
    "apply_source_localization": {
        "enabled": True,
        "value": {
            "method": "MNE",
            "lambda2": 0.111,
            "montage": "GSN-HydroCel-129"  # Now configurable
            # convert_to_eeg removed - always outputs 68 regions
        }
    }
}
```

## API Compatibility

### Good News: Zero Code Changes Needed! 🎉

The mixin API is **100% backward compatible**:

```python
# This still works exactly the same
class MyTask(Task):
    def run(self):
        self.import_raw()
        self.create_regular_epochs()

        # No changes needed!
        source_data = self.apply_source_localization()

        # source_data now has 68 channels (DK regions)
        # self.source_eeg_file points to saved .set file
```

### What's Different?

**Output Format:**
- **Before:** Returns STC object (10,242 vertices) unless `convert_to_eeg=True`
- **After:** Always returns 68-channel MNE object (DK regions)

**Files Saved:**
- `{subject}_dk_regions.set` - 68-channel EEGLAB file
- `{subject}_region_info.csv` - Region metadata

## Testing the Migration

### Test Script

```python
from autoclean.core.task import Task

config = {
    "schema_version": "2025.09",
    "apply_source_localization": {
        "enabled": True,
        "value": {
            "method": "MNE",
            "lambda2": 0.111,
            "montage": "GSN-HydroCel-129"
        }
    }
}

class TestSourceLoc(Task):
    def run(self):
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.create_regular_epochs()

        # Apply source localization
        source_epochs = self.apply_source_localization()

        # Verify output
        print(f"Output channels: {source_epochs.info['nchan']}")  # Should be 68
        print(f"Channel names: {source_epochs.ch_names[:5]}")     # DK region names
        print(f"Saved to: {self.source_eeg_file}")

task = TestSourceLoc("your_file.set", config=config)
task.run()
```

### Expected Output

```
=== Applying Source Localization ===
Using autocleaneeg-eeg2source package
Method: MNE, lambda2: 0.111
Input: Epochs, montage: GSN-HydroCel-129
Exporting to temporary file for processing...
Processing with source localization...
Loading 68-region output...
✓ Source localization complete: 68 DK regions
Saved to: derivatives/source_localization/subject_dk_regions.set

Output channels: 68
Channel names: ['bankssts-lh', 'bankssts-rh', 'caudalanteriorcingulate-lh', ...]
Saved to: derivatives/source_localization/subject_dk_regions.set
```

## Troubleshooting

### Import Error

**Problem:**
```
ImportError: autocleaneeg-eeg2source package not found
```

**Solution:**
```bash
pip install autocleaneeg-eeg2source
```

### Different Results

**Q:** Why do my results look different from v1.0.0?

**A:** If you were using `convert_to_eeg=False` in v1.0.0 (getting STCs), you'll now get 68 DK regions instead. This is the intended behavior - the new version always produces region-level data for consistency and ease of use.

### Need Raw STCs?

**Q:** I need raw source estimates (10,242 vertices), not 68 regions!

**A:** For advanced use cases requiring raw STCs, use the standalone package directly:

```python
from autoclean_eeg2source.core.converter import SequentialProcessor

# This gives you more control but requires manual file handling
processor = SequentialProcessor()
# ... custom processing
```

Or modify the package to optionally return STCs before conversion.

## Benefits of the New Version

✅ **Single source of truth** - one maintained codebase
✅ **Easier updates** - `pip install -U autocleaneeg-eeg2source`
✅ **Better memory management** - MemoryManager class
✅ **Automatic EOG handling** - detects and removes EOG channels
✅ **Consistent results** - same algorithm everywhere
✅ **Simpler output** - always 68 DK regions

## Rollback (if needed)

If you need to rollback:

```bash
cd /Volumes/braindata/autocleaneeg-repos/autocleaneeg-task-registry/blocks/analysis/source_localization

# Restore old files
cp mixin_old.py mixin.py
cp algorithm_old.py algorithm.py
cp manifest_old.json manifest.json

# Uninstall package (optional)
pip uninstall autocleaneeg-eeg2source
```

## Questions?

Contact: ernest.pedapati@cchmc.org
