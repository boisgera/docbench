#!/usr/bin/env python

def benchmark_primes():
    """
    >>> from primes import primes
    >>> n = 10000
    >>> primes(n)
    """

def benchmark_sieve():
    """
    >>> from primes import sieve
    >>> n = 10000
    >>> sieve(n)
    """

if __name__ == "__main__":
    import docbench
    docbench.benchmod()

