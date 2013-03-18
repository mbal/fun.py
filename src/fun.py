from collections import OrderedDict

class PatternException(Exception):
    def __init__(self, function, args, msg):
        self.function = function
        self.args = args
        self.msg = msg

    def __str__(self):
        return self.msg.format(self.function.__name__, self.args)


class BadMatch(PatternException):
    def __init__(self, function, args):
        super(BadMatch, self).__init__(function, args,
                "No function clause for {} matching {}")

class MultipleClauses(PatternException):
    def __init__(self, function, args):
        super(MultipleClauses, self).__init__(function, args,
                ("Multiple clauses for function `{}' with arguments: {}"))

class Variable(object):
    def __init__(self, name):
        self.name = name
    def __eq__(self, other):
        return self is other
    def __repr__(self):
        return self.name

class Any(object):
    def __eq__(self, other):
        return True

_ = Any()

class PosInt(object):
    def __eq__(self, other):
        return isinstance(other, int) and other > 0


class ArgMatcher(object):
    def __init__(self, types):
        self.bindings = {}
        self.types = types

    def matches(self, other):
        self.bindings = {}
        for (t, o) in zip(self.types, other):
            if isinstance(t, Variable):
                if t in self.bindings:
                    if self.bindings[t] != o:
                        return False
                else:
                    self.bindings[t] = o
            elif not t == o:
                return False
        return True

    def __hash__(self):
        # the hash function needs to be overwritten in order to use
        # `in` to check whether the argument have already been saved
        # in the dictionary
        return hash(self.types)

    def __repr__(self):
        return 'MatchObj<{}>'.format(self.types)


class PatternMatcher(object):
    def __init__(self):
        self.registry = OrderedDict()

    def __call__(self, *args):
        for fnargs in self.registry:
            if fnargs.matches(args):
                return self.registry[fnargs](*args)
        else:
            raise BadMatch(self, args)

    def register(self, fn, arg_type):
        update_wrapper(self, fn, ('__doc__', '__name__', '__module__'))
        am = ArgMatcher(arg_type)
        if am in self.registry:
            raise MultipleClauses(fn, arg_type)
        self.registry[ArgMatcher(arg_type)] = fn


class Register(object):
    """ Provides `functional-style` pattern matching for python. The decorated
    version is slower (3/4x times), so you shouldn't use it in code that needs
    good performances.
    >>> reg = Register()
    >>> @reg(10, PosInt(), Any())
    ... def function(a, b, c):
        ...     return a * b + c
    ...
    >>> function(10, 2, -8)
    12
    >>> function(1, -4, 0)
    BadMatch: No function clause matching (1, -4, 0)
    """

    def __init__(self):
        self.main_register = {}

    def __call__(self, *args):
        def wrap(function):
            name = function.__name__
            pm = self.main_register.setdefault(name, PatternMatcher())
            pm.register(function, args)
            return pm
        return wrap


def update_wrapper(wrapper, wrapped, what):
    """ similar to functools.update_wrapper, but it won't update Nones"""
    for w in what:
        attr = getattr(wrapped, w)
        if attr is not None:
            setattr(wrapper, w, attr)


if __name__ == '__main__':

    register = Register()
    X = Variable('x')

    @register(0)
    def fact(n):
        return 1
    @register(PosInt())
    def fact(n):
        return n * fact(n-1)

    print(fact(9))
    try:
        print(fact(-1))
    except BadMatch as e:
        print(e)

    @register(X, X)
    def function(a, b):
        return a + b
    @register(_, _)
    def function(a, b):
        return a * b

    print(function(2, 2))
    print(function("a", "a"))
    print(function(2, 5))
