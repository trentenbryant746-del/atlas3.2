from setuptools import setup
from Cython.Build import cythonize
setup(ext_modules=cythonize("planck.pyx", quiet=True),
      script_args=["build_ext", "--inplace"])
