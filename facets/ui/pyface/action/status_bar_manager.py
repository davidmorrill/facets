"""
A status bar manager realizes itself in a status bar control.
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

StatusBarManager = toolkit_object(
    'action.status_bar_manager:StatusBarManager'
)

#-- EOF ------------------------------------------------------------------------