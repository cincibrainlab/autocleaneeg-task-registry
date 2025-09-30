# FOOOF Spectral Parameterization Examples

These examples demonstrate using FOOOF (Fitting Oscillations & One Over F) to separate neural power spectra into periodic (oscillatory) and aperiodic (1/f background) components.

## Examples

### FOOOFAnalysisTest.py
**Purpose**: Complete spectral parameterization of source-localized EEG data

**What it demonstrates**:
- Source localization on continuous resting-state EEG
- Extracting aperiodic parameters (1/f background)
- Extracting periodic parameters (oscillatory peaks)
- Vertex-level analysis across cortical surface (20,484 vertices)

**Output files**:
- `derivatives/source_localization/*.h5` - Source estimates (STCs)
- `derivatives/fooof/*_psd-stc.h5` - Vertex-level PSD
- `derivatives/fooof/*_fooof_aperiodic.parquet` - Aperiodic parameters (offset, exponent, knee)
- `derivatives/fooof/*_fooof_aperiodic.csv` - Human-readable CSV version
- `derivatives/fooof/*_fooof_periodic.parquet` - Periodic parameters (center frequency, power, bandwidth)
- `derivatives/fooof/*_fooof_periodic.csv` - Human-readable CSV version

**Use case**: When you want to separate oscillatory activity from broadband 1/f background to better understand neural dynamics.

---

## What is FOOOF?

FOOOF parameterizes neural power spectra into two components:

### 1. Aperiodic Component (1/f background)
- **Offset**: Overall power level
- **Exponent**: Slope of 1/f decay (steeper = more inhibition)
- **Knee**: Bend point where slope changes (optional)

### 2. Periodic Component (oscillatory peaks)
- **Center Frequency**: Peak location in Hz
- **Power**: Peak amplitude above aperiodic background
- **Bandwidth**: Peak width (narrower = more rhythmic)

## Configuration Options

### Key Parameters

```python
"apply_fooof_aperiodic": {
    "enabled": True,
    "value": {
        "fmin": 1.0,              # Minimum frequency (Hz)
        "fmax": 45.0,             # Maximum frequency (Hz)
        "n_jobs": 4,              # Parallel jobs
        "aperiodic_mode": "knee"  # "fixed" or "knee"
    }
}

"apply_fooof_periodic": {
    "enabled": True,
    "value": {
        "freq_bands": {
            "delta": (1, 4),
            "theta": (4, 8),
            "alpha": (8, 13),
            "beta": (13, 30),
            "gamma": (30, 45)
        },
        "n_jobs": 4,
        "aperiodic_mode": "knee"
    }
}
```

### Important Notes

1. **Requires Continuous Data**: FOOOF needs source estimates from Raw data, not Epochs
   - Set `epoch_settings.enabled: False` in task config
   - Source localization creates `self.stc` from Raw data

2. **Frequency Range**: Choose based on your research question
   - Standard: 1-45 Hz (excludes high-frequency muscle artifacts)
   - Extended: 1-100 Hz (if interested in high gamma)
   - Narrow: 3-30 Hz (if focusing on specific bands)

3. **Aperiodic Mode**:
   - `"knee"`: Use for EEG data (allows for bend in spectrum)
   - `"fixed"`: Use if you want simple linear 1/f fit

4. **Processing Time**:
   - ~5-10 minutes per subject for vertex-level analysis
   - 20,484 vertices × 2 hemispheres = 40,968 FOOOF fits per subject

## Interpreting Results

### Aperiodic Parameters
```python
import pandas as pd

# Load aperiodic results
df = pd.read_parquet("derivatives/fooof/subject_fooof_aperiodic.parquet")

# Higher exponent = steeper 1/f slope = more inhibition
# Lower exponent = flatter spectrum = more excitation
print(df[['vertex_id', 'exponent', 'offset', 'knee', 'r_squared']])
```

