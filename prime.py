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

增加is_primeM(n)做Miller Rabin素性测试，MR_test(a,n)用于发现强伪素数（返回值帮助分解因子，算法有待实现）

>>> is_primeM(1111111)
False
>>> MR_test(2, 1111111)
0
"""

def isqrt(n) :
    """计算整数平方根，忽略小数部分，即找到最大整数r满足r^2 <=n and (r+1)^2 >n。
       牛顿迭代法，x <- ( x + n/x )/2，初值估计取1*2^s用公式做一次迭代。
       细致分析:
        1、用到整数除法 n//a = b，整数除法的不对称性，n=a*b+d，取决与d的大小n//a=b不一定n//b=a。
        2、整数除法n=a*b+d，若a>b且a>d，可以证明a^2> n >b^2 。
        3、对全局凹（凸）曲线，每次迭代总是从曲线单侧（背部？）逐步逼近，因而总是收敛。a> [(a+b)//2] >=b (只在a-b == 1时取等号)。
           可以证明，一般总是[(a+b)//2]^2 >n，如果[(a+b)//2]^2或[(a+b-1)//2]^2 <=n，则必有[(a+b+1)//2]^2 >n，按照定义就是平方根r。

    >>> isqrt(0)
    0
    >>> isqrt(1)
    1
    >>> isqrt(8)
    2
    >>> isqrt(64)
    8
    >>> isqrt(1000)
    31
    """
    if n<=0 :
        return 0
    c = n.bit_length()>>1
    r = ((1<<c) + (n>>c))>>1
    while True :
        t = ( r + n//r )>>1
        if t >= r :
            break;
        r = t
    return r

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

    for i in range(6, isqrt(n)+2, 6) :
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
        for i in range(6, isqrt(n)+2, 6) :
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
    elif (n&1)==0 :
        return False
    return powermod(2, n-1, n)==1 and powermod(3, n-1, n)==1 and powermod(5, n-1, n)==1

def ctz(n) :
    """所谓Count Trailing Zeros指令，返回整数n末尾0的个数（最低位1的位置）

    >>> ctz(0)
    0
    >>> ctz(1)
    0
    >>> ctz(40)
    3
    >>> ctz(1024)
    10
    """
    return (n^(n-1)).bit_length() - 1

def MR_test(a, n) :
    """Miller Rabin素性测试，改进的费马素性测试 a^(p-1)==1 (mod p)。
       因(p-1)为偶数，令(p-1)=(2^s)*d，依次计算平方序列x = a^d,a^2d,a^4d...a^((2^s)*d) (mod p)，找到1即可知p通过费马测试。
       基于x^2==1 (mod p)只存在平凡的平方根（x==1、-1），进一步对p筛选：发现1(mod p)非平凡的平方根，则未通过Miller-Rabin测试。
       返回值: 未通过费马测试返回0，a^d==1或-1返回1，发现x^2==-1(mod p)返回x==SQRT(-1)，发现x^2==1(mod p)返回-x==-SQRT(1)。

    >>> MR_test(2, 341)
    -32
    >>> MR_test(3, 341)
    0
    >>> MR_test(5, 341)
    0
    >>> MR_test(2, 1729)
    -1065
    >>> MR_test(3, 1729)
    -664
    >>> MR_test(5, 1729)
    -1065
    >>> MR_test(2, 25326001)
    1
    >>> MR_test(3, 25326001)
    1
    >>> MR_test(5, 25326001)
    1
    >>> MR_test(7, 25326001)
    0
    """
    x = powermod(a, n>>ctz(n-1), n)
    if x==1 or x==n-1 :
        return 1
    for i in range(1, ctz(n-1)) :
        y = x*x%n
        if y==n-1 :
            return x
        elif y==1 :
            return -x
        x = y
    else :
        y = x*x%n
        if y==1 :
            return -x
        else :
            return 0

def is_primeM(n) :
    if n<2 :
        return False
    elif n==2 or n==3 or n==5 :
        return True
    elif (n&1)==0 :
        return False
    return MR_test(2, n)>0 and MR_test(3, n)>0 and MR_test(5, n)>0

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
