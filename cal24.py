# Cal24.py
#
# version 0.1

"""\
算24点游戏。对任意四个整数，列出所有结果为24的表达式。
"""

from fractions import Fraction
import itertools

def expr_RPN(e) :
    """逆波兰计算器。输入为一个包含操作数和操作符的序列，输出计算结果及对应的中缀表达式字符串。
    
    >>> expr_RPN( (3, 5, '+', 4, '*', 8, '-') )
    (Fraction(24, 1), '(((3+5)*4)-8)')
    >>> expr_RPN( (1, 2, 3, '+', '+', 4, '*') )
    (Fraction(24, 1), '((1+(2+3))*4)')
    """
    st = []
    for i in e :
        if i == '+' :
            b = st.pop()
            a = st.pop()
            st.append( (a[0]+b[0], '('+a[1]+i+b[1]+')') )
        elif i == '-' :
            b = st.pop()
            a = st.pop()
            st.append( (a[0]-b[0], '('+a[1]+i+b[1]+')') )
        elif i == '*' :
            b = st.pop()
            a = st.pop()
            st.append( (a[0]*b[0], '('+a[1]+i+b[1]+')') )
        elif i == '/' :
            b = st.pop()
            a = st.pop()
            st.append( (a[0]/b[0], '('+a[1]+i+b[1]+')') )
        else :
            st.append( (Fraction(i), str(i)) )
    return st.pop()

def cal24(n4) :
    """输入4个整数，列出(generator)满足条件的表达式。
    """
    def RPNs(n4) :
        for a in set( itertools.permutations(n4) ) :
            for x in itertools.product('+-*/', repeat=3) :
                yield (a[0], a[1], x[0], a[2], x[1], a[3], x[2])
                yield (a[0], a[1], x[0], a[2], a[3], x[1], x[2])
                yield (a[0], a[1], a[2], x[0], x[1], a[3], x[2])
                yield (a[0], a[1], a[2], x[0], a[3], x[1], x[2])
                yield (a[0], a[1], a[2], a[3], x[0], x[1], x[2])
                
    for e in RPNs(n4) :
        try :
            n, s = expr_RPN(e)
            if n == 24 :
                yield s
        except Exception :
            pass

def cal_one(n4) :
    for s in cal24(n4) :
        print(s[1:-1])

def cal_all() :
    for n4 in itertools.product(range(1,11), repeat=4) :
        try :
            next( cal24(n4) )
        except StopIteration :
            print(n4[0], n4[1], n4[2], n4[3])

if __name__ == '__main__' :
    import argparse
    parser = argparse.ArgumentParser(description = '计算24点。')
    parser.add_argument('-a', '--all', action='store_true'
                                    , help='找出所有不能计算24的数字组合。')
    parser.add_argument('-n', metavar=('N1', 'N2', 'N3', 'N4'), type=int, nargs=4
                                    , help='从命令行读入整数。')
    args = parser.parse_args()

    if args.all :
        cal_all()
    elif args.n is not None :
        cal_one(args.n)
    else :
        while True :
            try :
                line = input('输入四个整数：')
                print(line)
                cal_one([ int(n) for n in line.split() ])
            except EOFError :
                break
