#!/usr/bin/env python
# coding: utf-8
"""
Docbench -- benchmarks based on doctests
"""

# Python 2.7 Standard Library
import argparse
import cProfile
import doctest
import json
import gc
import os.path
import time
import sys

# Third-Party Libraries
import path # from "path.py"
import lsprofcalltree

#
# Metadata
# ------------------------------------------------------------------------------
#
__author__ = u"Sébastien Boisgérault <Sebastien.Boisgerault@mines-paristech.fr>"
__license__ = "MIT License"
__url__ = None
__version__ = None

#
# ------------------------------------------------------------------------------
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
            gc.disable()
            start = time.time()
            exec statement in globs
            stop = time.time()
            gc.enable()
            gc.collect()
            times.append(stop - start)
        results.append((test.name, filter(times)))
    return results

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


#
# Command-Line Interface
# ------------------------------------------------------------------------------
#

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run benchmarks")
    parser.add_argument("filename", metavar="FILENAME", help="benchmark container")
    parser.add_argument("-o", "--output", nargs="?", 
                        type=argparse.FileType("w"), default=sys.stdout,
                        help="output file")
    parser.add_argument("-f", "--format", nargs="?", default="text")
    parser.add_argument("-p", "--profile", action="store_true", default=False)
    args = parser.parse_args()
    
    main(**vars(args))
    

