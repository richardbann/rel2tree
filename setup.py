from setuptools import setup
import os
import io


here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

VERSION = "6.0.2"

setup(
    name="rel2tree",
    description="Convert a list of records to a JSON-like structure",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version=VERSION,
    url="https://github.com/richardbann/rel2tree",
    author="Richard Bann",
    author_email="richardbann@gmail.com",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
    ],
    extras_require={
        "dev": [
            "black >= 19.3b0",
            "coverage >= 4.5.4",
            "sphinx >= 2.2.0",
            "sphinx_rtd_theme >= 0.4.3",
            "twine >= 1.13.0",
            "wheel >= 0.33.6",
        ]
    },
    license="MIT",
    packages=["rel2tree"],
)
