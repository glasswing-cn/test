;; r0 language program example
;;    目标是调试通过SICP的所有代码

(define (fib n)
    (cond ((= n 0) 1)
        (else (* n (fib (- n 1))))
    ))

(fib 10)
