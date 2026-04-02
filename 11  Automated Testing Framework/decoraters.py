def skip(reason=""):
    def decorator(func):
        func._skip = True
        func._skip_reason = reason
        return func
    return decorator

def parameter(arg_names, arg_values):
    """
    arg_names: string, comma-separated names, e.g. "user,passwd"
    arg_values: list of tuples, e.g. [("user1","pass1"), ("user2","pass2")]
    """
    def decorator(func):
        # store metadata on the function, don't execute yet
        names = [name.strip() for name in arg_names.split(",")]
        func._parametrize = {
            "names": names,
            "values": arg_values
        }
        return func
    return decorator

_fixture_registry = {}  # name -> function

def fixture(scope="function"):
    """
    scope: "function" = new for each test
             "module" = same for all tests in module
           "session" = same for all tests
    """
    def decorator(func):
        _fixture_registry[func.__name__] = {
            "func": func,
            "scope": scope,
            "cached": None,
            "teardown": None   # NEW
        }
        return func
    return decorator