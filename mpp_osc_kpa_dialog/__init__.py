from pathlib import Path
from .main import MPP_Osc_Dialog

__version__ = '0.1.0'

def plugin_mpp_cwd():
    return Path(__file__).parent