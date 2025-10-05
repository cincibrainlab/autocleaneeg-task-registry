"""RestingState_SourcePSD - Complete resting-state pipeline with source analysis.

This task provides a complete workflow from raw EEG to cortical source-level PSD:
- Standard preprocessing (filtering, ICA, artifact rejection, epoching)
- MNE source localization to 10,242 cortical vertices using fsaverage template
- ROI-level PSD calculation for 68 Desikan-Killiany anatomical regions
- Frequency band power extraction (delta, theta, alpha, beta, gamma)
- Comprehensive visualization reports

Ideal for: Resting-state qEEG studies requiring regional spectral analysis,
group-level statistical comparisons, or clinical biomarker extraction.

Outputs:
- Preprocessed sensor-space data (epochs)
- Source estimates (STCs) for each epoch
- ROI PSD data (parquet) with full frequency resolution
- Band power summaries (CSV) for statistical analysis
- Diagnostic visualizations (PNG)

References:
- MNE source localization: Hämäläinen & Ilmoniemi (1994)
- Desikan-Killiany atlas: Desikan et al. (2006)
- Welch's PSD method: Welch (1967)
"""

from __future__ import annotations

from autoclean.core.task import Task

config = {
    "schema_version": "2025.09",
    "resample_step": {"enabled": True, "value": 256},
    "filtering": {
        "enabled": True,
        "value": {
            "l_freq": 0.1,
            "h_freq": 45,
            "notch_freqs": [50, 60],
            "notch_widths": 5,
        },
    },
    "drop_outerlayer": {"enabled": False, "value": []},
    "eog_step": {
        "enabled": True,
        "value": {"eog_indices": [31, 32], "eog_drop": True},
    },
    "trim_step": {"enabled": True, "value": 4},
    "crop_step": {"enabled": False, "value": {"start": 0, "end": 120}},
    "reference_step": {"enabled": True, "value": "average"},
    "montage": {"enabled": True, "value": "standard_1020"},
    "ICA": {
        "enabled": True,
        "value": {
            "method": "infomax",
            "n_components": None,
            "fit_params": {"ortho": False, "extended": True},
            "temp_highpass_for_ica": 2.0,
        },
    },
    "component_rejection": {
        "enabled": True,
        "method": "iclabel",
        "value": {
            "ic_flags_to_reject": ["muscle", "heart", "eog", "ch_noise", "line_noise"],
            "ic_rejection_threshold": 0.3,
            "ic_rejection_overrides": {"muscle": 0.90},
            "psd_fmax": 45,
        },
    },
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -1, "tmax": 1},
        "event_id": None,
        "remove_baseline": {"enabled": False, "window": [-0.2, 0]},
        "threshold_rejection": {
            "enabled": False,
            "volt_threshold": {"eeg": 0.000125},
        },
    },
    "apply_source_localization": {
        "enabled": True,
        "value": {
            "method": "MNE",
            "lambda2": 0.111,
            "pick_ori": "normal",
            "n_jobs": 10,
            "convert_to_eeg": False,
        },
    },
    "apply_source_psd": {
        "enabled": True,
        "value": {"segment_duration": 80, "n_jobs": 4, "generate_plots": True},
    },
}


class RestingState_SourcePSD(Task):
    """Complete resting-state pipeline with MNE source localization and ROI PSD."""

    def run(self) -> None:
        """Execute the complete preprocessing and source analysis pipeline."""
        # Import and basic preprocessing
        self.import_raw()

        # Drop reference electrodes (A1=left mastoid, A2=right mastoid)
        # These were the recording reference, not independent brain signals.
        # Since we use average reference, they're excluded from all analysis.
        self.set_channel_types({"A1": "misc", "A2": "misc"}, drop=True)

        self.resample_data()
        self.assign_eog_channels()
        self.trim_edges()
        self.crop_duration()
        self.filter_data()

        # Store original for comparison
        self.original_raw = self.raw.copy()

        # BIDS-compliant paths
        self.create_bids_path()

        # Channel cleaning and referencing
        self.clean_bad_channels()
        self.rereference_data()

        # Artifact detection
        self.annotate_noisy_epochs()
        self.annotate_uncorrelated_epochs()
        self.detect_dense_oscillatory_artifacts()

        # ICA artifact removal
        self.run_ica()
        self.classify_ica_components(method="iclabel", reject=True)
        self.drop_eog_channels()

        # Epoching and cleaning
        self.create_regular_epochs(export=True)
        self.detect_outlier_epochs()
        self.gfp_clean_epochs()

        # Source analysis pipeline
        self.apply_source_localization()  # Creates self.stc_list from epochs
        self.apply_source_psd()  # Calculates ROI-level PSD

        # Generate reports
        self.generate_reports()

    def generate_reports(self) -> None:
        """Generate quality control visualizations."""
        if self.raw is None or self.original_raw is None:
            return

        self.plot_raw_vs_cleaned_overlay(self.original_raw, self.raw)
        self.step_psd_topo_figure(self.original_raw, self.raw)
