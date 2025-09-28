"""RestingEyesQuickCheck template.

Lightweight resting-state cleaning intended for pre-session impedance/quality checks.
"""

from __future__ import annotations

from autoclean.core.task import Task

# Focus on a quick sanity sweep with minimal processing so technicians can
# verify signal quality before a full acquisition.
config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "GSN-HydroCel-129"},
    "move_flagged_files": False,
    "resample_step": {"enabled": True, "value": 200},
    "filtering": {
        "enabled": True,
        "value": {"l_freq": 1.0, "h_freq": 45.0, "notch_freqs": [60]},
    },
    "drop_outerlayer": {"enabled": False, "value": []},
    "eog_step": {
        "enabled": True,
        "value": [1, 32, 8, 14, 17, 21, 125, 126, 127, 128],
    },
    "trim_step": {"enabled": True, "value": 2},
    "crop_step": {"enabled": True, "value": {"start": 0, "end": 120}},
    "reference_step": {"enabled": True, "value": "average"},
    "ICA": {
        "enabled": False,
        "value": {
            "method": "infomax",
            "n_components": None,
            "fit_params": {"extended": True},
            "temp_highpass_for_ica": 1.0,
        },
    },
    "component_rejection": {
        "enabled": False,
        "method": "icvision",
        "value": {
            "ic_flags_to_reject": [
                "muscle",
                "heart",
                "eog",
                "ch_noise",
                "line_noise",
            ],
            "ic_rejection_threshold": 0.3,
            "psd_fmax": 45.0,
        },
    },
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -0.5, "tmax": 0.5},
        "event_id": None,
        "remove_baseline": {"enabled": False, "window": [None, 0]},
        "threshold_rejection": {
            "enabled": False,
            "volt_threshold": {"eeg": 0.000150},
        },
    },
    "ai_reporting": False,
}


class RestingEyesQuickCheck(Task):
    """Minimal cleaning pass for fast resting-state quality checks."""

    def run(self) -> None:
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.assign_eog_channels()
        self.trim_edges()
        self.crop_duration()

        self.original_raw = self.raw.copy()

        # Skip ICA for speed; focus on channel health and obvious artifacts.
        self.clean_bad_channels()
        self.rereference_data()

        self.annotate_noisy_epochs()
        self.annotate_uncorrelated_epochs()

        self.create_regular_epochs(export=False)
        self.detect_outlier_epochs()

        self.generate_reports()

    def generate_reports(self) -> None:
        if self.raw is None or self.original_raw is None:
            return

        self.plot_raw_vs_cleaned_overlay(self.original_raw, self.raw)
        self.step_psd_topo_figure(self.original_raw, self.raw)
