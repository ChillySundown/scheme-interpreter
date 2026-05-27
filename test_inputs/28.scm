(define x (- (define y (* 2 (define z (+ (define a 3) 1)))) 1))
x
y
z
a
(define (foo x y) ((define - +) (- x y) (- y x)))
(foo 9 3)
(define (bar x y) (((define (inner) (define + -))) (+ x y) (- y x)))
(bar 9 3)
(define (baz x y) (((define (inner) (define - +))) (- x y) (- y x)))
(baz 9 3)
inner
(+ 9 3)
(- 9 3)