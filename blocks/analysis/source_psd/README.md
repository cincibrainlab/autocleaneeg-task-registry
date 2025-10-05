# Source PSD Block

**Version:** 2.0.0
**Category:** Analysis
**Status:** Stable

## Overview

The Source PSD block calculates power spectral density (PSD) from source-localized EEG data with region-of-interest (ROI) averaging using the Desikan-Killiany atlas (68 cortical regions).

**Version 2.0.0** introduces **dual-mode processing** for optimal performance and backward compatibility:

### ROI-Optimized Mode (v2.0.0+)
- **For:** Source localization v2.0.1+ output (68-channel ROI data)
- **Processing:** Direct PSD calculation on 68 channels
- **Speed:** ~10-30 seconds per subject
- **Performance:** 10-20× faster than vertex-level mode
- **Auto-detected:** When `self.source_eeg` exists

### Vertex-Level Mode (v1.0.0 compatible)
- **For:** Source localization v1.0.0 output (vertex STCs)
- **Processing:** PSD on 20,484 vertices → parcellation to 68 ROIs
- **Speed:** ~2-5 minutes per subject
- **Compatibility:** Backward compatible with existing workflows
- **Auto-detected:** When `self.stc` or `self.stc_list` exists

**Both modes produce identical output formats** for seamless downstream analysis.

## What It Does

Source-level PSD analysis performs:
1. **Automatic mode detection** (ROI-optimized vs vertex-level)
2. **Welch's method PSD estimation** (0.5-45 Hz frequency range)
3. **Adaptive windowing** (4s windows, 50% overlap) for spectral accuracy
4. **ROI processing:**
   - **ROI mode:** Direct calculation on 68 DK channels
   - **Vertex mode:** Parallel batch processing → parcellation to 68 ROIs
5. **Frequency band power extraction** (8 bands: delta through gamma)
6. **Diagnostic visualizations** (4-panel plots)

The block automatically selects the optimal processing mode based on available data, producing frequency-resolved PSD and band power summaries suitable for group-level statistical analyses.

## When to Use

**Use source PSD when you need:**
- Region-specific spectral analysis (e.g., frontal alpha power)
- Frequency band quantification across brain regions
- Group-level statistical comparisons of regional power
- Alpha peak frequency or band power analyses
- Spectral biomarkers for clinical populations

**Requirements:**
- Prior source localization (v2.0.1+ or v1.0.0)
  - v2.0.1+: `self.source_eeg` (68-channel ROI data)
  - v1.0.0: `self.stc` or `self.stc_list` (vertex STCs)
- Minimum 30 seconds of clean data (80s recommended)
- fsaverage brain data (auto-downloaded if not present, vertex mode only)
- Memory requirements:
  - ROI mode: ~2-4 GB
  - Vertex mode: ~8 GB recommended for parallel processing

## How It Works

### Algorithm

**ROI-Optimized Mode (v2.0+):**
```
68-Channel ROI EEG (Raw or Epochs)
         ↓
Segment Selection (middle 80s for stationarity)
         ↓
MNE compute_psd() - Welch's Method
    4s windows, 50% overlap, 0.5-45 Hz
         ↓
Frequency Band Integration
    Delta (1-4), Theta (4-8), Alpha (8-13)
    Beta (13-30), Gamma (30-45 Hz)
         ↓
Output: ROI × Frequency DataFrames
Processing Time: ~10-30 seconds
```

**Vertex-Level Mode (v1.0):**
```
Source Estimates (10,242-20,484 vertices × time)
         ↓
Variance Filtering (exclude low-variance vertices)
         ↓
Welch's Method PSD (4s windows, 50% overlap)
    Parallel batch processing (5000 vertices/batch)
         ↓
ROI Parcellation (Desikan-Killiany atlas, 68 regions)
         ↓
Frequency Band Integration
         ↓
Output: ROI × Frequency DataFrames
Processing Time: ~2-5 minutes
```

