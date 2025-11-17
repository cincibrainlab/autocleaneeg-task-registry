# Task Registry Directory

Comprehensive directory of validated AutoClean EEG tasks organized by paradigm category.

## Quick Reference

| Task | Category | Montage | Paradigm | ICA | Epoch Type |
|------|----------|---------|----------|-----|------------|
| **RestingEyesOpen** | Resting | GSN-129 | Resting-state eyes open | Yes (FastICA) | Regular (1s) |
| **RestingEyesClosed** | Resting | GSN-129 | Resting-state eyes closed | Yes (FastICA) | Regular (1s) |
| **RestingState_WaveletOnly** | Resting | GSN-129 | Resting with wavelet denoising | No | Regular (1s) |
| **ASSR_40Hz** | Auditory | GSN-129 | 40 Hz steady-state | Yes (FastICA) | Event (1.2s) |
| **MMN_Standard** | Auditory | GSN-129 | Mismatch negativity | Yes (FastICA) | Event (0.8s) |
| **Chirp_Default** | Auditory | GSN-129 | Chirp stimulation | Yes (Infomax) | Event (1.0s) |
| **BB_Long** | Auditory | GSN-129 | Broadband long-duration | Yes (Infomax) | Regular (2s) |
| **HBCD_MMN** | Auditory | GSN-129 | HBCD mismatch negativity | Yes (FastICA) | Event (0.8s) |
| **P300_Grael4K** | Auditory | Standard 10-20 | P300 oddball | Yes (Infomax) | Event (1.5s) |
| **HBCD_VEP** | Visual | GSN-129 | HBCD visual evoked | Yes (FastICA) | Event (0.7s) |
| **Mouse_XDAT_ASSR** | Rodent | MEA30 | Mouse ASSR | No | Event (1.0s) |
| **Mouse_XDAT_Chirp** | Rodent | MEA30 | Mouse chirp | No | Event (1.0s) |
| **Mouse_XDAT_Resting** | Rodent | MEA30 | Mouse resting-state | No | Regular (2s) |

## Categories

### Resting State (`tasks/resting/`)

**RestingEyesOpen**
- **Purpose**: Standard resting-state with eyes open
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 1-80 Hz, notch 60/120 Hz
- **ICA**: FastICA with ICLabel rejection (threshold 0.3)
- **Epochs**: 1-second non-overlapping regular epochs
- **Use Case**: Baseline neural activity, connectivity analysis

**RestingEyesClosed**
- **Purpose**: Standard resting-state with eyes closed
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 1-70 Hz, notch 60/120 Hz
- **ICA**: FastICA with ICLabel rejection (threshold 0.3)
- **Epochs**: 1-second non-overlapping regular epochs
- **Use Case**: Alpha rhythm analysis, relaxed baseline

**RestingState_WaveletOnly**
- **Purpose**: Resting-state with wavelet-based denoising instead of ICA
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 1-80 Hz, notch 60/120 Hz
- **ICA**: Disabled (uses wavelet thresholding)
- **Epochs**: 1-second non-overlapping regular epochs
- **Use Case**: Alternative artifact removal for datasets where ICA is unsuitable

### Auditory (`tasks/auditory/`)

**ASSR_40Hz**
- **Purpose**: Auditory steady-state response at 40 Hz
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 1-80 Hz, notch 60/120 Hz
- **ICA**: FastICA with ICLabel rejection (threshold 0.3)
- **Epochs**: -0.2 to 1.0s around stimulus onset
- **Event ID**: `assr: 1`
- **Use Case**: Neural synchrony, auditory processing

**MMN_Standard**
- **Purpose**: Mismatch negativity (oddball paradigm)
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 0.1-40 Hz, notch 60 Hz
- **ICA**: FastICA with ICLabel rejection (threshold 0.28)
- **Epochs**: -0.2 to 0.6s around stimulus onset
- **Event ID**: `standard: 1, deviant: 2`
- **Use Case**: Pre-attentive change detection, auditory memory

**Chirp_Default**
- **Purpose**: Chirp auditory stimulation
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 1-100 Hz, notch 60/120 Hz
- **ICA**: Infomax (extended) with ICLabel rejection (threshold 0.3)
- **Epochs**: -0.2 to 0.8s around stimulus onset
- **Event ID**: `chirp: 1`
- **Use Case**: Frequency-sweep auditory response

**BB_Long**
- **Purpose**: Long-duration broadband auditory stimulation
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 1-100 Hz, notch 60/120 Hz
- **ICA**: Infomax (extended) with ICLabel rejection (threshold 0.3)
- **Epochs**: 2-second non-overlapping regular epochs
- **Use Case**: Continuous auditory processing, spectral analysis

