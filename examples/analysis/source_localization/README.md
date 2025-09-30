# Source Localization Examples

These examples demonstrate using the `source_localization` block to project sensor-space EEG to cortical sources using MNE minimum norm estimation.

## Examples

### SourceLocalization_Raw.py
**Purpose**: Source localization on continuous (Raw) EEG data

**What it demonstrates**:
- Processing continuous resting-state EEG
- MNE inverse solution with fsaverage template
- Converting source estimates to 68-channel ROI EEG format
- BIDS-compatible derivatives output

**Output files** (in `derivatives/source_localization_eeg/`):
- `{subject}_dk_regions.set` - 68-channel EEGLAB file (Desikan-Killiany ROIs)
- `{subject}_dk_montage.fif` - ROI centroid positions
- `{subject}_region_info.csv` - ROI metadata (names, hemispheres, coordinates)

**Use case**: When you want compact ROI-level time courses for further analysis in EEGLAB or other tools.

---

### SourceLocalization_Epochs.py
**Purpose**: Source localization on epoched EEG data

**What it demonstrates**:
- Creating regular epochs from continuous data
- MNE inverse solution applied to epochs
- Converting epoch-level source estimates to ROI format
- Epoched EEGLAB output for trial-level analysis

**Output files** (same as Raw, but epoched):
- `{subject}_dk_regions.set` - 68-channel epoched EEGLAB file
- `{subject}_dk_montage.fif` - ROI positions
- `{subject}_region_info.csv` - ROI metadata

**Use case**: When you need trial-by-trial source activity (e.g., for ERP source analysis, single-trial connectivity).

---

## Configuration Options

### Key Parameters

```python
"apply_source_localization": {
    "enabled": True,
    "value": {
        "method": "MNE",              # Inverse method: "MNE", "dSPM", "sLORETA"
        "lambda2": 0.111,             # Regularization (1/SNR²)
        "pick_ori": "normal",         # "normal" or None
        "n_jobs": 10,                 # Parallel jobs
        "save_stc": False,            # Save vertex-level STC (2.3GB files!)
        "convert_to_eeg": True,       # Convert to 68-channel ROI format (3.9MB)
    }
}
```

### Important Notes

1. **STC files are huge**: Vertex-level source estimates are ~2.3GB for Raw, ~78MB per epoch
   - Set `save_stc: False` unless you specifically need vertex-level data
   - Set `convert_to_eeg: True` for compact 68-channel ROI files (3.9MB)

2. **ROI Conversion**: Uses Desikan-Killiany atlas (68 cortical regions)
   - Includes frontal, temporal, parietal, occipital, and cingulate regions
   - Time courses are averaged across vertices within each ROI
   - Result is standard 68-channel EEG compatible with existing tools

3. **Processing Time**:
   - Raw data: ~2-5 minutes per subject
   - Epoched data: ~3-8 minutes (depends on number of epochs)

## Downstream Analysis

After source localization, you can use:
- `source_psd` block - Regional power spectral density
- `source_connectivity` block - Functional connectivity + graph metrics
- `fooof_aperiodic` / `fooof_periodic` blocks - Spectral parameterization
- Or load the 68-channel .set files into EEGLAB/FieldTrip for custom analysis

## Scientific References

- Hämäläinen MS & Ilmoniemi RJ (1994). Interpreting magnetic fields of the brain: minimum norm estimates. *Medical & Biological Engineering & Computing*, 32(1), 35-42.
- Gramfort A, et al. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, 7, 267.
- Desikan RS, et al. (2006). An automated labeling system for subdividing the human cerebral cortex. *NeuroImage*, 31(3), 968-980.

## Running the Examples

```bash
# Continuous data
autocleaneeg-pipeline process --task SourceLocalization_Raw --file /path/to/data.set

# Epoched data
autocleaneeg-pipeline process --task SourceLocalization_Epochs --file /path/to/data.set
```