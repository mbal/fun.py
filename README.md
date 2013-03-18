fun.py
======

Your wet dream is functional programming, isn't it?

`fun.py` provides a simple decorator that tries to bring pattern matching facilities to the python's world.

    import fun
    reg = fun.Register()

    @reg(3, fun.PosInt())
    def function(a, b):
        """ the docstring for the function can be written in whichever 
        clause you prefer."""
        return a + b
    @reg(fun.Any(), fun.Any())
    def function(a, b):
        return a * (b + b)

Under test there's also a library similar to haskell's QuickCheck, although nowhere as complete (well, it isn't comparable even to the other important Python implementations)

    
