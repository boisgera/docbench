#!/usr/bin/env python
# coding: utf-8

# Python 2.7 Standard Library
import argparse
import cProfile
import doctest
import gc
import json
import sys
import time

# Third-Party Libraries
try:
    from pathlib import Path
except ImportError:
    from pathlib2 import Path
import lsprofcalltree


# Metadata
# ------------------------------------------------------------------------------
from .__about__ import *


# ------------------------------------------------------------------------------
def doctest_key(test):
    """
    Order of appearance of doctests in source code
    """
    return (test.filename, test.lineno, test.name, id(test))

def get_tests(objects):
    if not isinstance(objects, list):
        objects = [objects]
    tests = []
    for object_ in objects:
         if isinstance(object, doctest.DocTest):
             tests.append(object_)
         else:
             find_tests = doctest.DocTestFinder().find
             _tests = find_tests(object_)
             _tests.sort(key=doctest_key)
             tests.extend(_tests)
    return tests

def benchmark(objects, n=3, select_time=min, disable_gc=True):
    tests = get_tests(objects)
    results = []
    for test in tests:
        filename = "<doctest {0!r}>".format(test.name)
        times = []
        if len(test.examples) == 0:
            continue
        codes = [compile(ex.source, filename, "exec") for ex in test.examples]
        for i in range(n):
            globs = test.globs.copy()
            setup, statement = codes[:-1], codes[-1]
            for code in setup:
                exec(code, globs)
            if disable_gc:
                gc.disable()
            start = time.time()
            exec(statement, globs)
            stop = time.time()
            if disable_gc:
                gc.enable()
            gc.collect()
            times.append(stop - start)
        test_name = test.name
        results.append((test.name, select_time(times)))
    return results

def profile(objects, output_dir=None):
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    tests = get_tests(objects)
    results = []
    for test in tests:
        if len(test.examples) == 0:
            continue
        profile = cProfile.Profile()
        path = output / (test.name + '.kcg')
        output_file = path.open('w', encoding='utf-8')
        codes = [compile(ex.source, test.filename, "exec") for ex in test.examples]
        locs = {}
        globs = test.globs.copy()
        setup, statement = codes[:-1], codes[-1]
        for code in setup:
            exec(code, globs)
        profile.runctx(statement, globs, locs)
        kcg_profile = lsprofcalltree.KCacheGrind(profile)
        kcg_profile.output(output_file)
        output_file.close()


# Table Formatter
# ------------------------------------------------------------------------------
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


# Main Entry Point
# ------------------------------------------------------------------------------
def benchmod(module=None, filename=None, output=sys.stdout, format="text", profile=False):
    if module is None:
        if filename is None:
            module = sys.modules.get("__main__")
        else:
            filename = str(Path(filename).resolve())
            if not filename.endswith(".py"):
                 error = "{0!r} is not a Python file"
                 raise ValueError(error.format(filename))
            sys.insert(0, filename.dirname())
            try:
                module = __import__(filename.namebase)
            except ImportError:
                error = "unable to import {0!r}"
                raise ValueError(error.format(filename))
            finally:
                del sys.path[0]

    results = benchmark(module)

    if profile:
        dir = Path("profiles")
        if dir.exists():
            if not dir.is_dir():
                raise OSError("'profiles' is not a directory")
        else:
            dir.mkdir(parents=True, exist_ok=True)
        import docbench
        docbench.profile(module, output_dir=str(dir))

    if format == "text":
        content = table(results)
    elif format == "json":
        content = json.dumps(results)
    else:
        raise ValueError("unknown format {0!r}".format(format))

    if output is not None:
        output.write(content)
        try:
            output.flush()
        except AttributeError:
            pass

    return results


# Command-Line Arguments Analysis
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark Runner")
    parser.add_argument("filename", metavar="FILENAME", help="benchmark file")
    parser.add_argument("-o", "--output", nargs="?", 
                        type=argparse.FileType("w"), default=sys.stdout,
                        help="output file")
    parser.add_argument("-f", "--format", nargs="?", default="text")
    parser.add_argument("-p", "--profile", action="store_true", default=False)
    args = parser.parse_args()
    
    benchmod(**vars(args))

