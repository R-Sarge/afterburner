#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import os

from setuptools import find_packages, setup

# Package meta-data.
NAME = "afterburner"
DESCRIPTION = "Afterburner Python Web Framework built for learning purposes."
EMAIL = ""
AUTHOR = ""
REQUIRES_PYTHON = ">=3.7.0"
VERSION = "0.0.2"

# Which packages are required for this module to be executed?
REQUIRED = [
    "Jinja2==2.10.3",
    "parse==1.13.0",
    "requests==2.22.0",
    "requests-wsgi-adapter==0.4.1",
    "WebOb==1.8.5",
    "whitenoise==5.0.1",
]

# The rest you shouldn't have to touch too much :)

here = os.path.abspath(os.path.dirname(__file__))

# Import the README and use it as the long-description.
# Note: this will only work if 'README.md' is present in your MANIFEST.in file!
try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# Load the package's __version__.py module as a dictionary.
about = {}
if not VERSION:
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION


# Where the magic happens:
setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=["test_*"]),
    install_requires=REQUIRED,
    include_package_data=True,
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3.7",
    ],
    setup_requires=["wheel"],
)