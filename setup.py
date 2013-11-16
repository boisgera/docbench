#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import inspect
import os
import os.path
import re
import sys

# Third-Party Libraries
import about
import setuptools

# ------------------------------------------------------------------------------
def get_some_reST(markdown):
    "Markdown to reStructuredText converter"
    try:
        import sh; pandoc = sh.pandoc
    except:
        error  = "sh.py and/or pandoc not available.\n"
        error += "  sh.py:  <http://amoffat.github.io/sh/>\n"
        error += "  pandoc: <http://johnmacfarlane.net/pandoc/>"
        raise ImportError(error)
    with open("tmp.md", "w") as markdown_file:
        markdown_file.write(markdown)
    restructuredtext = sh.pandoc("-w", "rst", "tmp.md")
    os.remove("tmp.md")
    return restructuredtext


# ------------------------------------------------------------------------------

metadata = about.get_metadata("docbench/__about__.py")

contents = dict(
  packages = ["docbench"],
)

requirements = dict(
  install_requires = ["lsprofcalltree", "path.py==3.2"],
)

info = {}
info.update(metadata)
info.update(contents)
info.update(requirements)

if __name__ == "__main__":
    if "register" in sys.argv[1:]:
         README_md = open("README.md").read()
         README_rst = get_some_reST(README_md)
         info["long_description"] = README_rst
    setuptools.setup(**info)

