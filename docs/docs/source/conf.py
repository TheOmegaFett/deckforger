# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Deckforger'
copyright = '2024, Shane W Miller'
author = 'Shane W Miller'
release = 'Initial'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [ 'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode'
]

templates_path = ['_templates']
exclude_patterns = []

autosummary_generate = True  # If using autosummary
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'no-index': False,  # Turn off indexing conflicts
    'recursive': False, # Prevents scanning recursively
}

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']  # Ensure no hidden duplicates

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']



import os
import sys
sys.path.insert(0, os.path.abspath("../../../"))