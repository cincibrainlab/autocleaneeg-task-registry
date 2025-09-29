# Changelog

All notable changes to the AutoClean EEG Task Registry will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- **GitHub Pages Documentation**: Complete documentation site at https://cincibrainlab.github.io/autocleaneeg-task-registry/
- **Documentation Reorganization**: Moved all docs to `/docs` folder for GitHub Pages
  - Created comprehensive landing page (docs/index.md)
  - Organized integration docs in docs/integration/
  - Added development docs in docs/development/ (testing, architecture)
- **New Task Categories**: Organized tasks into `resting/`, `auditory/`, `visual/`, and `rodent/` subdirectories
- **Visual Tasks**: Added `HBCD_VEP` for visual evoked potential protocol
- **Auditory Tasks**: Added `Chirp_Default`, `BB_Long`, and `HBCD_MMN`
- **Rodent Tasks**: Added `Mouse_XDAT_ASSR`, `Mouse_XDAT_Chirp`, and `Mouse_XDAT_Resting` for preclinical studies
- **Task Directory**: Comprehensive `TASKS.md` with quick reference table and detailed task descriptions
- **Documentation**: Added `docs/` folder with migration guides and best practices
- **EOG Reference**: `EOG_CHANNEL_REFERENCE.md` with montage-specific channel mappings

### Changed

- **EOG Configuration** (Breaking): Now requires full dict format with explicit `eog_drop` control
  ```python
  # Before (deprecated)
  "eog_step": {"enabled": True, "value": [1, 32, ...]}

  # After (required)
  "eog_step": {
      "enabled": True,
      "value": {
          "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
          "eog_drop": True,
      },
  }
  ```
- **Schema Compliance**: All tasks now include complete step definitions even when `enabled: False`
- **PSD Visualization**: Added `psd_fmax` to all component rejection configs, aligned with filter cutoffs
- **Task Naming**: Standardized to PascalCase_With_Underscores (e.g., `Chirp_Default`, `HBCD_VEP`)
- **Task Structure**: All tasks follow v2.0 pattern (module-level config, no custom `__init__`, explicit methods)

### Updated

- ✅ `RestingEyesOpen` - EOG dict format, added `psd_fmax: 80.0`
- ✅ `RestingEyesClosed` - EOG dict format, added `psd_fmax: 70.0`
- ✅ `ASSR_40Hz` - EOG dict format, added `psd_fmax: 80.0`
- ✅ `MMN_Standard` - EOG dict format, added `psd_fmax: 40.0`
- ✅ `BiotrialResting1020` - Already compliant

### Removed

- Deprecated bare list format for EOG configuration (still supported in pipeline for backward compatibility)
- Custom `__init__` methods from migrated tasks
- Deprecated imports (`save_raw_to_set`, `step_create_bids_path`)

## Migration Guide

### EOG Configuration Update

**For EGI GSN-129 Tasks** (11 EOG channels):
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128],
        "eog_drop": True,
    },
}
```

**For Standard 10-20 Tasks** (2 EOG channels):
```python
"eog_step": {
    "enabled": True,
    "value": {
        "eog_indices": [31, 32],  # Fp1, Fp2
        "eog_drop": True,
    },
}
```

**For Rodent Systems** (no EOG):
```python
"eog_step": {
    "enabled": False,
    "value": {
        "eog_indices": [],
        "eog_drop": False,
    },
}
```

### Common Issues

**AttributeError: 'list' object has no attribute 'get'**
- **Cause**: Using deprecated bare list format
- **Fix**: Convert to full dict format (see examples above)

**EOG channels not removed after ICA**
- **Cause**: Missing or incorrect `eog_drop` flag
- **Fix**: Ensure `eog_drop: True` in configuration

**"Specified EOG channels not found in data"**
- **Cause**: Channel indices don't match montage
- **Fix**: Check `EOG_CHANNEL_REFERENCE.md` for correct indices

## Resources

- **Task Registry Docs**: https://cincibrainlab.github.io/autocleaneeg-task-registry/
- **Task Directory**: See `docs/TASKS.md` for complete task catalog
- **EOG Reference**: See `docs/EOG_CHANNEL_REFERENCE.md` for montage-specific channels
- **Best Practices**: See `docs/BEST_PRACTICES.md` for development guidelines
- **Pipeline Docs**: https://cincibrainlab.github.io/autoclean_pipeline/

---

**Last Updated**: 2025-09-29
**Schema Version**: 2025.09