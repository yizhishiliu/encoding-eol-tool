from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules=cythonize(
        "core_logic.py",                  # 要加密的源码
        compiler_directives={"language_level": "3"},
    )
)
