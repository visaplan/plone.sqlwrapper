# -*- coding: utf-8 -*- vim: et ts=8 sw=4 sts=4 si tw=79 cc=+1
"""Installer for the visaplan.plone.sqlwrapper package."""
from __future__ import absolute_import
from __future__ import print_function

from setuptools import find_packages
from setuptools import setup
from os.path import isfile

package_name = 'visaplan.plone.sqlwrapper'

# -------------------------------------------- [ get the version ... [
def read_version(fn, sfn):
    main = open(fn).read().strip()
    if sfn is not None and isfile(sfn):
        suffix = valid_suffix(open(sfn).read().strip())
    else:
        suffix = ''
    return main + suffix
    # ... get the version ...
def valid_suffix(suffix):
    """
    Enforce our suffix convention
    """
    suffix = suffix.strip()
    if not suffix:
        return suffix
    allowed = set('.dev0123456789rc')
    disallowed = set(suffix).difference(allowed)
    if disallowed:
        disallowed = ''.join(sorted(disallowed))
        raise ValueError('Version suffix contains disallowed characters'
                         ' (%(disallowed)s)'
                         % locals())
    chunks = suffix.split('.')
    chunk = chunks.pop(0)
    if chunk:
        raise ValueError('Version suffix must start with "."'
                         ' (%(suffix)r)'
                         % locals())
    if not chunks:
        raise ValueError('Version suffix is too short'
                         ' (%(suffix)r)'
                         % locals())
    for chunk in chunks:
        if not chunk:
            raise ValueError('Empty chunk %(chunk)r in '
                             'version suffix %(suffix)r'
                             % locals())
        char = chunk[0]
        if char in '0123456789':
            raise ValueError('Chunk %(chunk)r of version suffix %(suffix)r'
                             ' starts with a digit'
                             % locals())
        char = chunk[-1]
        if char not in '0123456789':
            raise ValueError('Chunk %(chunk)r of version suffix %(suffix)r'
                             ' doesn\'t end with a digit'
                             % locals())
    return suffix  # ... valid_suffix
    # ... get the version ...
    # ... get the version ...
VERSION = read_version('VERSION',
                       'VERSION_SUFFIX')
# -------------------------------------------- ] ... get the version ]


# ------------------------------------------- [ for setup_kwargs ... [
long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])

# see as well --> src/visaplan/PACKAGE/configure.zcml:
exclude_subpackages = (
        )
exclude_packages = []
for subp in exclude_subpackages:
    exclude_packages.extend([package_name + '.' + subp,
                             package_name + '.' + subp + '.*',
                             ])
packages = find_packages(
            'src',
            exclude=exclude_packages)

def github_urls(package, **kwargs):
    pop = kwargs.pop
    pkg_list = package.split('.')
    res = {}
    readthedocs = pop('readthedocs', False)
    if readthedocs:
        if readthedocs in (1, True):
            readthedocs = ''.join(pkg_list)
        res['Documentation'] = \
            'https://%(readthedocs)s.readthedocs.io' % locals()
        assert 'docs' not in kwargs
    else:
        docs = pop('docs', None)
        if docs is None:
            res['Documentation'] = 'https://pypi.org/project/%(package)s' \
                                   % locals()
        elif docs:
            res['Documentation'] = docs
    if not pop('github', 1):
        assert not kwargs
        return res
    pop_user = pop('pop_user', False)
    if pop_user:
        assert 'pick_user' not in kwargs
        assert 'user' not in kwargs
        user = pkg_list.pop(0)
        package = '.'.join(pkg_list)
    else:
        pick_user = pop('pick_user', 'user' not in kwargs)
        if pick_user:
            user = pkg_list[0]
            if 'user' in kwargs:
                assert pop('user') == user
    if pop('travis', False):  # reqires github to be trueish
        res.update({  # CHECKME: is there a de-facto standard key for this?
            'Tests': 'https://travis-ci.org/%(user)s/%(package)s' % locals()
            })
    base = 'https://github.com/%(user)s/%(package)s' % locals()
    res.update({
        'Source': base,
        'Tracker': base + '/issues',
        })
    return res
project_urls = github_urls(package_name,
                           github=1, pop_user=1)
# ------------------------------------------- ] ... for setup_kwargs ]

setup_kwargs = dict(
    name=package_name,
    version=VERSION,
    description="SQL statements generator for Zope SQL adapters",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        'Framework :: Zope2',
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Intended Audience :: Developers",
        "Natural Language :: German",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    # keywords='Python Plone',
    author='Tobias Herp',
    author_email='tobias.herp@visaplan.com',
    project_urls=project_urls,
    license='GPL version 2',
    packages=packages,
    namespace_packages=[
        'visaplan',
        'visaplan.plone',
        ],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'six',  # compatibility with Python 2.7 and 3.3+
        # -*- Extra requirements: -*-
        'visaplan.plone.base',  # adapter base class
        'visaplan.plone.tools',  # logging
        # ... further requirements removed
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
setup(**setup_kwargs)