### Technical Details

- **Method:** Welch's periodogram averaging
- **Frequency Range:** 0.5-45 Hz
- **Window Length:** Adaptive (4s preferred, min 8 windows required)
- **Overlap:** 50% (Hanning window)
- **Atlas:** Desikan-Killiany (aparc annotation)
- **ROIs:** 68 cortical regions (34 per hemisphere)
- **Segment Duration:** 80s default (middle epochs for stationarity)
- **Parallel Processing:** Batched vertex processing with configurable jobs

## Configuration

### Basic Configuration

```python
config = {
    "apply_source_psd": {
        "enabled": True,
        "value": {
            "segment_duration": 80,  # seconds
            "n_jobs": 4,
            "generate_plots": True
        }
    }
}
```

### Advanced Configuration

```python
# Process full dataset (no time limit)
config = {
    "apply_source_psd": {
        "enabled": True,
        "value": {
            "segment_duration": None,  # Use all data
            "n_jobs": 8,
            "generate_plots": True
        }
    }
}

# Fast processing (minimal plotting)
config = {
    "apply_source_psd": {
        "enabled": True,
        "value": {
            "segment_duration": 60,
            "n_jobs": 10,
            "generate_plots": False  # Skip diagnostic plots
        }
    }
}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `segment_duration` | float | `80` | Duration in seconds to process (None = all data) |
| `n_jobs` | int | `4` | Number of parallel jobs for computation |
| `generate_plots` | bool | `True` | Generate diagnostic PSD visualizations |

## Usage in Tasks

### Resting-State Example

```python
from autoclean.core.task import Task

config = {
    "schema_version": "2025.09",
    "apply_source_localization": {
        "enabled": True,
        "value": {"method": "MNE", "lambda2": 0.111}
    },
    "apply_source_psd": {
        "enabled": True,
        "value": {"segment_duration": 80, "n_jobs": 4}
    }
}

class RestingSourcePSD(Task):
    def run(self):
        # Preprocessing
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.rereference_data()
        self.run_ica()

        # Create epochs
        self.create_regular_epochs()

        # Source analysis pipeline
        self.apply_source_localization()  # Creates self.stc_list
        psd_df, file_path = self.apply_source_psd()  # Uses self.stc_list

        # Results now available for analysis
        # psd_df: DataFrame with [subject, roi, hemisphere, frequency, psd]
        print(f"Processed {len(psd_df['roi'].unique())} ROIs")
```

### Event-Related Example

```python
class ERPSourcePSD(Task):
    def run(self):
        # Preprocessing
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.rereference_data()

        # Epoch around events
        self.epoch_data()  # Time-locked epochs

        # Source analysis
        self.apply_source_localization()
        psd_df, file_path = self.apply_source_psd(
            segment_duration=None  # Use all epochs
        )

        # Access band powers for specific ROI
        frontal = psd_df[psd_df['roi'].str.contains('frontal')]
        alpha_power = frontal[
            (frontal['frequency'] >= 8) &
            (frontal['frequency'] <= 13)
        ]['psd'].mean()
```

## Outputs

### ROI PSD DataFrame (Parquet)

**File:** `derivatives/source_psd/{subject}_roi_psd.parquet`

**Columns:**
- `subject`: Subject identifier
- `roi`: ROI name (e.g., "superiorfrontal-lh")
- `hemisphere`: Hemisphere ("lh" or "rh")
- `frequency`: Frequency in Hz (0.5-45 Hz)
- `psd`: Power spectral density (µV²/Hz)

**Example:**
```python
import pandas as pd
psd_df = pd.read_parquet("subject_roi_psd.parquet")

