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
import os
import sys
from sphinx.ext.autosummary import Autosummary
from sphinx.ext.autosummary import get_documenter
from docutils.parsers.rst import directives
from sphinx.util.inspect import safe_getattr

sys.path.insert(0, os.path.abspath('../../'))


# -- Project information -----------------------------------------------------

project = 'Spendee'
copyright = '2019, Dionyz Lazar'
author = 'Dionyz Lazar'

# The full version, including alpha/beta/rc tags
release = '0.9.9'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx_autodoc_typehints', 'm2r', 'sphinx.ext.autosummary']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']


class AutoAutoSummary(Autosummary):

    option_spec = {
        'methods': directives.unchanged,
    }

    required_arguments = 1

    def get_members(self, obj, typ, include_public=None):
        if not include_public:
            include_public = []
        items = []
        for name in obj.__dict__.keys():
            try:
                documenter = get_documenter(obj=safe_getattr(obj, name), parent=obj, app=self.env.app)
            except AttributeError:
                continue
            if documenter.objtype == typ:
                items.append(name)
        public = [x for x in items if x in include_public or not x.startswith('_')]
        return public, items

    def run(self):
        clazz = str(self.arguments[0])
        try:
            (module_name, class_name) = clazz.rsplit('.', 1)
            m = __import__(module_name, globals(), locals(), [class_name])
            c = getattr(m, class_name)
            if 'methods' in self.options:
                _, methods = self.get_members(c, 'method', ['__init__'])
                self.content = ["~%s.%s" % (clazz, method) for method in methods if not method.startswith('_')]
        finally:
            return super(AutoAutoSummary, self).run()


def setup(app):
    app.add_directive('autoautosummary', AutoAutoSummary)
