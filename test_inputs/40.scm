(define y 9)
(if (<= (+ y y) (* y 2)) (define x (- y 1)) (define x (+ y 1)))
x
y
(define (foo x y) ((define not +) x y))
(foo 9 3)
(define (baz x y) ((define + not) x y))
(baz 9 3)
(+ 9 3)
(if (not #t) 1 0)
(if (not #f) 1 0)