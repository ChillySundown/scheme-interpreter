(define x (list 7 9 3 2))
(define minus (lambda (n) (- 0 n)))
(map minus x)
x
(map (lambda (x) (* x 2 x 2)) (list 10 9 8 7))
(map minus (list))
(map (lambda (x) (* x 2 x 2)) (list))
(map (lambda (x) (* x 2 x 2)) 7)
