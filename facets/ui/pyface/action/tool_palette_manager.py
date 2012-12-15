"""
A tool bar manager realizes itself in a tool palette control.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.pyface.toolkit \
    import toolkit_object

#-------------------------------------------------------------------------------
#  Defines the GUI toolkit specific implementation:
#-------------------------------------------------------------------------------

ToolPaletteManager = toolkit_object(
    'action.tool_palette_manager:ToolPaletteManager'
)

#-- EOF ------------------------------------------------------------------------