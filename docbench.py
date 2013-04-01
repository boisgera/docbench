#!/usr/bin/env python
# coding: utf-8
"""
Docbench -- Benchmarking with Doctest
"""

"""
(benchmarks are no good when the tests don't pass ... and DRY !)
The typical way to use this module would be to have the usal doctest base
(internal or external, as you wish) that covers a lot but for which every
test is fast ... AND then another "object" (file, function , etc. probably
external) of long-running tests that are meant too be benchmark but can
be tested too and use to generate profiles.
"""

# Python 2.7 Standard Library
import argparse
import cProfile
import doctest
import json
import os.path
import time
import sys

# Third-Party Libraries
import path # forked-path
import lsprofcalltree

#
# Misc. Notes
# ==============================================================================
#
#   - produce a benchmark table that may be used to compare performance between
#     several versions ? (see benchrun on Google Code).
#
#   - the idea is to investigate doctest and use them for the three purposes.
#     For every test, there is potentialy a setup. For a doctest, if there are
#     multiple statements, all but the last one would be considered setup.
#
#   - The timeit module is short, pure Python code with a ugly interface. 
#     Don't rely on it. See how DoctTestRunner __run method is implemented
#     and instrument that.
#
#   - Is "bench the last statement only" the good idea ?
#

#
# Metadata
# ------------------------------------------------------------------------------
#
__author__ = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__license__ = "MIT License"
__url__ = None
__version__ = None

#
# Misc. Notes
# ------------------------------------------------------------------------------
#
#
# TODO: support object (function, module, etc.) additionally to test.
#       Support lists of stuff ? Rather multiple positional arguments ?
#       What about the fact that we want all objects to be named ? Support
#       keyword arguments for them ? Could be nice but will be unsorted
#       then ... In a first approach, we may assume that everything is
#       properly named.
#
# TODO: extract short description from the test if any ? (if it does not
#       start with ">>>" ...)
#
# TODO: introduce timeit number and repeat ? (and post-process after repeat ?)
#       consider disabling gc ?
#
# TODO: implement a "-m" mode like doctest.
#
# TODO: for sequence of benchs in a module, can we ensure that source order is 
#       preserved ?
# 

def _source_order(self, other):
    """
    Source order for doctests
    """
    if not isinstance(other, doctest.DocTest):
        return -1
    return cmp((self.filename, self.lineno, self.name, id(self)),
               (other.filename, other.lineno, other.name, id(other)))

def get_tests(*objects):
    tests = []
    for object_ in objects:
         if isinstance(object, doctest.DocTest):
             tests.append(object_)
         else:
             find_tests = doctest.DocTestFinder().find
             _tests = find_tests(object_)
             _tests.sort(cmp=_source_order)
             tests.extend(_tests)
    return tests

def benchmark(*objects, **options):
    n = options.get("n", 3)
    filter = options.get("filter", min)

    tests = get_tests(*objects)
    results = []
    for test in tests:
        filename = "<doctest {0!r}>".format(test.name)
        times = []
        if len(test.examples) == 0:
            continue
        codes = [compile(ex.source, filename, "exec") for ex in test.examples]
        for i in range(n):
            globs = test.globs.copy()
            for code in codes[:-1]: # setup 
                exec code in globs
            statement = codes[-1]
            start = time.time()
            exec statement in globs
            stop = time.time()
            times.append(stop - start)
        results.append((test.name, filter(times)))
    return results

# OK, profile groks code object too ... with runctx we should be able to do
# what we want to do.

# profile options for kcg (save to file or let the user do it) ? use a tmp
# dir and LAUNCH kcg ? Support pstats stuff ?

def profile(output, *objects):
    tests = get_tests(*objects)
    results = []
    for test in tests:
        if len(test.examples) == 0:
            continue
        #filename = "<doctest {0!r}>".format(test.name)
        profile = cProfile.Profile()
        output_file = open(output / (test.name + ".kcg"), "w")
        codes = [compile(ex.source, test.filename, "exec") for ex in test.examples]
        locs = {}
        globs = test.globs.copy()
        for code in codes[:-1]: # setup 
            exec code in globs
        statement = codes[-1]
        profile.runctx(statement, globs, locs)
        kcg_profile = lsprofcalltree.KCacheGrind(profile)
        kcg_profile.output(output_file)
        output_file.close()

"""
def profile(command, output=None):
    output = "bitstream.kcg"
    output_file = open(output, "w")   
    profile = cProfile.Profile()
    profile.run(command)
    kcg_profile = lsprofcalltree.KCacheGrind(profile)
    kcg_profile.output(output_file)
    output_file.close()   
"""


#
# DocTests 
# ------------------------------------------------------------------------------
#

def meh():
    """
    >>> z = 7
    """

class C(object):
    """
    >>> c = 1
    """
    def __init__(self):
        """
        >>> z = 8
        """
        pass

def test():
   """
   >>> a = 1
   >>> a
   1
   >>> a + 1
   2
   >>> 2 * a
   2
   >>> while a < 10000000:
   ...     a += 1
   >>> fib()
   42
   """
   pass

def fib():
    a, b = 1, 1
    while a < 100000000000:
        a, b = b, a + b
    return 42
    

#
# Table Formatter
# ------------------------------------------------------------------------------
#

def table(cells):
    left_width = max(len(str(x)) for x, _ in cells)
    left_width = max(left_width, len("  Benchmark"))
    right_width = max(len(str(x)) for _, x in cells)
    right_width = max(right_width, len("Time  "))
    template = "{0:<" + str(left_width) + "}  {1:<" + str(right_width) + "}\n"
    text = template.format("Benchmark", "Time")
    text += template.format(left_width*"-", right_width*"-")
    for name, info in cells:
        text += template.format(name, "{0:.3g}".format(info))
    return text

#
# Main Entry Point
# ------------------------------------------------------------------------------
#

def main(**kwargs):
    filename = kwargs["filename"]
    output = kwargs["output"]
    format = kwargs["format"]
    do_profile = kwargs["profile"]

    if not filename.endswith(".py"):
         raise ValueError("{0!r} is not a Python file".format(filename))
    dirname, filename = os.path.split(filename)
    basename = filename[:-3]
    sys.path.insert(0, dirname)
    module = __import__(basename)
    del sys.path[0]
    results = benchmark(module)

    if do_profile:
        dir = path.path("profiles")
        if dir.exists():
            if not dir.isdir():
                raise OSError("'profiles' is not a directory")
            # TODO: check permissions ?
        else:
            dir.mkdir()
        profile(dir, module)
        
    if format == "text":
        content = table(results)
    elif format == "json":
        content = json.dumps(results)
    else:
        raise ValueError("unknown format {0!r}".format(format))
    output.write(content)
    try:
        output.flush()
    except AttributeError:
        pass

def testargs(**kwargs):
    print kwargs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run benchmarks")
    parser.add_argument("filename", metavar="FILENAME", help="benchmark container")
    parser.add_argument("-o", "--output", nargs="?", type=argparse.FileType('w'), default=sys.stdout,
                        help="output file")
    parser.add_argument("-f", "--format", nargs="?", default="text")
    parser.add_argument("-p", "--profile", action="store_true", default=False)
    args = parser.parse_args()
    
    main(**vars(args))
    