# Filter for specific ROI and frequency band
frontal_alpha = psd_df[
    (psd_df['roi'] == 'superiorfrontal-lh') &
    (psd_df['frequency'] >= 8) &
    (psd_df['frequency'] <= 13)
]
```

### Band Power Summary (CSV)

**File:** `derivatives/source_psd/{subject}_roi_bands.csv`

**Columns:**
- `subject`: Subject identifier
- `roi`: ROI name
- `hemisphere`: Hemisphere
- `band`: Frequency band name
- `band_start_hz`: Band start frequency
- `band_end_hz`: Band end frequency
- `power`: Mean band power (µV²/Hz)

**Frequency Bands:**
- **Delta:** 1-4 Hz
- **Theta:** 4-8 Hz
- **Alpha:** 8-13 Hz (also split into low/high)
- **Low Alpha:** 8-10 Hz
- **High Alpha:** 10-13 Hz
- **Low Beta:** 13-20 Hz
- **High Beta:** 20-30 Hz
- **Gamma:** 30-45 Hz

### Visualization (PNG)

**File:** `derivatives/source_psd/{subject}_psd_visualization.png`

**4-Panel Diagnostic Plot:**
1. **Regional PSDs (Top Left):** PSD curves for 5 selected left hemisphere regions
2. **Hemisphere Comparison (Top Right):** Average PSD for left vs right hemisphere
3. **Band Power Distribution (Bottom Left):** Normalized band powers across 4 regions
4. **Alpha/Beta Ratio (Bottom Right):** Regional alpha/beta ratios by hemisphere

## Performance

**ROI-Optimized Mode (v2.0+):**
- PSD calculation: ~5-15 seconds (68 channels)
- Visualization: ~5-10 seconds
- **Total:** ~10-30 seconds per subject
- **Memory:** ~2-4 GB
- **Speedup:** 10-20× faster than vertex mode

**Vertex-Level Mode (v1.0):**
- Vertex-level PSD: ~2-5 minutes (20,484 vertices, 80s data, 4 jobs)
- ROI parcellation: ~10-20 seconds (68 ROIs)
- Visualization: ~5-10 seconds
- **Total:** ~3-8 minutes per subject
- **Memory:** ~4-8 GB (parallel batches)

**Optimization Tips:**
- **ROI mode automatically selected** when using source localization v2.0.1+
- Vertex mode: Increase `n_jobs` for faster processing (4-10 recommended)
- Reduce `segment_duration` for memory-constrained systems
- Set `generate_plots=False` to skip visualization overhead
- Use parquet format for efficient storage (5-10× smaller than CSV)

## Downstream Analyses

Source PSD enables:

1. **Statistical Testing**
   ```python
   import pandas as pd
   from scipy import stats

   # Load PSDs for multiple subjects
   group_a = [pd.read_parquet(f) for f in group_a_files]
   group_b = [pd.read_parquet(f) for f in group_b_files]

   # Test frontal alpha difference
   alpha_a = [extract_alpha_power(df, 'superiorfrontal-lh') for df in group_a]
   alpha_b = [extract_alpha_power(df, 'superiorfrontal-lh') for df in group_b]
   t_stat, p_val = stats.ttest_ind(alpha_a, alpha_b)
   ```

2. **Alpha Peak Frequency**
   ```python
   # Find individual alpha peak
   roi_data = psd_df[psd_df['roi'] == 'lateraloccipital-lh']
   alpha_range = roi_data[
       (roi_data['frequency'] >= 8) & (roi_data['frequency'] <= 13)
   ]
   peak_freq = alpha_range.loc[alpha_range['psd'].idxmax(), 'frequency']
   ```

3. **Topographic Analysis**
   ```python
   # Create band power topography
   band_df = pd.read_csv(f"{subject}_roi_bands.csv")
   alpha_topo = band_df[band_df['band'] == 'alpha']
   # Plot using MNE parcellation plotting
   ```

## Limitations

1. **Frequency Resolution**
   - Limited by window length (4s → 0.25 Hz resolution)
   - Shorter data → longer windows → poorer frequency resolution
   - Trade-off between resolution and averaging for noise reduction

2. **Segment Duration**
   - Default 80s balances accuracy and performance
   - Shorter segments may have inadequate averaging
   - Longer segments may violate stationarity assumptions

3. **Atlas Constraints**
   - Desikan-Killiany has 68 relatively large ROIs
   - Spatial resolution limited by parcellation granularity
   - Cannot capture fine-grained spatial patterns

4. **Variance Filtering**
   - Low-variance vertices excluded (10th percentile threshold)
   - May exclude legitimate low-activity regions
   - Threshold automatically adapted but may need adjustment

## Troubleshooting

### "No source data found"
**Error:** `No source data found. Apply source localization first`

**Solution:** Apply source localization before PSD calculation:
```python
# For source localization v2.0.1+ (creates self.source_eeg)
self.apply_source_localization()
psd_df, file_path = self.apply_source_psd()  # Uses ROI mode

