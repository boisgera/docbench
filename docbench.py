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
import doctest
import os.path
import time
import sys

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
def get_tests(*objects):
    tests = []
    for object_ in objects:
         if isinstance(object, doctest.DocTest):
             tests.append(object_)
         else:
             find_tests = doctest.DocTestFinder().find
             tests.extend(find_tests(object_))
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
                exec code in test.globs
            statement = codes[-1]
            start = time.time()
            exec statement in test.globs
            stop = time.time()
            times.append(stop - start)
        results.append((test.name, filter(times)))
    return results

# OK, profile groks code object too ... with runctx we should be able to do
# what we want to do.

# profile options for kcg (save to file or let the user do it) ? use a tmp
# dir and LAUNCH kcg ? Support pstats stuff ?
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
   """
   doctest_ = doctest.DocTestFinder().find(test)[0] 
   print benchmark(doctest_)



#
# Main Entry Point
# ------------------------------------------------------------------------------
#

def main(filename):
    if not filename.endswith(".py"):
         raise ValueError("{0!r} is not a Python file")
    dirname, filename = os.path.split(filename)
    basename = filename[:-3]
    sys.path.insert(0, dirname)
    module = __import__(basename)
    del sys.path[0]
    print benchmark(module)


if __name__ == "__main__":
    try:
        filename = sys.argv[1]
    except IndexError:
        print "usage: docbench FILENAME"
        sys.exit(1)
    main(filename)

