.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

.. image::
   https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336
       :target: https://pycqa.github.io/isort/

=========================
visaplan.plone.sqlwrapper
=========================

This package provides a simple generator for SQL statements,
which are then executed by a Zope database adapter.

It does not try to implement an object-relational mapper (ORM) but simply helps
to create SQL statements.

The purpose of this package is *not* to provide new functionality
but to factor out existing functionality from an existing monolitic Zope product.
Thus, it is more likely to lose functionality during further development
(as parts of it will be forked out into their own packages,
or some functionality may even become obsolete because there are better
alternatives in standard Plone components).

There might be some work still necessary to make this product useful for a
broader audience; it is currently in use in our monolithic product resp. it's
successors only.

We consider it more likely the *successor packages* visaplan.tools_ and
visaplan.zope.reldb_ (see below) to be useful for current use.


Features
--------

- Methods:

  - ``insert``
  - ``update``
  - ``delete``
  - ``select``
  - ``query``

- Implements the `Context manager protocol`_


Examples
--------

This add-on can be seen in action at the following sites:

- https://www.unitracc.de
- https://www.unitracc.com


Contribute
----------

- Issue Tracker: https://github.com/visaplan/plone.sqlwrapper/issues
- Source Code: https://github.com/visaplan/plone.sqlwrapper


Support
-------

If you are having issues, please let us know;
please use the `issue tracker`_ mentioned above.


License
-------

The project is licensed under the GPLv2.

See also
--------

- visaplan.tools_ contains an ``sql`` module to generate SQL statements like
  the ones mentioned above, detached from any Zope context

- visaplan.zope.reldb_ contains a copy which follows the SQLAlchemy_
  placeholders convention (``:name``).

.. _`issue tracker`: https://github.com/visaplan/plone.sqlwrapper/issues
.. _SQLAlchemy: https://www.sqlalchemy.org
.. _visaplan.tools: https://pypi.org/project/visaplan.tools
.. _visaplan.zope.reldb: https://pypi.org/project/visaplan.zope.reldb
.. _`Context manager protocol`: https://www.python.org/dev/peps/pep-0343/

.. vim: tw=79 cc=+1 sw=4 sts=4 si et
