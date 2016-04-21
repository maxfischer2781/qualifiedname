import unittest
import sys
from qualifiedname import QualNameMeta

PY3K = sys.version_info >= (3,)


class NoScope(object):
    pass


class Scope1Standalone(object):
    __metaclass__ = QualNameMeta


class Scope1(object):
    __metaclass__ = QualNameMeta

    class Scope2(object):
        __metaclass__ = QualNameMeta

        class Scope3(object):
            __metaclass__ = QualNameMeta
            Scope1Standalone = Scope1Standalone
            NoScope = NoScope

            def scope4(self):
                pass

if PY3K:  # PY3K requires different metaclass syntax
    exec("""
class NoScope:
    pass
class Scope1Standalone(metaclass=QualNameMeta):
    pass
class Scope1(metaclass=QualNameMeta):
    class Scope2(metaclass=QualNameMeta):
        class Scope3(metaclass=QualNameMeta):
            Scope1Standalone = Scope1Standalone
            NoScope = NoScope
            def scope4(self):
                pass
""")


class TestObjectPrimitives(unittest.TestCase):
    def test_unnested(self):
        self.assertEqual(Scope1Standalone.__qualname__, 'Scope1Standalone')
        self.assertEqual(Scope1.__qualname__, 'Scope1')
        # don't *require* monkeypatching, but ensure it's correct if present
        if hasattr(NoScope, '__qualname__'):
            self.assertEqual(NoScope.__qualname__, 'NoScope')

    def test_nested_1(self):
        self.assertEqual(Scope1.Scope2.__qualname__, 'Scope1.Scope2')

    def test_nested_N(self):
        self.assertEqual(Scope1.Scope2.Scope3.__qualname__, 'Scope1.Scope2.Scope3')

    def test_nested_func_N(self):
        self.assertEqual(Scope1.Scope2.Scope3.scope4.__qualname__, 'Scope1.Scope2.Scope3.scope4')
