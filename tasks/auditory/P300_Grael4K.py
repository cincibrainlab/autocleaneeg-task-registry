"""P300 Grael4K task implementation with event-related potential processing."""

from __future__ import annotations

from autoclean.core.task import Task

config = {
    "schema_version": "2025.09",
    "dataset_name": "GRAEL4K_P300",
    "input_path": "",
    "montage": {"enabled": True, "value": "standard_1020"},
    "move_flagged_files": False,
    "resample_step": {"enabled": True, "value": 256},
    "filtering": {
        "enabled": True,
        "value": {"l_freq": 0.1, "h_freq": 45.0, "notch_freqs": [50, 60]},
    },
    "drop_outerlayer": {"enabled": False, "value": []},
    "eog_step": {
        "enabled": True,
        "value": {
            "eog_indices": [31, 32],
            "eog_drop": True,
        },
    },
    "trim_step": {"enabled": False, "value": 4},
    "crop_step": {"enabled": False, "value": {"start": 0, "end": 120}},
    "reference_step": {"enabled": True, "value": "average"},
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
            "ic_flags_to_reject": [
                "muscle",
                "heart",
                "eog",
                "ch_noise",
                "line_noise",
            ],
            "ic_rejection_threshold": 0.3,
            "ic_rejection_overrides": {"muscle": 0.90},
            "psd_fmax": 45.0,  # Align PSD plots with band-limited filtering
        },
    },
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -0.5, "tmax": 1.0},
        "event_id": {"Standard": 13, "Target": 14},
        "remove_baseline": {"enabled": False, "window": [-0.2, 0.0]},
        "threshold_rejection": {
            "enabled": False,
            "volt_threshold": {"eeg": 0.000125},
        },
    },
    "ai_reporting": False,
}


class P300_Grael4K(Task):
    """P300 Grael4K task for event-related potential analysis.

    This task implements the P300 oddball paradigm for the Grael4K dataset
    with standard 10-20 montage. Includes comprehensive artifact rejection
    and quality control visualizations.

    Montage: standard_1020
    EOG Channels: 31, 32
    """

    def run(self) -> None:
        """Run the P300 processing pipeline."""
        # Import raw EEG data
        self.import_raw()

        # Set channel types for auxiliary channels
        self.raw.set_channel_types({"A1": "misc", "A2": "misc"})

        # Basic preprocessing steps
        self.resample_data()
        self.assign_eog_channels()
        self.trim_edges()
        self.crop_duration()

        self.filter_data()
        self.drop_outer_layer()

        # Store original for comparison
        self.original_raw = self.raw.copy()

        # Channel cleaning
        self.clean_bad_channels()

        # Re-referencing
        self.rereference_data()

        # Artifact detection
        self.annotate_noisy_epochs()
        self.annotate_uncorrelated_epochs()
        self.detect_dense_oscillatory_artifacts()

        # ICA processing
        self.run_ica()

        # ICA component classification
        self.classify_ica_components(method="iclabel")

        # Epoching - using event IDs from config
        self.create_eventid_epochs()

        # Detect outlier epochs
        self.detect_outlier_epochs()

        # Clean epochs using GFP
        self.gfp_clean_epochs()

        # Generate visualization reports
        self.generate_reports()

    def generate_reports(self) -> None:
        """Generate quality control visualizations and reports."""
        if self.raw is None or self.original_raw is None:
            return

        # Plot raw vs cleaned overlay using mixin method
        self.plot_raw_vs_cleaned_overlay(self.original_raw, self.raw)

        # Plot PSD topography using mixin method
        self.step_psd_topo_figure(self.original_raw, self.raw)
