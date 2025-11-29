"""Mouse ASSR 40Hz task with TTL pulses.

This task implements the 40Hz ASSR (Auditory Steady-State Response) protocol
for mouse recordings using MEA30 electrode arrays with TTL pulse-based event
detection optimized for preclinical studies.
"""

from __future__ import annotations

from autoclean.core.task import Task

config = {
    "schema_version": "2025.09",
    "montage": {"enabled": True, "value": "MEA30"},
    "move_flagged_files": False,
    "resample_step": {"enabled": True, "value": 500},
    "filtering": {
        "enabled": True,
        "value": {"l_freq": 1.0, "h_freq": 100.0, "notch_freqs": [60, 120]},
    },
    "drop_outerlayer": {"enabled": False, "value": []},
    "eog_step": {
        "enabled": False,
        "value": {
            "eog_indices": [],
            "eog_drop": False,
        },
    },
    "trim_step": {"enabled": True, "value": 2},
    "crop_step": {"enabled": False, "value": {"start": 0, "end": 0}},
    "reference_step": {"enabled": False, "value": "average"},
    "ICA": {
        "enabled": False,
        "value": {
            "method": "fastica",
            "n_components": None,
            "fit_params": {"tol": 0.0001},
            "temp_highpass_for_ica": 1.0,
        },
    },
    "component_rejection": {
        "enabled": False,
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
            "psd_fmax": 100.0,
        },
    },
    "epoch_settings": {
        "enabled": True,
        "value": {"tmin": -0.2, "tmax": 0.8},
        "event_id": {"assr_40hz": 1},
        "remove_baseline": {"enabled": True, "window": [-0.2, 0.0]},
        "threshold_rejection": {
            "enabled": False,
            "volt_threshold": {"eeg": 0.000125},
        },
    },
    "ai_reporting": False,
}


class Mouse_ASSR_40Hz(Task):
    """Task for mouse 40Hz ASSR recordings with TTL pulse event detection."""

    def run(self) -> None:
        self.import_raw()
        self.resample_data()
        self.filter_data()
        self.drop_outer_layer()
        self.assign_eog_channels()
        self.trim_edges()
        self.crop_duration()

        self.original_raw = self.raw.copy()

        self.clean_bad_channels()
        self.raw.interpolate_bads(reset_bads=False)

        self.create_eventid_epochs()

        self.generate_reports()

    def generate_reports(self) -> None:
        if self.raw is None:
            return

        self.verify_topography_plot()
