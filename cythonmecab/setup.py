from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from Cython.Build import cythonize

setup(
    name = "cymecab",
    ext_modules = cythonize(
        Extension("cymecab",
                  sources=["cymecab.pyx", "cymecab_.cpp"],
                  extra_compile_args=[
                      "-O3",
                      "-L/usr/local/lib", "-lmecab", "-lstdc++"
                  ],
                  language="c++",
        ),
    ),
    cmdclass = {'build_ext': build_ext},
)
