from src.core import fitter
from src.core import adjust_globals

adjust_globals(features = 3, error_diff = 0.01)
print fitter('./tests/test1.points', True)	
adjust_globals(features = 3, error_diff = 0.01,correction_factor = 0.01)
print fitter('./tests/test2.points', True)	