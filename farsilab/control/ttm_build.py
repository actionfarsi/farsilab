# Run  python ttm_build.py build_ext --inplace

import numpy as np
from distutils.core import setup
from Cython.Build import cythonize

print(np.get_include())

setup(
    ext_modules = cythonize("ttm_c.pyx"),
    include_dirs = [np.get_include(), "C:/Anaconda3/lib/site-packages/numpy/core/include"],
)
