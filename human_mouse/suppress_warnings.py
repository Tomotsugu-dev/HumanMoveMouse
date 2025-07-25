"""
Suppress sklearn version warnings
"""
import warnings
from sklearn.exceptions import InconsistentVersionWarning

# Suppress the sklearn version warnings
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning, 
                       message="covariance is not symmetric positive-semidefinite")