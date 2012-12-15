"""
Invokes the Facets developer environment for use with the Facets UI demo.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.extra.tools.tools \
    import tools, Toolbox

#-- Launch the tool ------------------------------------------------------------

tools(
    application = 'Facets UI Demo',
    toolbox     = Toolbox( file_name = 'tool.box' )
)

#-- EOF ------------------------------------------------------------------------
