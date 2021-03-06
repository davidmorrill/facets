"""
A menu bar manager realizes itself in errr, a menu bar control.
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

MenuBarManager = toolkit_object( 'action.menu_bar_manager:MenuBarManager' )

#-- EOF ------------------------------------------------------------------------