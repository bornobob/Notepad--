from functools import wraps
from collections import defaultdict


# dictionary to keep track of which functions are extended
extensions = defaultdict(list)

# list to keep track of functions that are extensible
extensible_functions = []


class Extension:
    """
    Simple class to keep some information about an extension.
    """
    def __init__(self, func, extends_func, after):
        self.func = func
        self.extends = extends_func
        self.after = after

    def __repr__(self):
        return self.func.__name__ + " extends " + self.extends + \
               " (applies " + ("after" if self.after else "before") + ")"


class UndefinedFunctionException(Exception):
    pass


def extensible(x):
    """
    Enables a function to be extended by some other function.
    The function will get an attribute (extensible) which will return True.
    The function will also get a function (extendedby) which will return a
    list of all the functions that extend it.
    """
    extensible_functions.append(x.__name__)

    @wraps(x)
    def wrapper(*args, **kwargs):
        if x.__name__ in extensions:
            for f in extensions[x.__name__]:
                if not f.after:
                    f.func(*args, **kwargs)
        result = x(*args, **kwargs)
        if x.__name__ in extensions:
            for f in extensions[x.__name__]:
                if f.after:
                    f.func(*args, **kwargs)
        return result
    wrapper.extensible = True

    def extended_by():
        return extensions[x.__name__]
    wrapper.extendedby = extended_by
    return wrapper


def extends(func_to_extend, after=False):
    """
    Mark a function as an extension of func_to_extend.
    Setting after to True means that the function will be executed
    after the "normal" execution of the function it extends.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        print('AOP: Registering', func.__name__, 'extends', func_to_extend)
        extensions[func_to_extend].append(
            Extension(wrapper, func_to_extend, after))
        return wrapper
    return decorator


def check_errors():
    """
    Checks for all the extended functions if they extend an actual existing
    function. If not, it throws an exception.
    """
    for key, exts in extensions.items():
        if key not in extensible_functions:
            wrapper_extension = extensions[key][0]
            wrapper_name = wrapper_extension.func.__name__
            raise UndefinedFunctionException(
                'Function {} extends undefined function {}'.format(
                    wrapper_name,
                    key
                )
            )
