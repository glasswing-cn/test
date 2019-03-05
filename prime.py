# Prime.py
#
# version 0.1

"""\
素数相关的一些代码。首先是可靠（慢）的素数判断函数is_prime(n)和分解质因数函数factorize(n)，例如：

>>> is_prime(11111)
False
>>> factorize(12345)
[3, 5, 823]

然后函数is_primeF(n)以费马小定理做素数测试，repunit_prime(s, n)列出是素数的循环整数，例如：
>>> is_primeF(1111111)
False
>>> repunit_prime('1', 10)
{1, 2}
"""

import math

def is_prime(n) :
    """试除法判定素数，从2除至sqrt(n)。

    >>> is_prime(1)
    False
    >>> is_prime(2)
    True
    >>> is_prime(31)
    True
    >>> is_prime(100)
    False
    >>> is_prime(101)
    True
    >>> is_prime(997)
    True
    """
    if n<2 :
        return False
    elif n==2 or n==3 :
        return True
    elif n%2==0 or n%3==0 :
        return False

    for i in range(6, int(math.sqrt(n))+2, 6) :
        if n%(i-1)==0 or n%(i+1)==0 :
            return False
    return True

def factorize(n) :
    """分解质因数，从2开始试除直至不能分解。（会产生非素数的因子吗？）

    >>> factorize(-1)
    []
    >>> factorize(51)
    [3, 17]
    >>> factorize(100)
    [2, 2, 5, 5]
    >>> factorize(256)
    [2, 2, 2, 2, 2, 2, 2, 2]
    >>> factorize(12345)
    [3, 5, 823]
    """
    res = []
    while n>1 :
        if n%2==0 :
            res.append(2)
            n //= 2
            continue
        elif n%3==0 :
            res.append(3)
            n //= 3
            continue
        for i in range(6, int(math.sqrt(n))+2, 6) :
            if n%(i-1)==0 :
                res.append(i-1)
                n //= i-1
                break
            elif n%(i+1)==0 :
                res.append(i+1)
                n //= i+1
                break
        else :
            res.append(n)
            n = 1
    return res

def powermod(a, b, m) :
    """幂模运算a^b%m，使用Montgomery快速算法对大指数求解。

    >>> powermod(1234, 0, 10)
    1
    >>> powermod(3, 4, 100)
    81
    >>> powermod(5, 5, 1000)
    125
    """
    res = 1
    while b>0 :
        if b&1 :
            res = a*res%m
        a, b = a*a%m, b>>1
    return res

def is_primeF(n) :
    """费马小定理进行素性测试，a^(p-1)==1 (mod p)。

    >>> is_prime(1)
    False
    >>> is_primeF(2)
    True
    >>> is_primeF(31)
    True
    >>> is_primeF(100)
    False
    >>> is_primeF(101)
    True
    >>> is_primeF(997)
    True
    >>> is_primeF(11111111111111111)
    False
    >>> is_primeF(1111111111111111111)
    True
    """
    if n<2 :
        return False
    elif n==2 or n==3 or n==5 :
        return True
    elif n<5 :
        return False
    return powermod(2, n-1, n)==1 and powermod(3, n-1, n)==1 and powermod(5, n-1, n)==1

def repunit_prime(s, n) :
    """因为循环节不是1和循环次数非素数的循环整数一定是合数，这个函数寻找循环次数少于n的形如001001...这样的素数。

    >>> repunit_prime('1', 500)
    {1, 2}
    {1, 19}
    {1, 23}
    {1, 317}
    """
    if is_primeF( int(s*2) ) :
        print('{%s, %d}'%(s, 2))
    for i in range(6, n, 6) :
        if is_primeF( int(s*(i-1)) ) :
            print('{%s, %d}'%(s, i-1))
        if is_primeF( int(s*(i+1)) ) :
            print('{%s, %d}'%(s, i+1))


if __name__ == "__main__":
    import doctest
    doctest.testmod()


