"""
Defines the IUIInfo interface which provides a model class with access to the
UIInfo associated a currently open view of the model.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Interface, Instance

#-------------------------------------------------------------------------------
#  'IUIInfo' interface:
#-------------------------------------------------------------------------------

class IUIInfo ( Interface ):
    """ Defines the IUIInfo interface which provides a model class with access
        to the UIInfo associated a currently open view of the model.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The UIInfo object for an open View of the object:
    ui_info = Instance( 'facets.ui.ui_info.UIInfo' )

#-- EOF ------------------------------------------------------------------------
