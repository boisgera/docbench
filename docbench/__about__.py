# coding: utf-8
"""
Benchmark with doctest
"""
__name__    = "docbench"
__author__  = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__license__ = "MIT License"
__url__     = "https://github.com/boisgera/docbench"
__version__ = "1.0.0-alpha.2"
__classifiers__ = """
Intended Audience :: Developers
Operating System :: OS Independent
Programming Language :: Python :: 2.7
License :: OSI Approved :: MIT License
Topic :: Software Development :: Libraries :: Python Modules
Topic :: Software Development :: Testing
Topic :: System :: Benchmark
"""

export = "doc author license url version classifiers".split()
__all__ = ["__" + name + "__" for name in export]
