import functools

class PreconditionNotMatched(Exception): pass

def pre(cond):
    def wrapper(function):
        # functools.wraps substitutes the name and documentation of the
        # decorated function to the original values
        @functools.wraps(function)
        def inner(*args, **kwargs):
            if cond(*args, **kwargs):
                return function(*args, **kwargs)
            raise PreconditionNotMatched("precondition not matched with test: "
                    + str(args))
        return inner
    return wrapper


@pre(lambda n: n >= 0)
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n-1)

import random

def generate(t):
    if t == int:
        return random.randint(0, 100)
    if t == float:
        return random.random()
    if t == chr:
        return chr(random.randint(0, 255))

def generate_test_set(types, number=100):
    for i in range(number):
        yield tuple(generate(t) for t in types)

def check(pred, types):
    for test_set in generate_test_set(types):
        print(test_set)
        if not pred(*test_set):
            raise Exception("check failed on " + str(test_set))

check(lambda n: factorial(n) >= n, [int])
