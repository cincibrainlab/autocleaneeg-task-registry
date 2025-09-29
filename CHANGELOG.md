# Changelog

All notable changes to the AutoClean EEG Task Registry will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

#### EOG Configuration Standardization (2025-09-29)

**Breaking Change**: EOG step configuration now requires full dict format with explicit `eog_drop` control.

**Before** (Deprecated):
```python
"eog_step": {
    "enabled": True,
    "value": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],  # Bare list
}
```

**After** (Required):
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
        "eog_drop": True,  # Explicit control over channel removal
    },
}
```

**Why This Change?**
- **Explicit Intent**: Clear specification of whether EOG channels should be removed after ICA
- **Schema Compliance**: Aligns with pipeline schema validation requirements
- **Better Control**: Developers can now choose to keep or remove EOG channels
- **Prevents Errors**: Fixes AttributeError when pipeline expects dict format

**Migration Guide**:

1. **For EGI GSN-HydroCel-129 Tasks** (11 EOG channels):
   ```python
   # Old format
   "eog_step": {"enabled": True, "value": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128]}

   # New format
   "eog_step": {
       "enabled": True,
       "value": {
           "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
           "eog_drop": True,
       },
   }
   ```

2. **For Standard 10-20 Tasks** (2 EOG channels - Fp1, Fp2):
   ```python
   # Old format
   "eog_step": {"enabled": True, "value": [31, 32]}

   # New format
   "eog_step": {
       "enabled": True,
       "value": {
           "eog_indices": [31, 32],
           "eog_drop": True,
       },
   }
   ```

3. **To Keep EOG Channels** (no removal after ICA):
   ```python
   "eog_step": {
       "enabled": True,
       "value": {
           "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
           "eog_drop": False,  # Keep channels in final dataset
       },
   }
   ```

**Affected Tasks**:
- ✅ `RestingEyesOpen` - Updated
- ✅ `RestingEyesClosed` - Updated
- ✅ `ASSR_40Hz` - Updated
- ✅ `MMN_Standard` - Updated
- ✅ `BiotrialResting1020` - Already compliant

**Backward Compatibility**:
The pipeline still supports bare list format for backward compatibility, but **all registry tasks should use the new dict format** going forward.

### Added

#### EOG Channel Reference Documentation (2025-09-29)

Added comprehensive `EOG_CHANNEL_REFERENCE.md` documenting montage-specific EOG channel mappings.

**What's Included**:
- **EGI GSN-HydroCel-129**: 11 EOG channels with anatomical descriptions
- **EGI GSN-HydroCel-124**: 11 EOG channels (adjusted layout)
- **Standard 10-20**: 2 EOG channels (Fp1, Fp2)
- **Grael 4K**: 2-4 EOG channels with system-specific notes
- **MEA30**: Rodent system considerations

**Example Usage**:

```python
# For high-density EGI nets
config = {
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "eog_step": {
        "enabled": True,
        "value": {
            "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
            "eog_drop": True,
        },
    },
}

# For clinical 10-20 systems
config = {
    "montage": {"enabled": True, "value": "standard_1020"},
    "eog_step": {
        "enabled": True,
        "value": {
            "eog_indices": [31, 32],  # Fp1, Fp2
            "eog_drop": True,
        },
    },
}
```

**Benefits for Developers**:
- Quick reference for correct EOG channels per montage
- Troubleshooting guidance for common issues
- System-specific considerations (especially Grael 4K)
- Configuration examples for all supported systems

---

## Best Practices for Task Authors

### 1. Always Use Full Dict Format for EOG
```python
# ✅ Correct - Full dict format
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
        "eog_drop": True,
    },
}

# ❌ Avoid - Bare list (deprecated)
"eog_step": {
    "enabled": True,
    "value": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
}
```

### 2. Include psd_fmax in Component Rejection
Align PSD visualization ceiling with your filtering cutoff:

```python
"filtering": {
    "enabled": True,
    "value": {"l_freq": 1.0, "h_freq": 80.0, "notch_freqs": [60, 120]},
},
"component_rejection": {
    "enabled": True,
    "method": "icvision",
    "value": {
        "ic_flags_to_reject": ["muscle", "heart", "eog", "ch_noise", "line_noise"],
        "ic_rejection_threshold": 0.3,
        "psd_fmax": 80.0,  # Match h_freq for accurate visualization
    },
},
```

### 3. Document Montage Requirements
Include montage information in task docstrings:

```python
"""TaskName built-in task.

Description of the task purpose.

Montage: GSN-HydroCel-129 (129-channel EGI net)
EOG Channels: E1, E32, E8, E14, E17, E21, E25, E125, E126, E127, E128 (11 channels)
"""
```

### 4. Verify Channel Indices Match Your System
```python
# Before finalizing a task, verify channels exist
# Add this to your run() method during development:
def run(self):
    self.import_raw()

    # Verify EOG channels exist (remove after verification)
    eog_indices = [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128]
    for idx in eog_indices:
        if idx > len(self.raw.ch_names):
            print(f"Warning: EOG channel index {idx} exceeds channel count")

    # Continue with processing...
```

---

## Common Migration Issues

### Issue 1: AttributeError when accessing eog_step.value
**Error**: `AttributeError: 'list' object has no attribute 'get'`

**Cause**: Using deprecated bare list format

**Fix**: Convert to full dict format as shown above

### Issue 2: EOG channels not being removed after ICA
**Cause**: Missing or incorrect `eog_drop` flag

**Fix**: Ensure `eog_drop: True` in your configuration:
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [...],
        "eog_drop": True,  # ← Add this
    },
}
```

### Issue 3: "Specified EOG channels not found in data"
**Cause**: Channel indices don't match your montage

**Fix**:
1. Check `EOG_CHANNEL_REFERENCE.md` for correct indices
2. Verify your montage configuration matches your data
3. Use `raw.ch_names` to inspect actual channel names/order

---

## Version History

### 2025-09-29
- Standardized EOG configuration across all registry tasks
- Added comprehensive EOG channel reference documentation
- Improved developer documentation with migration examples

---

## Contributing

When adding or modifying tasks:

1. **Use schema-compliant configurations**: Follow the examples in this changelog
2. **Test both formats**: Verify your task works with the pipeline
3. **Document montage requirements**: Specify required electrode system
4. **Include examples**: Add configuration examples in task docstrings
5. **Validate EOG channels**: Ensure channel indices match montage specifications

For questions or issues, refer to:
- `EOG_CHANNEL_REFERENCE.md` - Montage-specific channel mappings
- `README.md` - Registry overview and usage
- Pipeline documentation - https://cincibrainlab.github.io/autoclean_pipeline/

---

**Last Updated**: 2025-09-29
**Document Version**: 1.0.0