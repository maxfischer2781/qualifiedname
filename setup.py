import os
import re
import sys
import codecs
from setuptools import setup, find_packages

repo_base = os.path.abspath(os.path.dirname(__file__))

# grab meta without import package
sys.path.insert(0, os.path.join(repo_base, 'qualifiedname'))
import meta as qualifiedname_meta

install_requires = []
try:
    import argparse
except ImportError:
    install_requires.append('argparse')

# use readme for long descripion
with codecs.open(os.path.join(repo_base, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()
for directive_re, replacement_re in [(':py:.*:', ''), (':envvar:', '')]:
    long_description = re.sub(directive_re, replacement_re, long_description)

setup(
    name='qualifiedname',

    # meta data
    version=qualifiedname_meta.__version__,

    description='Backport of __qualname__ proposed in PEP 3155',
    long_description=long_description,
    url='https://github.com/maxfischer2781/qualifiedname',

    author='Max Fischer',
    author_email='maxfischer2781@gmail.com',

    license='MIT',
    platforms=['Operating System :: OS Independent'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        # TODO: confirm others
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        # TODO: confirm others
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Interpreters',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='qualname backport pickle name',

    # content
    packages=find_packages(exclude=('qualifiedname_*',)),
    install_requires=install_requires,
    #extras_require={
    #    'example': ['matplotlib'],
    #},
    # unit tests
    test_suite='qualifiedname_test',
)
