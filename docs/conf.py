# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import cryptography.x509

# Without this remapping, autodoc is unable to interlink cryptography docs
cryptography.x509.Certificate.__module__ = "cryptography.x509"

# -- Project information -----------------------------------------------------
from pathlib import Path

project = "MiniSAML"
copyright = "2020, HENNGE K.K."
author = "HENNGE K.K."

# The full version, including alpha/beta/rc tags
release = (
    next(
        line
        for line in (Path(__file__).parent.parent / "pyproject.toml")
        .read_text()
        .splitlines(keepends=False)
        if line.startswith("version")
    )
    .split("=")[1]
    .strip(" '\"")
)


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinxcontrib.mermaid", "sphinx.ext.autodoc", "sphinx.ext.intersphinx"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "cryptography": ("https://cryptography.io/en/latest/", None),
    "lxml": ("https://lxml.de/apidoc/", None),
}


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "furo"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

autodoc_preserve_defaults = True
