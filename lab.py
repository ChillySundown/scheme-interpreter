"""
6.101 Lab:
LISP Interpreter Part 2
"""

#!/usr/bin/env python3

# import typing  # optional import
# import pprint  # optional import
import doctest
import os
import sys

from scheme_utils import (
    number_or_symbol,
    SchemeEvaluationError,
    SchemeNameError,
    SchemeSyntaxError,  # uncomment in LISP part 2!
    SchemeREPL,
)

sys.setrecursionlimit(20_000)
# NO ADDITIONAL IMPORTS!


class Frame:
    """
    Object representing the current Frame of a function
    or the builtin Frame
    """

    def __init__(self, parent_frame=None):
        self.bindings = {}
        self.parent_frame = parent_frame

    def __getitem__(self, alias):
        if alias in self.bindings:
            return self.bindings[alias]
        else:
            if self.parent_frame is None:
                raise SchemeNameError
            else:
                return self.parent_frame[alias]

    def __setitem__(self, alias, value):
        self.bindings[alias] = value

    def set_setbang(self, alias, value):
        if alias in self.bindings:
            self.bindings[alias] = value
            return value
        else:
            if self.parent_frame is None: 
                raise SchemeNameError
            else:
                return self.parent_frame.set_setbang(alias, value)

    def add_bindings(self, binding_dict):
        for key, val in binding_dict.items():
            self.bindings[key] = val

    def __str__(self):
        return str(self.bindings)


class Function:
    """
    Object representing a user-defined function
    """

    def __init__(self, params, expression, enc_frame):
        self.params = params
        self.expression = expression
        self.enc_frame = enc_frame

    def get_call(self, *args):
        if len(args) != len(self.params):
            print("welcome to hell")
            raise SchemeEvaluationError

        params_to_args = dict(zip(self.params, args))

        op_frame = Frame(parent_frame=self.enc_frame)
        op_frame.add_bindings(params_to_args)
        return self.expression, op_frame

    def __str__(self):
        return str(self.params) + ", " + str(self.expression)


class Pair:
    def __init__(self, car, cdr):
        self.car = car
        self.cdr = cdr

    def get_car(self):
        return self.car

    def get_cdr(self):
        return self.cdr

    def __str__(self):
        return str(self.car) + ", " + str(self.cdr)

    def __repr__(self):
        return "Pair(" + str(self.car) + ", " + str(self.cdr) + ")"


####################################################################
# region                  Tokenization
####################################################################


def tokenize(source):
    """
    Takes source, a string, and returns a list of individual token strings.
    Ignores comments and whitespace.

    >>> tokenize(' + ')
    ['+']
    >>> tokenize('-867.5309')
    ['-867.5309']
    >>> k = "(foo (bar 3.14))"
    >>> tokenize(k)
    ['(', 'foo', '(', 'bar', '3.14', ')', ')']
    """
    # >>> s = "((parse   these \n tokens) ;but ignore comments\n here );)"
    # >>> tokenize(s)
    # ['(', '(', 'parse', 'these', 'tokens', ')', 'here', ')']
    p1 = 0
    p2 = 0

    output = []

    while p2 < len(source):
        # elif source[p2] == '\n':
        #     p2 += 1
        while p2 < len(source) and source[p2] not in " ;()\n":
            p2 += 1
        if p1 < p2:
            output.append(source[p1:p2])
        if p2 < len(source) and source[p2] == ";":
            while p2 < len(source) and source[p2] != "\n":
                p2 += 1
            if p2 == len(source):
                return output
        if p2 < len(source) and source[p2] in "()":
            output += source[p2]

        p2 += 1
        p1 = p2

    return output


# endregion
####################################################################
# region                  Parsing
####################################################################


def parse(tokens):
    """
    Parses a list of token strings and outputs a tree-like representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Hint: Make use of number_or_symbol imported from scheme_utils

    >>> parse(['+'])
    '+'
    >>> parse(['-867.5309'])
    -867.5309
    >>> parse(['(', '(', 'parse', 'these', 'tokens', ')', 'here', ')'])
    [['parse', 'these', 'tokens'], 'here']
    """
    paren_count = 0

    def parse_expression(index):
        nonlocal paren_count
        if tokens[index] == "(":
            paren_count += 1
            current_level = []
            inext = index + 1

            while inext < len(tokens) and tokens[inext] != ")":
                expr, inext = parse_expression(inext)
                current_level.append(expr)
            paren_count -= 1

            if inext >= len(tokens):
                raise SchemeSyntaxError
            if inext < len(tokens) - 1 and paren_count == 0:
                raise SchemeSyntaxError
            elif inext >= len(tokens) - 1 and paren_count != 0:
                raise SchemeSyntaxError

            return current_level, inext + 1
        else:
            if tokens[index] == ")":
                raise SchemeSyntaxError
            return number_or_symbol(tokens[index]), index + 1

    parsed_expr, next_index = parse_expression(0)
    if next_index < len(tokens):
        raise SchemeSyntaxError
    return parsed_expr


