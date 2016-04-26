from __future__ import print_function
import sys
import inspect
from qualifiedname import qualinspect
from qualifiedname import qname_recursive

from qualifiedname.meta import PY3K_QUALNAME


QNAME_RECURSIVE = 1
QNAME_AST = 2

QNAME_DEFAULT = QNAME_AST if sys.version_info >= (2, 7) else QNAME_RECURSIVE

if PY3K_QUALNAME:
    class QualNameMeta(type):
        """
        MetaClass adding qualified names

        This is a placeholder dummy. Your interpreter supports ``__qualname__`` natively.
        """
        _qname_trace_skips = set()  # expose same interface
else:
    class QualNameMeta(type):
        """
        MetaClass adding qualified names

        This is a partial backport of PEP 3155. Two different methodologies for
        deriving ``__qualname__`` are support: recursive and AST.

        AST
        ---

        Parses the abstract syntax tree of the module where a class is defined. In
        principle, this is the more robust method. It supports function local
        namespaces, i.e. ``foo.<locals>.Bar``. However, it requires the ast to be
        recoverable, which in practice means the source of a module must be available.

        Recursive
        ---------

        Recursively updates names of nested objects. It is not robust, creating partial
        qualnames when an object is not globally accessible. This is caused by a lack
        of support for function local namespaces, i.e. ``foo.<locals>.Bar`` will just
        be ``Bar``.

        Due to namespace resolution, regular objects may have ``__qualname__`` set.
        They must be bound to an instance of :py:class:`~qualname.QualNameMeta` and
        defined in the same module.
        """
        _qname_trace_skips = set()
        _qname_method = QNAME_DEFAULT

        def __new__(mcs, name, bases, class_dict):
            if '__qualname__' not in class_dict:
                if class_dict.get('_qname_method', mcs._qname_method) == QNAME_RECURSIVE:
                    new_cls = type.__new__(mcs, name, bases, class_dict)
                    qname_recursive.set_qualname_recursive(new_cls)
                elif class_dict.get('_qname_method', mcs._qname_method) == QNAME_AST:
                    classdef_line = mcs._trace_classdef_line()
                    class_dict['__qualname__'] = qualinspect.get_qualname(class_dict['__module__'], classdef_line)
                    mcs._propagate_qualname(class_dict)
                    new_cls = type.__new__(mcs, name, bases, class_dict)
                else:
                    raise ValueError('Unknown qname method enum: %s' % class_dict.get('_qname_method', mcs._qname_method))
            else:
                new_cls = type.__new__(mcs, name, bases, class_dict)
            return new_cls

        @classmethod
        def _trace_classdef_line(mcs):
            # trace calls until we leave constructor
            frame = inspect.currentframe()
            while frame.f_code.co_name in mcs._qname_trace_skips:
                frame = frame.f_back
            return frame.f_lineno

        @classmethod
        def _propagate_qualname(mcs, class_dict, class_qname=None):
            class_qname = class_qname or class_dict['__qualname__']
            class_module = class_dict['__module__']
            for name, value in class_dict.items():
                mcs._safe_set_qualname(name, value, class_module, class_qname)

        @classmethod
        def _safe_set_qualname(mcs, name, value, class_module, class_qname):
            if isinstance(value, (staticmethod, classmethod)):
                try:
                    func = value.__func__
                except AttributeError:  # py2.6: explicitly call default __func__ property
                    func = value.__get__(object()).im_func
                mcs._safe_set_qualname(name, func, class_module, class_qname)
            # don't assume we know better than whoever set it before
            if hasattr(value, '__qualname__'):
                return
            # skip assignments of things defined elsewhere
            if getattr(value, '__name__', False) != name or getattr(value, '__module__', False) != class_module:
                return
            # defined in same module *globally*
            if getattr(sys.modules[class_module], name, None) is value:
                return
            try:
                value.__qualname__ = class_qname + '.' + name
            except TypeError:
                pass


QualNameMeta._qname_trace_skips.add('__new__')
QualNameMeta._qname_trace_skips.add('_trace_classdef_line')
