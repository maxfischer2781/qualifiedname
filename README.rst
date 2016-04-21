README
======

This module backports the ``__qualname__`` attribute suggested by `PEP 3155`_
to older python versions.

.. _PEP 3155: https://www.python.org/dev/peps/pep-3155/

Why ``__qualname__``?
---------------------

Python 3.3 added the ``__qualname__`` attribute. It is similar to the
``__name__`` attribute, allowing you to look up an object in a module.
Unlike ``__name__``, it also covers nested definitions, allowing you
to lookup non-global objects.

::

  >>> class C:
  ...   class D:
  ...     def g(): pass
  ...
  >>> C.D.g.__name__
  'g'
  >>> C.D.g.__qualname__
  'C.D.g'

Usage
-----

There are two ways to use `qualifiedname`: via the metaclass ``QualNameMeta``
or ``set_qualname_recursive``. The first will more cleanly integrate into
regular programs, while the later can monkey-path existing code!

QualNameMeta
............

Just use ``QualNameMeta`` as the metaclass for your classes. They will
automatically gain the ``__qualname__`` attribute.

::

  # python 2
  >>> from qualifiedname import QualNameMeta
  >>> class C(object):
  ...   __metaclass__ = QualNameMeta
  ...   class D(object):
  ...     __metaclass__ = QualNameMeta
  ...     def g(): pass
  >>> C.D.g.__qualname__
  'C.D.g'

::

  # python 3
  >>> from qualifiedname import QualNameMeta
  >>> class C(metaclass=QualNameMeta):
  ...   class D(metaclass=QualNameMeta):
  ...     def g(): pass
  >>> C.D.g.__qualname__
  'C.D.g'

:note: Due to how ``QualNameMeta`` operates, ``__qualname__`` will be
       created for regular nested classes as well.

set_qualname_recursive
......................

The function ``set_qualname_recursive`` implements most of the actual magic
behind ``QualNameMeta``. You can use it manually to patch existing objects.

::

  # python 2
  >>> from qualifiedname import set_qualname_recursive
  >>> class C(object):
  ...   class D(object):
  ...     def g(): pass
  >>> getattr(C.D.g, '__qualname__', '<no qualname>')
  <no qualname>
  >>> set_qualname_recursive(C)
  >>> C.D.g.__qualname__
  'C.D.g'

SEE ALSO
--------

The `qualname`_ module provides qualified names at runtime and supports the
``<locals>`` definition.

.. _qualname: https://github.com/wbolster/qualname
