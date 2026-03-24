import collections
import inspect


_ARG_SPEC = collections.namedtuple("ArgSpec", "args varargs keywords defaults")


def ensure_getargspec(inspect_module=inspect):
    if hasattr(inspect_module, "getargspec"):
        return

    arg_spec = getattr(inspect_module, "ArgSpec", _ARG_SPEC)
    inspect_module.ArgSpec = arg_spec

    def getargspec(function):
        full = inspect_module.getfullargspec(function)
        return arg_spec(full.args, full.varargs, full.varkw, full.defaults)

    inspect_module.getargspec = getargspec
