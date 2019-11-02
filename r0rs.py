# r0rs.py
#
# version 0.1

"""\
一个简单的解释器，实现类LISP语言R0。

>>> SxParser.toString(Interp0().evals(SxParser.fromString( '(* 3 4 5)' )))
'60'
>>> SxParser.toString(Interp0().evals(SxParser.fromString( '((lambda (r) (* 3.14 r r)) 10)' )))
'314.0'
>>> ss = '(define (fib n) (cond ((= n 0) 1) (else (* n (fib (- n 1)))) )) (fib 5)'
>>> SxParser.toString(Interp0().evals(SxParser.fromString( ss )))
'120'
"""

# --- Interpreter -----------------------------------------
from functools import reduce
from enum import Enum

T = Enum('T', 'STRING INT FLOAT BOOL BUILTIN LAMBDA KEYWORD SYMBOL')

class ATOM :
    """S表达式(S-expression)是原子、空列表或S表达式的列表。"""
    def pack(value) :
        if type(value) == str :
            return ATOM(T.STRING, value)
        elif type(value) == int :
            return ATOM(T.INT, value)
        elif type(value) == float :
            return ATOM(T.FLOAT, value)
        elif type(value) == bool :
            return ATOM(T.BOOL, value)
    
    def __init__(self, kind, value) :
        self.kind = kind
        self.value = value
    def __repr__(self) :
        return 'ATOM(%s:%s)' % (self.kind.name, str(self))
    def __str__(self) :
        if self.kind == T.STRING :
            return '"' + self.value + '"'
        elif self.kind == T.BOOL :
            return '#t' if self.value else '#f'
        elif self.kind == T.BUILTIN :
            return '<function at %s>' % hex(id(self.value))
        elif self.kind == T.LAMBDA :
            return '<lambda(%s)>' % ', '.join(self.value[0]) # + SxParser.toString(self.value[1])
        else :      # T.INT T.FLOAT T.KEYWORD T.SYMBOL
            return str(self.value)
    def isSYMBOL(self) :
        return self.kind == T.SYMBOL

class RuntimeError(Exception) :
    pass

