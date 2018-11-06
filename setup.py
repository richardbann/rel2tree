from setuptools import setup
import os
import io


here = os.path.abspath(os.path.dirname(__file__))

with io.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = '\n' + f.read()

VERSION = '5.0.0'

setup(
    name='rel2tree',
    description='Convert relational data to tree-like structure (JSON)',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=VERSION,
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
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
)
