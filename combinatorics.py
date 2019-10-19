# combinatorics.py
#
# version 0.1

"""\
简单的组合工具箱，与itertools最大的区别是支持重复元素的排列组合。

>>> list(combinations((1, 1, 1, 2, 2, 3), 3))
[(1, 1, 1), (1, 1, 2), (1, 1, 3), (1, 2, 2), (1, 2, 3), (2, 2, 3)]
>>> list(permutations((1, 1, 1, 2, 2, 3), 2))
[(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3), (3, 1), (3, 2)]
>>> list(partitions(5, 3, 3))
[(3, 2, 0), (3, 1, 1), (2, 2, 1)]
>>> list(allocations('aabc', (2, 2)))
[('aa', 'bc'), ('ab', 'ac'), ('ac', 'ab'), ('bc', 'aa')]
>>> list(groups('aabc', (2, 2)))
[('aa', 'bc'), ('ab', 'ac')]
"""

''' -- incredible list comprehension in python
def alloc(seq, grp) :
    def alloc2(seq, r) :
        return ( ((), seq) for i in range(1) ) if r<=0 \
            else ( (seq[i:i+1]+s1, seq[:i]+s2) for i in range(len(seq)-r+1) for s1, s2 in alloc2(seq[i+1:], r-1) )
    return ( () for i in range(1) ) if len(grp)<=0 \
            else ( (s1, *ss) for s1,s2 in  alloc2(seq, grp[0]) for ss in alloc(s2, grp[1:]) )
'''
import collections
from functools import reduce

class _orderedCounter(collections.Counter, collections.OrderedDict) :
    pass


def partitions(n, m=0, r=0) :
    m = m if m else n
    r = r if r else n
    if m > 1 :
        for i in range(min(n,r), (n-1)//m, -1) :
            for p in partitions(n-i, m-1, i) :
                yield (i, ) + p
    elif m == 1 : yield (n, )


def _alloc2(seq, n, r) :
    if r > 0 :
        if n > r :
            for i in range(len(seq)) :
                cnt = seq[i][1] if seq[i][1] else r
                for k in range( min(cnt, r), 0, -1) :
                    a = ((seq[i][0],k),)
                    b = ((seq[i][0],cnt-k),) if cnt > k else ()
                    for s1,s2 in _alloc2(seq[i+1:], n-cnt, r-k) :
                        yield a+s1, seq[:i]+b+s2
                n -= cnt
        elif n == r : yield seq, ()
    elif r == 0 : yield (), seq


def allocations(seq, grp) :
    def do_alloc(seq, n, grp) :
        if len(grp) > 0 :
            for s1,s2 in _alloc2(seq, n, grp[0]) :
                for ss in do_alloc(s2, n-grp[0], grp[1:]) :
                    yield (s1, *ss)
        else : yield ()
    nn = len(seq)
    ss = tuple( (seq.index(key), cnt) for key,cnt in (_orderedCounter(seq).items()) )
    for result in do_alloc(ss, nn, grp) :
        yield tuple( reduce(lambda x,y:x+y, (seq[ind:ind+1]*cnt for ind,cnt in group), seq[:0]) for group in result )


def groups(seq, grp) :
    def equ_grp(seq, n, m) :
        if m > 1 :
            r = n//m
            if r > 0 :
                cnt = seq[0][1]
                for gen in partitions(cnt, m, r) :
                    pre = tuple( (seq[0][0], g) for g in gen )
                    grp = tuple( r-c for c in gen )
                    for ss in do_grp(seq[1:], n-cnt, grp) :
                        yield tuple( (a,)+s for a,s in zip(pre, ss) )
            elif r == 0 : yield ((), )*m
        elif m == 1 : yield (seq, )
    def do_grp(seq, n, grp) :
        if len(grp) > 0 :
            m = next( (i for i in range(1, len(grp)) if grp[i]!=grp[0]), len(grp) )
            ne = grp[0]*m
            for s1,s2 in _alloc2(seq, n, ne) :
                for se in equ_grp(s1, ne, m) :
                    for ss in do_grp(s2, n-ne, grp[m:]) :
                        yield (*se, *ss)
        else : yield ()
    nn = len(seq)
    ss = tuple( (seq.index(key), cnt) for key,cnt in (_orderedCounter(seq).items()) )
    for result in do_grp(ss, nn, grp) :
        yield tuple( reduce(lambda x,y:x+y, (seq[ind:ind+1]*cnt for ind,cnt in group), seq[:0]) for group in result )


def combinations(seq, r) :
    return ( a for a,b in allocations(seq, (r, len(seq)-r)) )

def permutations(seq, r) :
    return ( reduce(lambda x,y:x+y, g, seq[:0]) for g in allocations(seq, tuple(1 for i in range(r))) )

def fact(n) :
    return n*fact(n-1) if n>0 else 1

if __name__ == '__main__' :
#    breakpoint()
#    print( *list(partitions(20,3,10)), sep='\n')
    q = ('111123478', (2,2,2,3))
    p1 = list(allocations(*q))
    p2 = list(groups(*q))
    print('----- allocations -----')
    print(*p1, sep='\n')
    print('----- groups -----')
    print(*p2, sep='\n')
    print(q, 'alloc = ', len(p1), '\tgroup = ', len(p2))
