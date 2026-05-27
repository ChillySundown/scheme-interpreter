(define a (cons 1 (cons 2 (cons 3 4))))
(cdr (cdr (cdr a)))
(car (cdr (cdr a)))
(car (cdr (cdr (cdr a))))
(define b (cons (cons 1 (cons 2 (cons (cons 3 4) 5))) (cons 0 (cons 1 0))))
(cdr (car b))
(car (car b)); 1
(car (cdr (car b))); 2
(car (car (cdr (cdr (car b))))); 3
(cdr (car (cdr (cdr (car b))))); 4
(cdr (cdr (cdr (car b)))); 5
(car (cdr b)); 0
(car (cdr (cdr b))); 1
(cdr (cdr (cdr b))); 0
(+ car cdr)
(- 7 cdr)
(/ 1 2 -)
(* 1 2 -4.5 car cdr cons)
(define car 1)
(+ car 7)
(car (cons 1 2))
(if (define cdr #t) 1 0)
(cdr (cons 1 2))
