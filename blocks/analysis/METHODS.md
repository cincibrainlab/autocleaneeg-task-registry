# Methods: Source Localization and Spectral Analysis

## Source Localization

### Overview
Cortical source activity was estimated from scalp electroencephalography (EEG) recordings using distributed minimum norm estimation (MNE) implemented in the MNE-Python software package (version ≥1.6.0; Gramfort et al., 2013). The source localization pipeline transformed sensor-space EEG data into 68 cortical regions of interest (ROIs) defined by the Desikan-Killiany atlas (Desikan et al., 2006).

### Forward Model Construction
A three-layer boundary element model (BEM) was constructed using the FreeSurfer average brain template (fsaverage; Fischl, 2012). The forward solution was computed using a standard three-compartment head model consisting of the inner skull, outer skull, and scalp surfaces. EEG electrode positions were automatically detected from the data montage or specified using standard 10-20 system coordinates. For high-density EEG systems (>64 channels), manufacturer-specific montage templates were applied (e.g., GSN-HydroCel-129 for EGI systems). The forward model utilized a dipole source model with sources distributed across the cortical surface (approximately 20,484 vertices per hemisphere on the fsaverage template), oriented perpendicular to the cortical surface.

### Inverse Solution
Source activity was estimated using the minimum norm estimate (MNE) method (Hämäläinen & Ilmoniemi, 1994), which provides a linear inverse solution by minimizing the L2-norm of the source distribution under the constraint that it explains the observed sensor measurements. The regularization parameter (λ²) was set to 1/9 (equivalent to a signal-to-noise ratio of 3:1), following standard recommendations for cognitive neuroscience applications (Lin et al., 2006). This regularization parameter balances the dual objectives of fitting the data while maintaining physiologically plausible source estimates with minimal spatial spread.

The inverse operator was computed as:

**Ĵ** = **W M<sup>T</sup>** (**M W M<sup>T</sup>** + λ²**C**)<sup>-1</sup> **b**

where **Ĵ** represents the estimated source amplitudes, **M** is the lead field matrix (forward model), **W** is the source covariance matrix (assumed to be the identity matrix for MNE), **C** is the noise covariance matrix (estimated from pre-stimulus baseline or assumed to be the identity matrix), **b** is the measured sensor data, and λ² is the regularization parameter.

### Region-of-Interest Parcellation
Source estimates were parcellated into 68 cortical regions (34 per hemisphere) according to the Desikan-Killiany atlas (Desikan et al., 2006). This atlas provides a gyral-based anatomical parcellation of the cerebral cortex including major functional regions such as prefrontal, motor, sensory, parietal, temporal, and occipital cortices. For each ROI, time courses were computed by averaging the activity across all vertices within the region, weighted by the inverse solution. This approach reduces the high-dimensional vertex-level data (20,484 vertices) to a more tractable 68-region representation while preserving anatomical specificity and reducing computational demands for subsequent analyses.

The 68 Desikan-Killiany regions include bilateral representations of: banks of the superior temporal sulcus, caudal anterior cingulate, caudal middle frontal, cuneus, entorhinal, fusiform, inferior parietal, inferior temporal, isthmus of the cingulate, lateral occipital, lateral orbitofrontal, lingual, medial orbitofrontal, middle temporal, parahippocampal, paracentral, pars opercularis, pars orbitalis, pars triangularis, pericalcarine, postcentral, posterior cingulate, precentral, precuneus, rostral anterior cingulate, rostral middle frontal, superior frontal, superior parietal, superior temporal, supramarginal, frontal pole, temporal pole, transverse temporal, and insula.

### Data Processing and Output
Source localization was performed independently for continuous (Raw) and epoched (Epochs) data formats. The output consisted of 68-channel time series data, with each channel representing the averaged source activity within one cortical ROI. This transformation preserves the temporal resolution of the original EEG data while providing anatomically interpretable regional activity. All processing was performed using the autocleaneeg-eeg2source package (version ≥0.3.7), which implements memory-efficient batch processing with automatic cleanup of intermediate files.

---

## Power Spectral Density Analysis

### Overview
Power spectral density (PSD) was computed from source-localized ROI time series data using Welch's method (Welch, 1967), a modified periodogram approach that reduces variance in spectral estimates through averaging across overlapping windows. The analysis was optimized for 68-channel ROI data, providing approximately 10-20× faster processing compared to vertex-level spectral analysis while maintaining identical output formats.