**HBCD_MMN**
- **Purpose**: HBCD study mismatch negativity protocol
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 0.1-40 Hz, notch 60 Hz
- **ICA**: FastICA with ICLabel rejection (threshold 0.28)
- **Epochs**: -0.2 to 0.6s around stimulus onset
- **Event ID**: `standard: 1, deviant: 2`
- **Use Case**: HBCD consortium standardized oddball protocol

**P300_Grael4K**
- **Purpose**: P300 oddball paradigm for Grael4K dataset
- **Montage**: standard_1020 (10-20 system)
- **Filtering**: 0.1-45 Hz, notch 50/60 Hz
- **ICA**: Infomax (extended) with ICLabel rejection (threshold 0.3, muscle override 0.90)
- **Epochs**: -0.5 to 1.0s around stimulus onset
- **Event ID**: `Standard: 13, Target: 14`
- **Use Case**: P300 event-related potential analysis, cognitive processing

### Visual (`tasks/visual/`)

**HBCD_VEP**
- **Purpose**: HBCD study visual evoked potential protocol
- **Montage**: EGI GSN-HydroCel-129
- **Filtering**: 0.1-40 Hz, notch 60 Hz
- **ICA**: FastICA with ICLabel rejection (threshold 0.28)
- **Epochs**: -0.2 to 0.5s around stimulus onset
- **Event ID**: `visual_stimulus: 1`
- **Use Case**: HBCD consortium standardized visual processing protocol

### Rodent (`tasks/rodent/`)

**Mouse_XDAT_ASSR**
- **Purpose**: Mouse ASSR with correlation-based artifact rejection
- **Montage**: MEA30 (30-channel microelectrode array)
- **Filtering**: 1-100 Hz, notch 60/120 Hz
- **ICA**: Disabled (uses correlation-based channel rejection)
- **Epochs**: -0.2 to 0.8s around stimulus onset
- **Event ID**: `assr: 1`
- **Use Case**: Preclinical ASSR studies

**Mouse_XDAT_Chirp**
- **Purpose**: Mouse chirp with correlation-based artifact rejection
- **Montage**: MEA30 (30-channel microelectrode array)
- **Filtering**: 1-100 Hz, notch 60/120 Hz
- **ICA**: Disabled (uses correlation-based channel rejection)
- **Epochs**: -0.2 to 0.8s around stimulus onset
- **Event ID**: `chirp: 1`
- **Use Case**: Preclinical chirp auditory studies

**Mouse_XDAT_Resting**
- **Purpose**: Mouse resting-state with correlation-based artifact rejection
- **Montage**: MEA30 (30-channel microelectrode array)
- **Filtering**: 1-100 Hz, notch 60/120 Hz
- **ICA**: Disabled (uses correlation-based channel rejection)
- **Epochs**: 2-second non-overlapping regular epochs
- **Use Case**: Preclinical baseline neural activity

## Common Parameters

### EOG Channels (GSN-129)
Standard EOG channel indices for human EGI nets:
```python
"eog_indices": [1, 32, 8, 14, 17, 21, 25, 125, 126, 127, 128]
```

### ICA Methods
- **FastICA**: Fast, deterministic, good for most applications
- **Infomax Extended**: Better for super-Gaussian sources (muscle artifacts)

### ICLabel Rejection Flags
Standard artifact categories rejected:
- `muscle`: EMG artifacts
- `heart`: ECG artifacts
- `eog`: Eye movement artifacts
- `ch_noise`: Channel-specific noise
- `line_noise`: Power line interference

### Epoch Types
- **Regular**: Non-overlapping fixed-duration epochs for continuous data
- **Event**: Stimulus-locked epochs for event-related potentials

## Usage

```bash
# List all available tasks
autocleaneeg-pipeline list-tasks

# Run a specific task
autocleaneeg-pipeline process RestingEyesOpen /path/to/data.raw

# Export task schema
autocleaneeg-pipeline task schema export -o my_task_schema.json
```

## Schema Compliance

All tasks follow the `2025.09` schema version with:
- Module-level `config` dictionary
- No custom `__init__` methods
- Explicit method calls in `run()`
- Complete step definitions (even if `enabled: False`)

## Contributing

To add a new task:
1. Choose appropriate category directory
2. Follow v2.0 task pattern (see existing tasks)
3. Ensure schema compliance
4. Add entry to this directory
5. Update `registry.json`

See `docs/BEST_PRACTICES.md` for detailed guidelines.