# endregion
####################################################################
# region                       Evaluation
####################################################################


def evaluate(tree, frame=None):
    """
    Given tree, a fully parsed expression, evaluates and outputs the result of
    evaluating expression according to the rules of the Scheme language.

    >>> evaluate(6.101)
    6.101
    >>> evaluate(['+', 3, ['-', 3, 1, 1], 2])
    6
    """
    while True:
        if frame is None:
            frame = make_initial_frame()

        if isinstance(tree, (int, float)):
            return tree
        elif isinstance(tree, (str,)):
            return frame[tree]
        else:
            if tree == []:
                return None
            elif tree[0] == "define":
                if isinstance(tree[1], (list,)):
                    frame[tree[1][0]] = Function(tree[1][1:], tree[2], frame)
                    return frame[tree[1][0]]
                else:
                    frame[tree[1]] = evaluate(tree[2], frame)
                    return frame[tree[1]]
            elif tree[0] == "lambda":
                return Function(tree[1], tree[2], frame)
            elif tree[0] == "if":
                if evaluate(tree[1], frame):
                    tree = tree[2]
                else:
                    tree = tree[3]
                continue
            elif tree[0] == "and":
                for arg in tree[1:]:
                    if not evaluate(arg, frame):
                        return False
                return True
            elif tree[0] == "or":
                for arg in tree[1:]:
                    if evaluate(arg, frame):
                        return True
                return False
            elif tree[0] == 'del':
                var = tree[1]
                if not isinstance(var, (str,)): 
                    raise SchemeEvaluationError
                elif var not in frame.bindings:
                    raise SchemeNameError
                else:
                    value = frame[var]
                    del frame.bindings[var]
                    return value
            elif tree[0] == 'let':
                exprs = tree[1]
                body = tree[2]
                child_frame = Frame(parent_frame=frame)
                for expr in exprs:
                    var_name = expr[0]
                    var_val = expr[1]
                    value = evaluate(var_val, frame=frame)
                    child_frame[var_name] = value
                return evaluate(body, frame=child_frame)
            elif tree[0] == 'set!':
                var = tree[1]
                expr = tree[2]

                expr_val = evaluate(expr, frame=frame)
                return frame.set_setbang(var, expr_val)

            try:
                op = evaluate(tree[0], frame)

                args_seq = []
                for child in tree[1:]:
                    args_seq.append(evaluate(child, frame))

                if op in SCHEME_BUILTINS.values():
                    return op(*args_seq)
                elif isinstance(op, Function):
                    tree, frame = op.get_call(*args_seq)
                    continue
                else: 
                    raise SchemeEvaluationError
            except TypeError:
                raise SchemeEvaluationError


# endregion
####################################################################
# region                      Built-ins
####################################################################


def builtin_arithmetic(*args, op):
    if not isinstance(args[0], (int, float)):
        raise SchemeEvaluationError

    if len(args) == 1:
        return args[0]
    else:
        first_num, *rest_num = args
        return op(first_num, builtin_arithmetic(*rest_num, op=op))


def builtin_addition(*args):
    return builtin_arithmetic(*args, op=lambda x, y: x + y)


def builtin_mul(*args):
    """
    Computes the product of two or more evaluated numeric args.
    >>> builtin_mul(1, 2)
    2
    >>> builtin_mul(1, 2, -3)
    -6
    """
    # if len(args) == 2:
    #     return args[0] * args[1]

    # first_num, *rest_nums = args
    # return first_num * builtin_mul(*rest_nums)
    return builtin_arithmetic(*args, op=lambda x, y: x * y)


def builtin_sub(*args):
    """
    Computes the difference of two or more evaluated numeric args
    """
    first_num, *rest_nums = args
    if not isinstance(first_num, (int, float)):
        raise SchemeEvaluationError
    else:
        return first_num - builtin_addition(*rest_nums)


def builtin_div(*args):
    div_start = args[0]
    for div in args[1:]:
        div_start /= div
    return div_start


def compare(args, op=None):
    for current_arg_index in range(1, len(args)):
        prev_arg_index = current_arg_index - 1
        if op(args[prev_arg_index], args[current_arg_index]):
            return False
    return True


def builtin_equal(*args):
    return compare(args, op=lambda a, b: a != b)


def builtin_increasing(*args):
    return compare(args, op=lambda a, b: a >= b)


