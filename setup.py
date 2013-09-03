#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import os.path
import re
import sys

# Third-Party Libraries
import setuptools



def get_info(module):
    "Extract module metadata"
 
    info = {}

    # Read the relevant __*__ module attributes
    for name in "name author license url version doc".split():
        value = getattr(module, "__" + name + "__", None)
        if value:
            info[name] = value

    # Search for author email with <...@...> syntax in the author field
    author = info.get("author", None)
    if author:
        email_pattern = r"<([^>]+@[^>]+)>"
        match = re.search(email_pattern, author)
        if match:
            info["author_email"] = author_email = match.groups()[0]
            info["author"] = author.replace("<" + author_email + ">", "").strip()

    # Get the module synopsis (first non-blank line) from its docstring
    doc = info.get("doc", None)
    if doc:
        lines = doc.splitlines()
        for line in lines:
            if line:
                info["description"] = line.strip()
                break
    del info["doc"]

    return info

sys.path.insert(0, ".")
import docbench
info = get_info(docbench)

extra = dict(
  py_modules       = [info["name"]],
  scripts          = ["scripts/docbench"],
  install_requires = ["path.py"],
)

info.update(extra)


print info

if __name__ == "__main__":
    setuptools.setup(**info)

