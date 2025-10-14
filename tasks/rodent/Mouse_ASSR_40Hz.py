from autoclean.core.task import Task

# =============================================================================
#                     30-channel mouse multielectrode array (MEA) EEG recordings of 40Hz ASSR EEG PREPROCESSING CONFIGURATION
# =============================================================================
# This configuration controls how your 30-channel mouse multielectrode array (MEA) EEG recordings of 40Hz ASSR EEG data will be
# automatically cleaned and processed. Each section handles a different aspect
# of the preprocessing pipeline.
#
# 🟢 enabled: True  = Apply this processing step
# 🔴 enabled: False = Skip this processing step
#
# 💡 TIP: A web-based configuration wizard is available to generate this
#         automatically - you shouldn't need to edit this manually!
# =============================================================================

config = {
    "schema_version": "2025.09",
    'resample_step': {
        'enabled': True,
        'value': 250
    },
    'filtering': {
        'enabled': True,
        'value': {
            'l_freq': 1,
            'h_freq': 100,
            'notch_freqs': [60, 120],
            'notch_widths': 5
        }
    },
    'drop_outerlayer': {
        'enabled': False,
        'value': []
    },
    'eog_step': {
        'enabled': False,
        'value': []
    },
    'trim_step': {
        'enabled': True,
        'value': 4
    },
    'crop_step': {
        'enabled': False,
        'value': {
            'start': 0,
            'end': None
        }
    },
    'reference_step': {
        'enabled': True,
        'value': 'average'
    },
    'montage': {
        'enabled': True,
        'value': 'MEA30'
    },
    'ICA': {
        'enabled': False,
        'value': {
            'method': 'infomax',
            'n_components': None,
            'fit_params': {
                'extended': True
            }
        }
    },
    'component_rejection': {
        'enabled': False,
        'method': 'iclabel',
        'value': {
            'ic_flags_to_reject': ['heart', 'ch_noise', 'line_noise'],
            'ic_rejection_threshold': 0.3,
            'ic_rejection_overrides': {},
            'psd_fmax': 100
        }
    },
    'epoch_settings': {
        'enabled': True,
        'value': {
            'tmin': -0.2,
            'tmax': 0.8
        },
        'event_id': {"assr": 1},
        'remove_baseline': {
            'enabled': True,
            'window': [-0.2, 0]
        },
        'threshold_rejection': {
            'enabled': False,
            'volt_threshold': {
                'eeg': 0.000125
            }
        }
    },
    'move_flagged_files': False
}

class ASSR40Hz_TTLpulses(Task):

    def run(self) -> None:
        # Import raw EEG data
        self.import_raw()

        #Basic preprocessing steps
        self.resample_data()

        self.filter_data()

        self.drop_outer_layer()

        self.assign_eog_channels()

        self.trim_edges()

        self.crop_duration()

        self.original_raw = self.raw.copy()

        # Channel cleaning
        self.clean_bad_channels()

        # Re-referencing
        self.rereference_data()

        # Artifact detection
        self.annotate_noisy_epochs()
        self.annotate_uncorrelated_epochs()
        self.detect_dense_oscillatory_artifacts()

        # ICA processing with optional export
        self.run_ica()  # Export after ICA
        self.classify_ica_components()

        # Epoching with export
        self.create_eventid_epochs() # Using event IDs

        # Detect outlier epochs
        self.detect_outlier_epochs()

        # Clean epochs using GFP with export
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

        # Additional report generation can be added here
