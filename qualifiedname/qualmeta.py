from qualifiedname.meta import PY3K_QUALNAME
from qualifiedname.qname_recursive import set_qualname_recursive

if PY3K_QUALNAME:
    class QualNameMeta(type):
        """
        MetaClass adding qualified names

        This is a placeholder dummy. Your interpreter supports ``__qualname__`` natively.
        """
        pass
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
