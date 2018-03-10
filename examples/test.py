#!/usr/bin/env python

# Python Standard Library
import sys


def test_primes():
    """
    >>> from primes import primes
    >>> n = 50
    >>> primes(n)
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
    """

def test_sieve():
    """
    >>> from primes import primes, sieve
    >>> n = 10000
    >>> primes(n) == sieve(n)
    True
    """

if __name__ == "__main__":
    import doctest
    profile = "--profile" in sys.argv
    doctest.testmod()