def builtin_nondecreasing(*args):
    return compare(args, op=lambda a, b: a > b)


def builtin_decreasing(*args):
    return compare(args, op=lambda a, b: a <= b)


def builtin_nonincreasing(*args):
    return compare(args, op=lambda a, b: a < b)


def builtin_not(*args):
    if len(args) != 1:
        raise SchemeEvaluationError
    else:
        return not args[0]


def cons(*args):
    if len(args) != 2:
        raise SchemeEvaluationError
    else:
        return Pair(args[0], args[1])


def get_car(*args):
    if len(args) != 1 or not isinstance(args[0], (Pair,)):
        raise SchemeEvaluationError
    else:
        return args[0].get_car()


def get_cdr(*args):
    if len(args) != 1 or not isinstance(args[0], (Pair,)):
        raise SchemeEvaluationError
    else:
        return args[0].get_cdr()


def builtin_list(*args):
    if len(args) == 0:
        return None
    else:
        first, *rest = args
        return Pair(first, builtin_list(*rest))

def builtin_list_type_check(obj):
    if not isinstance(obj, (Pair,)) and obj is not None:
        return False
    else:
        if obj is None:
            return True
        else:
            return builtin_list_type_check(obj.get_cdr())


def builtin_list_length(obj):
    if obj is not None and not builtin_list_type_check(obj):
        raise SchemeEvaluationError
    else:
        if obj is None:
            return 0
        else:
            return 1 + builtin_list_length(obj.get_cdr())


def builtin_list_ref(cons, index):
    if not isinstance(cons, (Pair,)):
        raise SchemeEvaluationError

    if index == 0:
        return cons.get_car()
    else:
        return builtin_list_ref(cons.get_cdr(), index - 1)


def builtin_append(*lists):
    if not lists:
        return None
    elif lists[0] is not None and not isinstance(lists[0], (Pair,)):
        raise SchemeEvaluationError

    first, *rest = lists
    if first is None and not rest:
        return None
    elif first is None:
        return builtin_append(*rest)
    else:
        return Pair(
            first.get_car(),
            builtin_append(
                *[
                    first.get_cdr(),
                ]
                + rest
            ),
        )


def builtin_begin(*args):
    if not args:
        raise SchemeEvaluationError
    return args[-1]


def evaluate_file(file_name, frame=None):
    with open(file_name, encoding="utf-8") as f:
        valid_expr = parse(tokenize(f.read()))
        return evaluate(valid_expr, frame)


def builtin_map(function, link):
    if link is None:
        return link
    else:
        if link.get_cdr() is None:
            return Pair(function(link.get_car()), None)
        else:
            return Pair(function(link.get_car()), builtin_map(function, link.get_cdr()))
        
def builtin_filter(function, link):
    if link is None:
        return link
    else:
        if function(link.get_car()):
            return Pair(link.get_car(), builtin_filter(function, link.get_cdr()))
        else:
            return builtin_filter(function, link.get_cdr())
        
def builtin_reduce(function, link, val):
    def reduce_helper(function, link, current_val):
        if link is None:
            return current_val
        else:
            return builtin_reduce(function, link.get_cdr(), function(current_val, link.get_car()))



SCHEME_BUILTINS = {
    "+": lambda *args: sum(args),
    "*": builtin_mul,
    "-": builtin_sub,
    "/": builtin_div,
    "#t": True,
    "#f": False,
    "equal?": builtin_equal,
    ">": builtin_decreasing,
    "<": builtin_increasing,
    ">=": builtin_nonincreasing,
    "<=": builtin_nondecreasing,
    "not": builtin_not,
    "cons": cons,
    "car": get_car,
    "cdr": get_cdr,
    "list": builtin_list,
    "list?": builtin_list_type_check,
    "length": builtin_list_length,
    "list-ref": builtin_list_ref,
    "append": builtin_append,
    "begin": builtin_begin,
}


def make_initial_frame():
    builtin_frame = Frame()
    builtin_frame.add_bindings(SCHEME_BUILTINS)
    return Frame(parent_frame=builtin_frame)


# endregion
####################################################################
# region                       REPL
####################################################################

if __name__ == "__main__":
    run_doctest = True
    run_repl = True

    if run_doctest:
        _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
        doctest.run_docstring_examples(tokenize, globals(), optionflags=_doctest_flags)
        # doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    if run_repl:
        sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
        argv = sys.argv
        init_frame = make_initial_frame()
        for file_name in argv[1:]:
            evaluate_file(file_name, init_frame)

        SchemeREPL(sys.modules[__name__], verbose=True, repl_frame=init_frame).cmdloop()

# endregion