# For source localization v1.0.0 (creates self.stc/self.stc_list)
self.apply_source_localization()
psd_df, file_path = self.apply_source_psd()  # Uses vertex mode
```

### "Insufficient data for PSD calculation"
**Solution:**
- Reduce `segment_duration` (minimum 30s)
- Check that epochs are not too short (<2s)
- Ensure adequate clean data after artifact rejection

### High memory usage
**Solution:**
- Reduce `n_jobs` (fewer parallel batches)
- Reduce `segment_duration` (process less data)
- Close other applications
- Process in multiple stages

### Missing fsaverage data
**Solution:** MNE will auto-download (~200 MB) on first run. Ensure internet connection.

### "No vertices found for label"
**Solution:** This warning is normal for a few ROIs with source localization. Acceptable if <5% of ROIs affected.

### Unrealistic spectral patterns
**Solution:**
- Check source localization quality first
- Verify adequate preprocessing (ICA, filtering)
- Check for line noise contamination (notch filtering)
- Ensure sufficient data length (>30s minimum)

## Scientific References

1. **Welch's Method**
   - Welch P (1967). The use of fast Fourier transform for the estimation of power spectra: A method based on time averaging over short, modified periodograms. *IEEE Transactions on Audio and Electroacoustics*, 15(2), 70-73.

2. **Desikan-Killiany Atlas**
   - Desikan RS, et al. (2006). An automated labeling system for subdividing the human cerebral cortex on MRI scans into gyral based regions of interest. *NeuroImage*, 31(3), 968-980.

3. **MNE-Python Software**
   - Gramfort A, et al. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, 7, 267.

4. **Source-Level Spectral Analysis**
   - Hipp JF, et al. (2012). Large-scale cortical correlation structure of spontaneous oscillatory activity. *Nature Neuroscience*, 15(6), 884-890.

5. **Alpha Oscillations**
   - Klimesch W (2012). Alpha-band oscillations, attention, and controlled access to stored information. *Trends in Cognitive Sciences*, 16(12), 606-617.

## Version History

- **2.0.0** (2025-10-05): Dual-mode release
  - **NEW:** ROI-optimized mode for source localization v2.0.1+ (68-channel direct processing)
  - **NEW:** Automatic mode detection (self.source_eeg vs self.stc/self.stc_list)
  - **NEW:** 10-20× performance improvement in ROI mode (~30s vs 2-5min)
  - Maintains full backward compatibility with v1.0.0 vertex-level mode
  - Identical output format for both modes
  - Enhanced metadata with processing mode information
  - Added calculate_roi_psd() function
  - Updated documentation with dual-mode guidance

- **1.0.0** (2025-09-29): Initial vertex-level release
  - Welch's method PSD for source estimates (20,484 vertices)
  - ROI averaging with Desikan-Killiany atlas
  - Parallel batch processing
  - Band power extraction (8 frequency bands)
  - 4-panel diagnostic visualization
  - Parquet/CSV output formats