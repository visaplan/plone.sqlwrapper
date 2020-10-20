.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

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


Features
--------

- Methods:

  - ``insert``
  - ``update``
  - ``delete``
  - ``select``
  - ``query``

- Implements the Context manager protocol (PEP 343)


Examples
--------

This add-on can be seen in action at the following sites:

- https://www.unitracc.de
- https://www.unitracc.com


Documentation
-------------

Full documentation for end users can be found in the "docs" folder.


Installation
------------

Install visaplan.plone.sqlwrapper by adding it to your buildout::

    [buildout]

    ...

    eggs =
        visaplan.plone.sqlwrapper


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/visaplan/visaplan.plone.sqlwrapper/issues
- Source Code: https://github.com/visaplan/visaplan.plone.sqlwrapper


Support
-------

If you are having issues, please let us know;
please use the `issue tracker`_ mentioned above.


License
-------

The project is licensed under the GPLv2.

.. _`issue tracker`: https://github.com/visaplan/PACKAGE/issues

.. vim: tw=79 cc=+1 sw=4 sts=4 si et
