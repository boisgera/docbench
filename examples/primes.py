#!/usr/bin/env python

def primes(n):
    p = []
    for i in range(2, n+1):
        for j in range(2, i):
            if (i % j == 0):
                break
        else:
            p.append(i)
    return p

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