### Periodic Parameters
```python
# Load periodic results
df = pd.read_parquet("derivatives/fooof/subject_fooof_periodic.parquet")

# Find alpha peaks in occipital regions
alpha_peaks = df[(df['band'] == 'alpha') & (df['power'] > threshold)]
print(alpha_peaks[['vertex_id', 'center_frequency', 'power', 'bandwidth']])
```

## Downstream Analysis

After FOOOF analysis, you can:
- **Statistical Analysis**: Compare parameters across groups/conditions
- **Spatial Mapping**: Visualize parameter distributions on cortical surface
- **Correlation Analysis**: Relate parameters to behavioral measures
- **Longitudinal Studies**: Track developmental or clinical changes

## Scientific Background

### Key Insights from FOOOF
1. **Oscillations are peaks above 1/f**: Traditional band power conflates periodic and aperiodic
2. **Aperiodic exponent reflects E/I balance**: Steeper = more inhibition
3. **Peak bandwidth reflects rhythmicity**: Narrower = more sustained oscillation
4. **1/f offset reflects overall power**: May relate to signal quality or neural mass activity

### Methodological Advantages
- **Separates overlapping components**: Distinguishes true oscillations from broadband changes
- **Robust to noise**: Model fitting is less sensitive to artifacts than raw power
- **Physiologically interpretable**: Parameters map to known neural mechanisms
- **Reproducible**: Consistent results across sessions and subjects

## Scientific References

- **Donoghue T, et al. (2020)**. Parameterizing neural power spectra into periodic and aperiodic components. *Nature Neuroscience*, 23(12), 1655-1665.
  - Original FOOOF paper introducing the method

- **Gao R, et al. (2017)**. Inferring synaptic excitation/inhibition balance from field potentials. *NeuroImage*, 158, 70-78.
  - Theoretical basis for aperiodic exponent as E/I balance

- **Ostlund BD, et al. (2022)**. Behavioral and cognitive correlates of the aperiodic (1/f-like) exponent of the EEG power spectrum in adolescents with and without ADHD. *Developmental Cognitive Neuroscience*, 48, 100931.
  - Clinical application example

- **Donoghue T, et al. (2021)**. Methodological considerations for studying neural oscillations. *European Journal of Neuroscience*, 55(11-12), 3502-3527.
  - Best practices and methodological guidance

## Common Use Cases

### Research Questions Suited for FOOOF:
- ✅ Age-related changes in cortical excitability (aperiodic exponent)
- ✅ Clinical differences in oscillatory activity (e.g., alpha power in depression)
- ✅ Effects of pharmacological interventions on E/I balance
- ✅ Developmental trajectories of neural rhythms
- ✅ Resting-state biomarkers for neurological disorders

### Not Well-Suited For:
- ❌ Event-related dynamics (use time-frequency analysis instead)
- ❌ Phase-based analyses (FOOOF only works on power spectra)
- ❌ Very short data segments (<2 seconds of data)

## Running the Examples

```bash
# FOOOF analysis (continuous data)
autocleaneeg-pipeline process --task FOOOFAnalysisTest --file /path/to/data.set

# Check outputs
ls derivatives/fooof/
# Expected:
# - sub-001_psd-stc.h5
# - sub-001_fooof_aperiodic.parquet
# - sub-001_fooof_aperiodic.csv
# - sub-001_fooof_periodic.parquet
# - sub-001_fooof_periodic.csv
```

## Troubleshooting

**Issue**: "FOOOF fit failed for many vertices"
- **Solution**: Check frequency range - may need to exclude noisy frequencies
- **Solution**: Verify data quality - heavy artifacts can prevent good fits

**Issue**: "No periodic peaks detected"
- **Solution**: May be expected in some brain regions or states
- **Solution**: Try adjusting `peak_threshold` in FOOOF settings

**Issue**: "Processing very slow"
- **Solution**: Increase `n_jobs` parameter for more parallel processing
- **Solution**: Reduce frequency range to fit fewer frequency bins