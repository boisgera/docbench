# coding: utf-8
"""
About - Metadata for Setuptools

**TODO:** documentation.
"""

# Python 2.7 Standard Library
import importlib
import inspect
import os
import pydoc
import re
import sys

# Third-Party Libraries
from path import path
import setuptools
import sh

# Metadata
metadata = dict(
    __name__        = __name__,
    __appname__     = "about",
    __version__     = "2.0.0",
    __license__     = "MIT License",
    __author__      = u"Sébastien Boisgérault <Sebastien.Boisgerault@gmail.com>",
    __url__         = "https://warehouse.python.org/project/about",
    __doc__         = __doc__,
    __docformat__   = "markdown",
    __classifiers__ = ["Programming Language :: Python :: 2.7",
                       "Topic :: Software Development ::",
                       "License :: OSI Approved :: MIT License"]
  )

globals().update(metadata)


def get_metadata(module):
    """
    Get the metadata content from the module argument.

    This function uses the following variables when they are defined:

        __name__
        __appname__
        __version__
        __license__
        __author__
        __url__
        __doc__
        __docformat__
        __classifiers__

    It returns a `metadata` dictionary that provides keywords arguments
    for the setuptools `setup` function.
    """

    about_data = module.__dict__
    metadata = {}

    # Read the relevant __*__ module attributes.
    names = """
        __name__
        __appname__
        __version__
        __license__
        __author__
        __url__
        __doc__
        __docformat__
        __classifiers__
    """
    for name in names.split():
        value = about_data.get(name)
        if value is not None:
            metadata[name[2:-2]] = value

    # Search for author email with a <...@...> syntax in the author field.
    author = metadata.get("author")
    if author is not None:
        email_pattern = r"<([^>]+@[^>]+)>"
        match = re.search(email_pattern, author)
        if match is not None:
            metadata["author_email"] = email = match.groups()[0]
            metadata["author"] = author.replace("<" + email + ">", "").strip()
        else:
            metadata["author"] = author

    # Get the module summary and description from the docstring.

    # Process the doc format first (markdown is the default format)
    doc = metadata.get("doc")
    if doc is not None:
        docformat = metadata.get("docformat", "markdown").lower()
        if "rest" in docformat or "restructuredtext" in docformat:
            pass
        elif "markdown" in docformat:
            # Try to refresh the ReST documentation in 'doc/doc.rst'
            try:
                pandoc = sh.pandoc
                try:
                    sh.mkdir("doc")
                except sh.ErrorReturnCode:
                    pass
                sh.pandoc("-o", "doc/doc.rst", _in=doc)            
            except sh.CommandNotFound, sh.ErrorReturnCode:
                warning = "warning: cannot generate the ReST documentation."
                print >> sys.stderr, warning
           # Fallback on the old 'doc/doc.rst' file if it exists.
            try:
                doc = path("doc/doc.rst").open().read()
            except IOError, sh.ErrorReturnCode:
                doc = None # there is nothing we can do at this stage.
                warning = "warning: unable to use existing ReST documentation."
                print >> sys.stderr, warning
        else:
             error = "the doc format should be 'markdown' or 'restructuredtext'."
             raise ValueError(error)
        if doc is not None:
            # We assume that pydoc conventions are met: 
            # the first line is the summary, it's followed by a blankline, 
            # and then by the long description. 
            metadata["description"], metadata["long_description"] = pydoc.splitdoc(doc)

    # Process trove classifiers.
    classifiers = metadata.get("classifiers")
    if classifiers and isinstance(classifiers, str):
        classifiers = [c.strip() for c in classifiers.splitlines() if c.strip()]
        metadata["classifiers"] = classifiers

    return metadata

def printer(line, stdin):
    print line,

class About(setuptools.Command):

    description = "Display Project Metadata"

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        metadata = self.distribution.metadata

        attrs = [
            ("name"     , metadata.name       ),
            ("version"  , metadata.version    ),
            ("summary"  , metadata.description),
            ("home page", metadata.url        ),
            ("license"  , metadata.license    ),
        ]

        author = metadata.author
        maintainer = metadata.maintainer
        if author:
            attrs.extend([
                ("author", metadata.author      ),
                ("e-mail", metadata.author_email),
            ])
        if maintainer and maintainer != author:
            attrs.extend([
                ("maintainer", metadata.maintainer      ),
                ("e-mail"    , metadata.maintainer_email),
            ])

        desc = metadata.long_description
        if desc:
           line_count = len(desc)
           attrs.append(("description", "yes ({0} lines)".format(line_count)))
        else:
           attrs.append(("description", None))

        attrs.extend([
            ("classifiers" , metadata.classifiers     ),
            ("platform"    , metadata.platforms       ),
            ("download url", metadata.download_url    ),
        ])

        # I am ditching "keywords" but keeping "classifiers".
        # (no one is declaring or using "keywords" AFAICT)
        attrs.append(("classifiers", metadata.classifiers))

        # Get the mandatory, runtime, declarative dependencies 
        # (managed by setuptools).
        attrs.append(("requires", self.distribution.install_requires))

        print
        for name, value in attrs:
            print "  - " + name + ":",
            if isinstance(value, list):
                print
                for item in value:
                  print "      - " + str(item)
            elif isinstance(value, basestring):
                lines = value.splitlines()
                if len(lines) <= 1:
                    print value
                else:
                    print
                    for line in lines:
                        print "      | " + line
            else:
                print "undefined"
        print


if __name__ == "__main__":
    import about
    local = open("about.py", "w")
    local.write(open(inspect.getsourcefile(about)).read())
    local.close()
    
