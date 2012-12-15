"""
Invokes the Facets developer environment.

We need to make sure the develop tool is imported so that the Python module
names are fully qualified correctly.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.extra.tools.tools \
    import tools

#-- Launch the tool ------------------------------------------------------------

tools()

#-- EOF ------------------------------------------------------------------------