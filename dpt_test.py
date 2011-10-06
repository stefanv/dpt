""" File dpt_test.py

Test cases for dpt.py.

"""

from dpt import *
import random
from random import randint, sample
from math import sqrt
    
class example_1D:
    text = "Random sequences"
    @staticmethod
    def test(n,cyclic=False):
        M = 1 << 16 - 1
        value = [randint(0,M) for k in range(n)]
        return GraphFunction(value,[(k,k+1) for k in range(n-1)]+
            cyclic*[(n-1,0)])
    @staticmethod
    def cases(kmax=None):
        kmax = kmax or 6
        for k in range(1,kmax+1): yield 10**k+1

class example_2D:
    text = "Random squares"
    @staticmethod
    def test(m,n=None):
        n = n or m
        M = 1 << 16 - 1
        value = [randint(0,M) for k in range(m*n)]
        return GraphFunction(value,
            [(j*n+k,j*n+k+1) for j in range(m) for k in range(n-1)]+
            [(k+j*n,k+(j+1)*n) for j in range(m-1) for k in range(n)])
    @staticmethod
    def cases(kmax=None):
        kmax = kmax or 9
        for k in range(1,kmax+1): yield 2**k+1

class example_complete:
    text = "Complete graphs with distinct values"
    @staticmethod
    def test(m):
        M = 1 << 16 - 1
        value = range(m) # [randint(0,M) for k in range(m)]
        return GraphFunction(value, 
            [(i,j) for i in range(m) for j in range(i)])
    @staticmethod
    def cases(kmax=None):
        kmax = kmax or 11
        for k in range(1,kmax+1): yield 2**k

class example_random:
    text = "Random sparse graphs with distinct values"
    @staticmethod
    def test(m,n=None):
        n = n or int(m*sqrt(m)/10)
        M = 1 << 16 - 1
        value = range(m)
# First m-1 arcs make a tree.  Remaining n arcs are random.
        return GraphFunction(value, 
            [(k,randint(0,k-1)) for k in range(1,m)]
            + [tuple(sample(xrange(m),2)) for k in range(n)])
    @staticmethod
    def cases(kmax=None):
        kmax = kmax or 12
        for k in range(1,kmax+1): yield 2**k

examples = ['1D','2D','complete','random']
classes = [example_1D,example_2D,example_complete,example_random]

def test(case,kmax):
    from timeit import Timer
    ex=examples[case]
    example=classes[case]
    print "------- %s -------" % example.text
    for k in example.cases(kmax):
        setup = "from dpt import GraphFunction; \
from dpt_test import example_%s; \
d=example_%s.test(%i)"  % (ex,ex,k)
        code = 'd.dpt(); print d.nnodes, d.narcs,d.count,d.border1,d.border'
        t = Timer(setup=setup, stmt=code).timeit(1)
        print "    ", t

if __name__ == '__main__':
    from sys import argv
    print "------ Format of output lines: -------\n\
#nodes #arcs count border1 border2\n    seconds"
    kmax = None       
    if len(argv)>1: kmax = int(argv[1])
    for case in range(4):
        test(case,kmax)         


