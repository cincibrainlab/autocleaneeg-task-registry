# tasks/resting/BiotrialResting1020.py
"""BiotrialResting1020 task implementation for resting-state qEEG processing."""

from typing import Any, Dict
from autoclean.core.task import Task

# =============================================================================
#                  Resting-State qEEG PREPROCESSING CONFIGURATION
# =============================================================================
# This configuration controls how your resting-state qEEG data will be
# automatically cleaned and processed. Each section handles a different aspect
# of the preprocessing pipeline.
#
# 🟢 enabled: True  = Apply this processing step
# 🔴 enabled: False = Skip this processing step
#
# 💡 TIP: Use the AutoClean configuration wizard to generate settings
#         automatically, or copy settings from existing tasks!
# =============================================================================

config = {
    'resample_step': {
        'enabled': True,
        'value': 256
    },
    'filtering': {
        'enabled': True,
        'value': {
            'l_freq': .1,
            'h_freq': 45,
            'notch_freqs': [50, 60],
            'notch_widths': 5
        }
    },
    'drop_outerlayer': {
        'enabled': False,
        'value': []
    },
    'eog_step': {
        'enabled': True,
        'value': {
            'eog_indices': [31, 32],
            'eog_drop': True
        }
    },
    'trim_step': {
        'enabled': True,
        'value': 4
    },
    'crop_step': {
        'enabled': False,
        'value': {
            'start': 0,
            'end': 120
        }
    },
    'reference_step': {
        'enabled': True,
        'value': 'average'
    },
    'montage': {
        'enabled': True,
        'value': 'standard_1020'
    },
    'ICA': {
        'enabled': True,
        'value': {
            'method': 'infomax',
            'n_components': None,
            'fit_params': {
                'ortho': False,
                'extended': True
            },
            'temp_highpass_for_ica': 2.0
        }
    },
    'component_rejection': {
        'enabled': True,
        'method': 'iclabel',
        'value': {
            'ic_flags_to_reject': ['muscle', 'heart', 'eog', 'ch_noise', 'line_noise'],
            'ic_rejection_threshold': 0.3,
            'ic_rejection_overrides': {        # Optional per-type overrides
                'muscle': 0.90                 # 
            },
            'psd_fmax': 45  # Set to low-pass filter for accurate images for ICVISION
        }
    },
    'epoch_settings': {
        'enabled': True,
        'value': {
            'tmin': -1,
            'tmax': 1
        },
        'event_id': None,
        'remove_baseline': {
            'enabled': False,
            'window': [-0.2, 0]
        },
        'threshold_rejection': {
            'enabled': False,
            'volt_threshold': {
                'eeg': 0.000125
            }
        }
    }
}


class BiotrialResting1020(Task):
    """BiotrialResting1020 resting-state qEEG task implementation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the BiotrialResting1020 task.
        
        Parameters
        ----------
        config : Dict[str, Any]
            Configuration dictionary from the pipeline
        """
        # Initialize data containers
        self.raw = None
        self.original_raw = None
        self.epochs = None
        
        # Call parent initialization - IMPORTANT!
        super().__init__(config)

    def run(self) -> None:
        """Run the resting-state qEEG processing pipeline."""
        # Import raw EEG data
        self.import_raw()

        # Set channel types
        self.raw.set_channel_types({"A1": "misc", "A2": "misc"})

        # Basic preprocessing steps
        self.resample_data()
        self.assign_eog_channels()
        self.trim_edges()
        self.crop_duration()

        self.filter_data()
        # self.drop_outer_layer()

        # Store original for comparison
        self.original_raw = self.raw.copy()
        
        # Create BIDS-compliant paths and filenames
        self.create_bids_path()
        
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
        
        self.classify_ica_components(
            method='iclabel',
            reject=True,  # Will use rejection settings from config
        )
        
        # Drop EOG channels after ICA processing
        self.drop_eog_channels()

        # Epoching with export
        self.create_regular_epochs(export=True)  # Export epochs
        
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
