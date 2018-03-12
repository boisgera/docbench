#!/usr/bin/env python
# coding: utf-8

# Python Standard Library
import inspect
import os.path
import re
import sys

# Pip Package Manager
try:
    import pip
    import setuptools
    import pkg_resources
except ImportError:
    error = "pip is not installed, refer to <{url}> for instructions."
    raise ImportError(error.format(url="http://pip.readthedocs.org"))

# Redistributed Third-Party ("Vendor") Libraries 
def local(path):
    return os.path.join(os.path.dirname(__file__), path)

sys.path.insert(1, local(".lib"))
try:
    setup_requires = ["about>=5.2<6"]
    require = lambda *r: pkg_resources.WorkingSet().require(*r)
    require(*setup_requires)
    import about
except pkg_resources.DistributionNotFound:
    error = """{req!r} not found; install it locally with:

    pip install --target=.lib --ignore-installed {req!r}
"""
    raise ImportError(error.format(req=" ".join(setup_requires)))


# Setup
# ------------------------------------------------------------------------------
sys.path.insert(0, "docbench"); import __about__
metadata = about.get_metadata(__about__)

contents = dict(
  packages = ["docbench"],
)

install_requires = ["lsprofcalltree>=0.0.3"]
if sys.version_info < (3, 0):
    install_requires.append("pathlib2")

requirements = dict(
  install_requires = install_requires,
)

info = {}
info.update(metadata)
info.update(contents)
info.update(requirements)

if __name__ == "__main__":
    setuptools.setup(**info)

