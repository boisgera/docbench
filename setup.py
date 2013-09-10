#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import inspect
import os
import os.path
import re
import sys

# Third-Party Libraries
import setuptools

# ------------------------------------------------------------------------------

def get_metadata(module):
    "Extract and process embedded module metadata"
 
    metadata = {}

    # Read the relevant __*__ module attributes
    for name in "name author version license url classifiers".split():
        value = getattr(module, "__" + name + "__", None)
        if value:
            metadata[name] = value

    # Search for author email with <...@...> syntax in the author field
    author = metadata.get("author", None)
    if author:
        email_pattern = r"<([^>]+@[^>]+)>"
        match = re.search(email_pattern, author)
        if match:
            metadata["author_email"] = email = match.groups()[0]
            metadata["author"] = author.replace("<" + email + ">", "").strip()

    # Get the module short description from the docstring
    doc = inspect.getdoc(module) or ""
    if doc:
        lines = doc.splitlines()
        metadata["description"] = lines[0]

    # Process trove classifiers
    classifiers = metadata.get("classifiers", None)
    if classifiers and isinstance(classifiers, str):
        classifiers = [l.strip() for l in classifiers.splitlines() if l.strip()]
        metadata["classifiers"] = classifiers

    return metadata

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

sys.path.insert(0, ".")
import docbench
metadata = get_metadata(docbench)

contents = dict(
  py_modules = [metadata["name"]],
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
         metadata["long_description"] = README_rst
    setuptools.setup(**info)

