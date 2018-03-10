[![Build status](https://travis-ci.org/boisgera/docbench.svg?branch=master)](https://travis-ci.org/boisgera/docbench)

Docbench: Doctests Benchmarking
================================================================================

Docbench is a framework based on [doctest][] to benchmark Python code.
If you already are familiar with doctest, 
you should be able to use docbench in minutes. 

[doctest]: http://docs.python.org/2/library/doctest.html

--------------------------------------------------------------------------------

We will walk you through the use of docbench with a simple use case: 
a module that computes prime numbers.

Create a `primes.py` file and define the `primes` function:

    def primes(n):
        p = []
        for i in range(2, n+1):
            for j in range(2, i):
                if (i % j == 0):
                    break
            else:
                p.append(i)
        return p

The function returns an ordered list of primes numbers up to the number `n`.
Its implementation is simple but the execution takes a lot of time when `n` grows.
The following `sieve` function should return the same result, but performs less
computations and therefore should be faster.

    def sieve(n):
        p = []
        for i in range(2, n+1):
            prime = True
            for j in p:
                if j * j > i:
                    break
                if (i % j == 0):
                    prime = False
                    break
            if prime:
                p.append(i)
        return p


Does it Work?
--------------------------------------------------------------------------------

**If you already know doctest, you may skip this section.**

Testing this module with doctest is pretty straightforward: create a `test.py`
file with a function `test_primes` with no implementation but a doctest 
for the `primes` function:

    def test_primes():
        """
        >>> from primes import primes
        >>> n = 50
        >>> primes(n)
        [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
        """

You are pretty confident that if `test_primes` doctest works as advertised
in this doctest, the `primes` function behaves correctly. 
Therefore, you may now test `sieve` against `primes`:

    def test_sieve():
        """
        >>> from primes import primes, sieve
        >>> n = 10000
        >>> primes(n) == sieve(n)
        True
        """

Finally, add the following boilerplate a the end of your file:

    if __name__ == "__main__":
        import doctest
        doctest.testmod()

You are ready to execute this test suite with:

    $ python test.py

No error displayed ? The `primes` module has successfully passed all tests !


Is is Fast?
--------------------------------------------------------------------------------

Create a new file name `benchmark.py`. Add functions that act as docbench 
holders for the function `primes` and `sieve`. We rely on the convention 
that only the time spent in the last statement of any docbench will be 
measured, the previous ones are considered setup code.

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

Add the following boilerplate at the end of your file:

    if __name__ == "__main__":
        import docbench
        docbench.benchmod()

Run your benchmark with:
    
    $ python benchmark.py

You should end up with an output similar too:

    Benchmark                  Time            
    -------------------------  ----------------
    __main__.benchmark_primes  1.03            
    __main__.benchmark_sieve   0.00876

Indeed, `sieve` is quite faster than `primes` !

