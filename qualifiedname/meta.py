__version__ = "0.1.0"


# detect whether qualnames are needed
class QualTest(object):
    pass

PY3K_QUALNAME = False
if hasattr(QualTest, '__qualname__'):
    PY3K_QUALNAME = True
del QualTest

__all__ = ['__version__', 'PY3K_QUALNAME']
