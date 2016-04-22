import sys as _sys


# detect whether qualnames are needed
class QualTest(object):
    pass

PY3K_QUALNAME = False
if hasattr(QualTest, '__qualname__'):
    PY3K_QUALNAME = True
del QualTest


if PY3K_QUALNAME:
    class QualNameMeta(type):
        """
        MetaClass adding qualified names

        This is a placeholder dummy. Your interpreter supports ``__qualname__`` natively.
        """

    def set_qualname_recursive(obj, parent_qualname=None, _seen=None):
        """
        Recursively set an object's qualname
        """
        return False
else:
    class QualNameMeta(type):
        """
        MetaClass adding qualified names

        This is a partial backport of PEP 3155. It does not support
        function local namespaces, i.e. ``foo.<locals>.bar``.

        Due to namespace resolution, regular objects may have ``__qualname__`` set.
        They must be bound to an instance of :py:class:`~qualname.QualNameMeta` and defined
        in the same module.
        """
        def __new__(mcs, name, bases, class_dict):
            new_cls = type.__new__(mcs, name, bases, class_dict)
            set_qualname_recursive(new_cls)
            return new_cls


    def set_qualname_recursive(obj, parent_qualname=None, _seen=None):
        """
        Recursively set an object's qualname

        :param obj: a class or function to update and recurse into
        :param parent_qualname: starting namespace's qualname or ``None`` for module namespace
        :type parent_qualname: str
        :return: whether a qualname has been assigned to ``obj``
        """
        # avoid infinite recursion
        _seen = _seen if _seen is not None else set()
        if id(obj) in _seen:
            return
        _seen.add(id(obj))
        if _try_qualname(obj, parent_qualname):
            for attr in obj.__dict__.values():
                if hasattr(attr, '__module__'):  # qualname only makes sense if there is a module
                    if attr.__module__ != obj.__module__:
                        continue  # not defined in same namespace
                    set_qualname_recursive(attr, obj.__qualname__, _seen=_seen)
        return getattr(obj, '__qualname__', None)


    def _try_qualname(obj, parent_qualname=None):
        """
        Try to set a valid ``__qualname__`` of ``obj``

        :returns: whether a ``__qualname__`` has been newly set
        """
        if getattr(obj, '__qualname__', False) and _qualname_is_finalized(obj):  # obj already has a valid qualname
            return False
        qualname = obj.__name__ if not parent_qualname else (parent_qualname + '.' + obj.__name__)
        if _qualname_is_finalized(obj, obj.__module__, qualname):
            try:
                setattr(obj, '__qualname__', qualname)
            except TypeError:  # cannot patch builtins
                return False
            else:
                return True
        return False


    def _qualname_is_finalized(obj, module=None, qualname=None):
        """Test whether an object's qualname is final, i.e. can be resolved"""
        module = module or getattr(obj, '__module__')
        qualname = qualname or getattr(obj, '__qualname__')
        __import__(module)
        namespace = _sys.modules[module]
        for name in qualname.split('.'):
            try:
                namespace = getattr(namespace, name)
            except AttributeError:
                return False
        return namespace is obj
