import unittest
import sys
from qualifiedname import QualNameMeta, set_qualname_recursive

PY3K = sys.version_info >= (3,)


class QualNameMeta2(QualNameMeta):
    def __new__(cls, *args, **kwargs):
        return QualNameMeta.__new__(cls, *args, **kwargs)


class NoScope(object):
    pass


class Scope1Standalone(object):
    __metaclass__ = QualNameMeta


class Scope1(object):
    __metaclass__ = QualNameMeta

    class Scope2(object):
        __metaclass__ = QualNameMeta

        class Scope3(object):
            __metaclass__ = QualNameMeta2
            Scope1Standalone = Scope1Standalone
            NoScope = NoScope

            @classmethod
            def scope4(cls):
                class ScopeF4(object):
                    __metaclass__ = QualNameMeta
                return ScopeF4

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

set_qualname_recursive(NoScope)
set_qualname_recursive(Scope1Standalone)
set_qualname_recursive(Scope1)

class TestObjectPrimitives(unittest.TestCase):
    def test_unnested(self):
        self.assertEqual('Scope1Standalone', Scope1Standalone.__qualname__)
        self.assertEqual('Scope1', Scope1.__qualname__)
        # don't *require* monkeypatching, but ensure it's correct if attempted
        if hasattr(NoScope, '__qualname__'):
            self.assertEqual('NoScope', NoScope.__qualname__)

    def test_nested_1(self):
        self.assertEqual('Scope1.Scope2', Scope1.Scope2.__qualname__)

    def test_nested_N(self):
        self.assertEqual('Scope1.Scope2.Scope3', Scope1.Scope2.Scope3.__qualname__)

    def test_nested_func_N(self):
        self.assertEqual('Scope1.Scope2.Scope3.scope4', Scope1.Scope2.Scope3.scope4.__qualname__)

    def test_dynamic_1(self):
        self.assertEqual('Scope1.Scope2.Scope3.scope4.<locals>.ScopeF4', Scope1.Scope2.Scope3.scope4().__qualname__)
