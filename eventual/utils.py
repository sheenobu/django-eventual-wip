import inspect
from importlib import import_module
from funcy import memoize, compose, wraps, any, any_fn, select_values, lmapcat


def import_string(path):
    if "." in path:
        module, attr = path.rsplit(".", 1)
        return getattr(import_module(module), attr)
    else:
        return import_module(path)


class MonkeyProxy(object):
    pass


def monkey_mix(cls, mixin):
    """
    Mixes a mixin into existing class.
    Does not use actual multi-inheritance mixins, just monkey patches methods.
    Mixin methods can call copies of original ones stored in `_no_monkey` proxy:
    class SomeMixin(object):
        def do_smth(self, arg):
            ... do smth else before
            self._no_monkey.do_smth(self, arg)
            ... do smth else after
    """
    assert not hasattr(cls, "_no_monkey"), "Multiple monkey mix not supported"
    cls._no_monkey = MonkeyProxy()

    test = any_fn(inspect.isfunction, inspect.ismethoddescriptor)
    methods = select_values(test, mixin.__dict__)

    for name, method in methods.items():
        if hasattr(cls, name):
            setattr(cls._no_monkey, name, getattr(cls, name))
        setattr(cls, name, method)
