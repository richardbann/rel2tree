from setuptools import setup
import os
import io


here = os.path.abspath(os.path.dirname(__file__))
with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = "\n" + f.read()

setup(
    name="rel2tree",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="6.0.0",
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
            # "coverage >= 4.5.2",
            # "sphinx >= 1.8.4",
            # "sphinx_rtd_theme >= 0.4.2",
            # "twine >= 1.12.1",
            # "wheel >= 0.32.3",
        ]
    },
    license="MIT",
    packages=["rel2tree"],
)