### Data Segmentation and Preprocessing
For analyses requiring temporal specificity, a representative segment (default: 80 seconds) was extracted from the middle of each recording to maximize stationarity and minimize edge effects. For continuous data (Raw format), this segment was selected as a single contiguous block. For epoched data (Epochs format), the appropriate number of epochs was selected from the temporal center of the dataset to approximate the target duration. The use of temporally central data segments reduces potential confounds from habituation, fatigue, or arousal changes that may occur during extended recordings.

### Spectral Estimation
Power spectral density was estimated using Welch's method (Welch, 1967), implemented via the MNE-Python `compute_psd()` function. This approach segments the time series into overlapping windows, applies a Hann taper to each window to minimize spectral leakage, computes the discrete Fourier transform (DFT) for each windowed segment, and averages the resulting periodograms to reduce variance.

Window length was adaptively determined based on data type and duration:
- **Continuous data (Raw)**: Windows of up to 4 seconds were used, provided that at least 8 windows fit within the available data segment to ensure sufficient averaging for variance reduction. Shorter windows were used for briefer recordings, with a minimum of 8 windows maintained to achieve acceptable spectral estimate stability.
- **Epoched data (Epochs)**: Window length was constrained by individual epoch duration (maximum of epoch length or 4 seconds, whichever is shorter). For typical 2-second epochs, this resulted in 2-second windows (512 samples at 256 Hz), providing 0.5 Hz frequency resolution. PSD estimates from individual epochs were computed independently and then averaged across all epochs.

All windows used 50% overlap (Hann window with 50% overlap provides near-optimal variance reduction; Harris, 1978), and a Hann window taper was applied to minimize spectral leakage from neighboring frequencies. Frequency resolution was determined by the window length: frequency_resolution = sampling_rate / window_length. For example, with 256 Hz sampling and 2-second windows, the analysis achieved 0.5 Hz resolution across the 0.5-45 Hz frequency range.

The specific Welch parameters were:
- **Frequency range**: 0.5–45 Hz (spanning delta through low gamma bands while avoiding DC drift and high-frequency noise)
- **FFT length (n_fft)**: Equal to window length in samples
- **Overlap (n_overlap)**: 50% of window length
- **Window function**: Hann (von Hann) window
- **Detrending**: Linear detrend applied to each window
- **Scaling**: Density scaling (V²/Hz) for physiological interpretability

### Frequency Band Analysis
In addition to continuous spectral estimates, power was quantified within canonical frequency bands following established conventions in cognitive neuroscience (Buzsáki & Draguhn, 2004; Klimesch, 1999):

- **Delta**: 1–4 Hz (associated with sleep, attention, and reward processing)
- **Theta**: 4–8 Hz (associated with memory encoding, spatial navigation, and executive function)
- **Alpha**: 8–13 Hz (associated with wakeful rest, attention, and sensory inhibition)
  - **Low alpha**: 8–10 Hz
  - **High alpha**: 10–13 Hz
- **Beta**: 13–30 Hz (associated with motor control and cognitive processing)
  - **Low beta**: 13–20 Hz
  - **High beta**: 20–30 Hz
- **Gamma**: 30–45 Hz (associated with local cortical processing and feature binding)

Band power was computed by averaging PSD estimates across all frequency bins falling within each band's range. This approach provides robust estimates of oscillatory activity while reducing the dimensionality of spectral data for statistical analysis.

### Output and Visualization
PSD estimates were saved in two formats to facilitate different analytical approaches:

1. **Frequency-resolved data**: Parquet format files containing PSD values for each ROI at each frequency bin (subject × ROI × hemisphere × frequency), providing complete spectral information for advanced analyses.

2. **Band power summaries**: CSV format files containing averaged power within each frequency band for each ROI (subject × ROI × hemisphere × band), suitable for statistical analyses and group comparisons.

Diagnostic visualizations were generated automatically, including: (1) spectral plots for representative ROIs showing the characteristic 1/f pattern of neural oscillations, (2) hemisphere comparisons to identify lateralization effects, (3) frequency band power distributions across regions, and (4) alpha/beta ratio distributions relevant for arousal and cognitive load assessment.

### Computational Efficiency
The ROI-optimized spectral analysis processes 68 channels (one per cortical region) rather than 20,484 cortical vertices, resulting in approximately 10-20× faster computation (typically 30-60 seconds per subject) compared to vertex-level approaches while maintaining identical output formats. This efficiency enables large-scale studies and real-time applications. For epoched data, spectral estimates from individual epochs are computed in parallel when multiple epochs are available, further improving processing speed.

