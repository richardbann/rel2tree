#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from rel2tree import __version__

with open('README') as readme_file:
    readme = readme_file.read()


setup(
    name='rel2tree',
    version=__version__,
    description="Convert relational data to tree-like structure (JSON)",
    long_description=readme,
    author="Richard Bann",
    author_email='richardbann@gmail.com',
    url='https://github.com/richardbann/rel2tree',
    packages=['rel2tree'],
    install_requires=[],
    license="MIT license",
    zip_safe=True,
    keywords='data records JSON aggregate',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
