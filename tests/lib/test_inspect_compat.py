import importlib
import inspect
import types
import unittest

from castervoice.lib.inspect_compat import ensure_getargspec


class TestInspectCompat(unittest.TestCase):

    def test_ensure_getargspec_restores_legacy_signature_shape(self):
        fake_inspect = types.SimpleNamespace(getfullargspec=inspect.getfullargspec)

        def sample(alpha, beta=2, *args, **kwargs):
            return alpha, beta, args, kwargs

        ensure_getargspec(fake_inspect)
        argspec = fake_inspect.getargspec(sample)

        self.assertEqual(["alpha", "beta"], argspec.args)
        self.assertEqual("args", argspec.varargs)
        self.assertEqual("kwargs", argspec.keywords)
        self.assertEqual((2,), argspec.defaults)

    def test_contexts_import_under_python_312_style_inspect(self):
        module = importlib.import_module("castervoice.lib.contexts")
        self.assertTrue(hasattr(module, "WINDOWS_CONTEXT"))
