"""Resting-state EEG processing with wavelet_threshold block.

This task demonstrates using the wavelet_threshold processing block
as an alternative to ICA for artifact removal in resting-state data.

Processing Block: wavelet_threshold (signal_processing)
Version: 1.0.0
"""

from __future__ import annotations

from autoclean.core.task import Task


config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "standard_1020"},
    "move_flagged_files": False,

    # Basic preprocessing
    "resample_step": {"enabled": True, "value": 250},
    "filtering": {
        "enabled": True,
        "value": {
            "l_freq": 1.0,
            "h_freq": 45.0,
            "notch_freqs": [60.0],
            "notch_widths": 4.0,
        },
    },
    "drop_outerlayer": {"enabled": False, "value": []},
    "trim_step": {"enabled": True, "value": 2.0},
    "crop_step": {"enabled": False, "value": {"start": 0.0, "end": 0.0}},
    "eog_step": {"enabled": False, "value": []},

    # Wavelet threshold processing block (replaces ICA)
    "wavelet_threshold": {
        "enabled": True,
        "value": {
            "wavelet": "sym4",
            "level": 5,
            "threshold_mode": "soft",
            "threshold_scale": 1.0,
            "is_erp": False,
            "bandpass": (1.0, 30.0),
            "filter_kwargs": None,
            "psd_fmax": 45.0,
            "picks": "eeg",
        },
    },

    # Rereferencing
    "reference_step": {"enabled": True, "value": "average"},

    # ICA disabled - using wavelet instead
    "ICA": {
        "enabled": False,
        "value": {
            "method": "fastica",
            "n_components": None,
            "max_iter": "auto",
            "random_state": 97,
        },
    },
    "component_rejection": {
        "enabled": False,
        "method": "icvision",
        "value": {
            "ic_flags_to_reject": ["muscle", "heart", "eog", "ch_noise", "line_noise"],
            "ic_rejection_threshold": 0.3,
            "psd_fmax": 80.0,
        },
    },

    # Epoching
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -1.0, "tmax": 1.0},
        "event_id": None,
        "remove_baseline": {"enabled": False, "window": [None, 0.0]},
        "threshold_rejection": {
            "enabled": False,
            "volt_threshold": {"eeg": 0.000125},
        },
    },

    "ai_reporting": False,
}


class RestingState_WaveletDemo(Task):
    """Resting-state task using wavelet_threshold for artifact removal."""

    def run(self) -> None:
        """Execute resting-state processing with wavelet thresholding."""

        # Import and basic preprocessing
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.trim_edges()

        # Apply wavelet threshold (core artifact removal)
        self.apply_wavelet_threshold()

        # Post-processing
        self.rereference_data()
        self.create_regular_epochs(export=True)