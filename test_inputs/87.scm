(if #t 7 8)
(if #f 7 8)
(if #t 0 1)
(if #t 1 0)
(if #f 0 1)
(if #f 1 0)
((if #t (lambda (x) (* x x)) (lambda (x) (+ x x))) 7)
((if #f (lambda (x) (* x x)) (lambda (x) (+ x x))) 7)
(if #t (define x 9) (define x 10))
(if #f (define y 11) (define y 12))
(if #t (define z 13) (define a 14))
(if #f (define b 15) (define c 16))
x
y
z
a
b
c
(if (if #t #f #t) 9 10)
(if (define b #t) 20 30)
(if b 30 20)
(if (if #t #f #t) (if #t (define d 20) (define e 30)) (if #f (define f 40) (define g 50)))
d
e
f
g
((if #t + -) 1 2)
((if #t 1 0))