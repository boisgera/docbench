# coding: utf-8

metadata = dict(
  __name__    = "docbench",
  __appname__ = "docbench",
  __version__ = "1.0.0-alpha.5",
  __license__ = "MIT License",
  __author__  = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>",
  __url__     = "https://github.com/boisgera/docbench",
  __classifiers__ = """
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python :: 2.7
License :: OSI Approved :: MIT License
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Testing
Topic :: System :: Benchmark
"""
)

globals().update(metadata)
__all__ = metadata.keys()
__all__.remove("__name__")
