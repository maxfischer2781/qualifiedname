from __future__ import print_function
import inspect
import ast
import sys
import collections
import weakref


def qualname(obj):
    """
    Lookup or compute the ``__qualname__`` of ``obj``

    :param obj: class or function to lookup
    :return: ``__qualname__`` of ``obj``
    :rtype: str
    :raises: AttributeError if no ``__qualname__`` can be found
    """
    # only compute qualname if not present already
    try:
        return obj.__qualname__
    except AttributeError as err:
        no_qualname_exception = err
    obj = getattr(obj, '__func__', obj)
    # inspect source to retrace definition
    source, line_no = inspect.findsource(obj)
    try:
        __qualname__ = QNameTracer(''.join(source)).at_line_no(line_no)
    except KeyError as err:
        no_qualname_exception.__context__ = err
        raise no_qualname_exception
    return __qualname__


def get_qualname(module, line_no):
    """
    Return the qualname corresponding to a definition

    Parses the abstract syntax tree to reconstruct the name of scopes.
    A qualname is defined at the beginning of a scope - a ``class`` or
    ``def`` statement.

    :param module: name of the module in which the definition is performed
    :param line_no: line number at which the definition is performed
    :return: qualname at ``line_no`` of ``module``
    :raises: KeyError if ``module`` or ``line_no`` do not point to valid definitions
    """
    module = sys.modules[module]
    source, _ = inspect.findsource(module)
    return QNameTracer(''.join(source)).at_line_no(line_no)


class QNameTracer(ast.NodeVisitor):
    _cache = weakref.WeakValueDictionary()
    _cache_fifo = collections.deque(maxlen=10)  # limit cache to 10 elements
    _init = False

    def __new__(cls, source):
        try:
            return cls._cache[source]
        except KeyError:
            self = ast.NodeVisitor.__new__(cls)
            cls._cache[source] = self
            cls._cache_fifo.append(self)
            return self

    def __init__(self, source):
        if self._init:
            return
        ast.NodeVisitor.__init__(self)
        self._name_stack = []
        self._lno_qualname = {}
        self.visit(ast.parse(source=source))
        self._init = True

    def at_line_no(self, line_no):
        return self._lno_qualname[line_no]

    def _set_qualname(self, ast_line_no, push_qualname=None):
        # ast_line_no starts at 1, inspect line_no starts at 0
        line_no = ast_line_no
        name_stack = self._name_stack + ([push_qualname] if push_qualname is not None else [])
        self._lno_qualname[line_no] = '.'.join(name_stack)

    def visit_FunctionDef(self, node):
        # enter scope
        self._name_stack.append(node.name)
        self._set_qualname(node.lineno)
        # proceed in function local namespace
        self._name_stack.append('<locals>')
        self.generic_visit(node)
        # unwind at exit
        self._name_stack.pop()
        self._name_stack.pop()

    def visit_ClassDef(self, node):
        # enter scope
        self._name_stack.append(node.name)
        self._set_qualname(node.lineno)
        # proceed at same scope
        self.generic_visit(node)
        # unwind at exit
        self._name_stack.pop()

    def visit_Exec(self, node):
        try:
            qnames = self.__class__(node.body.s)
        except SyntaxError:
            return
        for ast_line_no, exec_qualname in qnames._lno_qualname.items():
            self._set_qualname(node.lineno + ast_line_no, push_qualname=exec_qualname)