class Interp0 :
    """每个解释器对象拥有独立的执行环境。"""
    class Env :
        """符号表环境，简单以字典列表实现。"""
        def __init__(self, symtable) :
            self._symtable = symtable
        def __str__(self) :
            str_syms = [ '{ ' + ' | '.join( '%s : %s'%(k,v) for k,v in syms.items() ) + ' }' for syms in self._symtable ]
            return '\n'.join(str_syms)
        def add(self, sym, val) :
            if isinstance(sym, ATOM) and sym.isSYMBOL() :
                self._symtable[-1][sym.value] = val
            else : raise RuntimeError('add no symbol reference', sym, val)
        def dele(self, sym) :
            if isinstance(sym, ATOM) and sym.isSYMBOL() and sym.value in self._symtable[-1] :
                del self._symtable[-1][sym.value]
            else : raise RuntimeError('unknown symbol', sym)
        def lookup(self, sym) :
            if isinstance(sym, ATOM) and sym.isSYMBOL() :
                for syms in reversed(self._symtable) :
                    if sym.value in syms : return syms[sym.value]
            raise RuntimeError('unknown symbol', sym)
        def extend(self, syms) :
            symtable = self._symtable[:]
            symtable.append(syms)
            return Interp0.Env(symtable)
    
    def _call_lambda(atom, expr, env) :
        args = [ Interp0._ev(e, env) for e in expr[1:] ]
        params = atom.value[0]
        lambdy = atom.value[1]
        env0 = atom.value[2]
        env1 = env0.extend(dict(zip(params, args)))
        return Interp0._ev(lambdy, env1)
    def _call_builtin(atom, expr, env) :
        args = [ Interp0._ev(e, env) for e in expr[1:] ]
        return atom.value(args)
    def _call_keyword(atom, expr, env) :
        if atom.value == 'lambda' :     # (lambda (x y ...) (+ x y ...))
            params = [ a.value for a in expr[1] ]
            lambdy = expr[2]
            val = (params, lambdy, env)
            return ATOM(T.LAMBDA, val)
        elif atom.value == 'cond' :     # (cond ((> x y) a) ((< x y) b) ... (#t c))
            for choose in expr[1:] :
                p = Interp0._ev(choose[0], env)
                if p.value :
                    return Interp0._ev(choose[1], env)
            else : return []            # cond all false, return undetermind
        elif atom.value == 'define' :   # (define x a) || (define (f x y ...) (+ x y ...)) | (define) // return nothing?
            if len(expr) == 1 :
                print(env)
            elif len(expr) == 3 :
                if isinstance(expr[1], ATOM) :
                    env.add(expr[1], Interp0._ev(expr[2], env))
                elif isinstance(expr[1], list) :
                    expr_lambda = [ ATOM(T.KEYWORD, 'lambda'), expr[1][1:], expr[2] ]
                    Interp0._ev( [ ATOM(T.KEYWORD, 'define'), expr[1][0], expr_lambda ] , env)
        elif atom.value == 'let' :      # (let ((x a) (y b) ...) (+ x y ...)) // just call an unamed lambda expr
            params,args = zip(expr[1])
            expr_lambda = [ ATOM(T.KEYWORD, 'lambda'), list(params), expr[2] ]
            return Interp0._ev( [expr_lambda] + list(args) , env)
    def _ev(expr, env) :
        """解释器核心代码"""
        #print(repr(expr), env)
        if isinstance(expr, list) :
            if len(expr) > 0 :
                atom = Interp0._ev(expr[0], env)
                if isinstance(atom, ATOM) :
                    if atom.kind == T.LAMBDA :
                        return Interp0._call_lambda(atom, expr, env)
                    elif atom.kind == T.BUILTIN :
                        return Interp0._call_builtin(atom, expr, env)
                    elif atom.kind == T.KEYWORD :
                        return Interp0._call_keyword(atom, expr, env)
                raise RuntimeError('not callable', atom)
            else : return expr  # ()
        elif isinstance(expr, ATOM) :
            if expr.isSYMBOL() :
                return env.lookup(expr)
            else : return expr  # atom

    def builtins(name) :
        """builtin functions"""
        if name == 'add' :
            f = lambda args:ATOM.pack( reduce(lambda x,y:(x+y) , [a.value for a in args[1:]], args[0].value) )
        elif name == 'sub' :
            f = lambda args:ATOM.pack( -args[0].value if len(args)==1 \
                    else reduce(lambda x,y:(x-y) , [a.value for a in args[1:]], args[0].value) )
        elif name == 'mul' :
            f = lambda args:ATOM.pack( reduce(lambda x,y:(x*y) , [a.value for a in args[1:]], args[0].value) )
        elif name == 'div' :
            f = lambda args:ATOM.pack( reduce(lambda x,y:(x//y) , [a.value for a in args[1:]], args[0].value) \
                    if reduce(lambda x,y:(x and y.kind==T.INT), args, True) \
                    else reduce(lambda x,y:(x/y) , [a.value for a in args[1:]], args[0].value) )
        elif name == 'lt' :
            f = lambda args:ATOM.pack( args[0].value < args[1].value )
        elif name == 'gt' :
            f = lambda args:ATOM.pack( args[0].value > args[1].value )
        elif name == 'eq' :
            f = lambda args:ATOM.pack( args[0].value == args[1].value )
        return ATOM(T.BUILTIN, f)

    def __init__(self, syms={}, load='') :
        builtin = {
            '+'     : 'add',
            '-'     : 'sub',
            '*'     : 'mul',
            '/'     : 'div',
            '<'     : 'lt',
            '>'     : 'gt',
            '='     : 'eq',
        }
        symtable = [ syms if syms else dict( (k, Interp0.builtins(v)) for k,v in builtin.items() ) , {} ]
        self.env = Interp0.Env(symtable)
        code = ''' ; preload code
        (define else #t)
        (define (not x) (cond (x #f) (else #t)) )
        (define (and x y) (cond ((not x) #f) ((not y) #f) (else #t)) )
        (define (or  x y) (cond (x #t) (y #t) (else #f)) )
        (define (if p x y) (cond (p x) (else y)) )
        (define (!= x y) (not (= x y)) )
        (define (>= x y) (or (> a b) (= a b)) )
        (define (<= x y) (or (< x y) (= x y)) )
        '''
        self.evals( SxParser.fromString(load if load else code) )
    def eval(self, expr) :
        return Interp0._ev(expr, self.env)
    def evals(self, exprs) :
        for e in exprs : v = self.eval(e)
        return v

# --- Parser ----------------------------------------------------------
import re

class SyntaxError(Exception) :
    pass

class SxParser :
    """S表达式解析器，支持增量式解析。"""
    def fromString(lines) :
        parser = SxParser()
        parser.feed(lines)
        if parser.complete() :
            return parser.exprs
        else :
            raise SyntaxError('unexpect end')
    def toString(expr) :
        if isinstance(expr, list) :
            return '(' + ' '.join( SxParser.toString(e) for e in expr ) + ')'
        elif isinstance(expr, ATOM) :
            return str(expr)
    
    def __init__(self) :
        self.clear()
    def clear(self) :
        self.exprs = []
        self.where = [self.exprs]       # stack
    def complete(self) :
        return len(self.where) == 1
    def feed(self, line) :
        def tokenize(line) :
            token_spec = [
                ('WHITE',       r'[ \t\f\v]+'),
                ('NEWLINE',     r'[\r\n]'),
                ('COMMENT',     r';.*[\r\n]'),
                ('QLP',         '\'\('),
                ('LP',          r'\('),
                ('RP',          r'\)'),
                ('STRING',      r'"([^\r\n]*?)"'),
                ('ATOM',        r'[^ \t\f\v\r\n\(\)]+'),
            ]
            atom_spec = [
                ('INT',         r'[+-]?\d+'),
                ('FLOAT',       r'[+-]?\d+\.\d*'),
                ('BOOL',        r'#[tf]'),
                ('KEYWORD',     r'lambda|cond|define|let'),
            ]
            token_regex = '|'.join( '(?P<%s>%s)' % pair for pair in token_spec )
            token_pattn = re.compile(token_regex)
            atom_regex = '|'.join( '(?P<%s>%s)' % pair for pair in atom_spec )
            atom_pattn = re.compile(atom_regex)
            pos = 0
            while pos < len(line) :
                mo = token_pattn.match(line, pos)
                if mo :
                    kind = mo.lastgroup
                    value = mo.group()
                    pos = mo.end()
                    if kind == 'WHITE' or kind == 'NEWLINE' or kind == 'COMMENT' :
                        continue
                    elif kind == 'STRING' :
                        yield T.STRING, value[1:-1]
                    elif kind == 'ATOM' :
                        am = atom_pattn.fullmatch(value)
                        if am :
                            kind = am.lastgroup
                            if kind == 'INT' :
                                yield T.INT, int(value)
                            elif kind == 'FLOAT' :
                                yield T.FLOAT, float(value)
                            elif kind == 'BOOL' :
                                yield T.BOOL, True if value == '#t' else False
                            elif kind == 'KEYWORD' :
                                yield T.KEYWORD, value
                        else :
                            yield T.SYMBOL, value
                    else :      # QLP LP RP
                        yield kind, value
                else :
                    raise SyntaxError('unknown token', line[pos:])
        for k,v in tokenize(line) :
            if k == 'LP' :
                self.where[-1].append([])
                self.where.append(self.where[-1][-1])
            elif k == 'RP' :
                if len(self.where) > 1 :
                    self.where.pop()
                else :
                    raise SyntaxError('unexpect token', v)
            else :
                self.where[-1].append(ATOM(k,v))

# --- Main ------------------------------------------------------------------
import argparse

def run_progfile() :
    intp = Interp0()
    with open(args.progfile, encoding='utf-8') as f :
        exps = SxParser.fromString(f.read())
    for e in exps :
        v = intp.eval(e)
        if v != None : print(SxParser.toString(v))

def run_interactive() :
    intp = Interp0()
    pser = SxParser()
    print('Welcome to R0 interpretor, LISP alike simple programming language.  version 0.1\n')
    while True :
        pser.clear()
        try : line = input('--> ')
        except EOFError : return    # exit
        try :
            pser.feed(line)
            while not pser.complete() :
                line = input('... ')
                pser.feed(line)
            for e in pser.exprs :
                v = intp.eval(e)
                if v != None : print(SxParser.toString(v))
        except Exception as err :
            print('INTP', repr(err).partition('(')[0], ':', *err.args)

if __name__ == '__main__' :
    parser = argparse.ArgumentParser(description = '简单的解释器，实现类LISP语言R0。')
    parser.add_argument('progfile', nargs='?', help='程序源文件。')
    args = parser.parse_args()
    #print(args)
    #ss = '  (/ ( + 3 5 ) ( * 7 -9 ) flash name ) define \n #t #f #tf #T #F lambda \n (+ "hello"123 123"world" "stri\ng") 3 "the end"'
    #print(*[ repr(e) for e in SxParser.fromString(ss) ], sep='\n')
    #exit()
    if args.progfile :
        run_progfile()
    else :
        run_interactive()