### Quality Assurance
Spectral estimates were visually inspected for quality using automated diagnostic plots. Key quality indicators included: (1) smooth 1/f decay pattern across frequencies characteristic of neural oscillations, (2) absence of sharp spectral peaks at line noise frequencies (50/60 Hz), (3) comparable spectral patterns across homologous left and right hemisphere regions, and (4) physiologically plausible absolute power values (typically 10⁻²⁰ to 10⁻¹⁸ V²/Hz for source-localized cortical activity).

---

## Software and Statistical Analysis

All analyses were performed using MNE-Python (version ≥1.6.0; Gramfort et al., 2013), SciPy (version ≥1.10.0; Virtanen et al., 2020), NumPy (version ≥1.24.0; Harris et al., 2020), and pandas (version ≥2.0.0; McKinney, 2010). Source localization utilized the autocleaneeg-eeg2source package (version ≥0.3.7). Statistical analyses were conducted in Python using standard parametric and non-parametric methods as appropriate. Group-level analyses employed mixed-effects models to account for within-subject correlations across regions and frequency bands. Multiple comparisons were controlled using the false discovery rate (FDR) procedure (Benjamini & Hochberg, 1995). All code is available at https://github.com/cincibrainlab/autocleaneeg-task-registry.

---

## References

Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B (Methodological)*, *57*(1), 289-300.

Buzsáki, G., & Draguhn, A. (2004). Neuronal oscillations in cortical networks. *Science*, *304*(5679), 1926-1929. https://doi.org/10.1126/science.1099745

Desikan, R. S., Ségonne, F., Fischl, B., Quinn, B. T., Dickerson, B. C., Blacker, D., ... & Killiany, R. J. (2006). An automated labeling system for subdividing the human cerebral cortex on MRI scans into gyral based regions of interest. *NeuroImage*, *31*(3), 968-980. https://doi.org/10.1016/j.neuroimage.2006.01.021

Fischl, B. (2012). FreeSurfer. *NeuroImage*, *62*(2), 774-781. https://doi.org/10.1016/j.neuroimage.2012.01.021

Gramfort, A., Luessi, M., Larson, E., Engemann, D. A., Strohmeier, D., Brodbeck, C., ... & Hämäläinen, M. (2013). MEG and EEG data analysis with MNE-Python. *Frontiers in Neuroscience*, *7*, 267. https://doi.org/10.3389/fnins.2013.00267

Hämäläinen, M. S., & Ilmoniemi, R. J. (1994). Interpreting magnetic fields of the brain: Minimum norm estimates. *Medical & Biological Engineering & Computing*, *32*(1), 35-42. https://doi.org/10.1007/BF02512476

Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., ... & Oliphant, T. E. (2020). Array programming with NumPy. *Nature*, *585*(7825), 357-362. https://doi.org/10.1038/s41586-020-2649-2

Harris, F. J. (1978). On the use of windows for harmonic analysis with the discrete Fourier transform. *Proceedings of the IEEE*, *66*(1), 51-83. https://doi.org/10.1109/PROC.1978.10837

Klimesch, W. (1999). EEG alpha and theta oscillations reflect cognitive and memory performance: A review and analysis. *Brain Research Reviews*, *29*(2-3), 169-195. https://doi.org/10.1016/S0165-0173(98)00056-3

Lin, F. H., Witzel, T., Ahlfors, S. P., Stufflebeam, S. M., Belliveau, J. W., & Hämäläinen, M. S. (2006). Assessing and improving the spatial accuracy in MEG source localization by depth-weighted minimum-norm estimates. *NeuroImage*, *31*(1), 160-171. https://doi.org/10.1016/j.neuroimage.2005.11.054

McKinney, W. (2010). Data structures for statistical computing in Python. *Proceedings of the 9th Python in Science Conference*, 56-61. https://doi.org/10.25080/Majora-92bf1922-00a

Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., ... & van Mulbregt, P. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, *17*(3), 261-272. https://doi.org/10.1038/s41592-019-0686-2

Welch, P. D. (1967). The use of fast Fourier transform for the estimation of power spectra: A method based on time averaging over short, modified periodograms. *IEEE Transactions on Audio and Electroacoustics*, *15*(2), 70-73. https://doi.org/10.1109/TAU.1967.1161901
