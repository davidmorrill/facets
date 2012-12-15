"""
Abstract base class for all window actions.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.pyface.window \
    import Window

from facets.core_api \
    import Instance

from action \
    import Action

#-------------------------------------------------------------------------------
#  'WindowAction' class:
#-------------------------------------------------------------------------------

class WindowAction ( Action ):
    """ Abstract base class for all window actions.
    """

    #-- 'WindowAction' interface -----------------------------------------------

    # The window that the action is in.
    window = Instance( Window )

#-- EOF ------------------------------------------------------------------------