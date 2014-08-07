#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import inspect
import os
import re
import sys

# Third-Party Libraries
import setuptools

# Local Libraries
sys.path.insert(0, "lib"); import about
sys.path.insert(0, "docbench"); import __about__ as about_docbench

lines = open("README.md").read().splitlines()
about_docbench.__doc__ = "\n".join([lines[0]] + lines[2:])
metadata = about.get_metadata(about_docbench)

contents = dict(
  packages = ["docbench"],
)

requirements = dict(
  install_requires = ["lsprofcalltree", "path.py"],
)

info = {}
info.update(metadata)
info.update(contents)
info.update(requirements)

if __name__ == "__main__":
    setuptools.setup(**info)

