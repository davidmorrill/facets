"""
The interface for a simple 'About' dialog.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Image, List, Unicode

from i_dialog \
    import IDialog

#-------------------------------------------------------------------------------
#  'IAboutDialog' class:
#-------------------------------------------------------------------------------

class IAboutDialog ( IDialog ):
    """ The interface for a simple 'About' dialog.
    """

    #-- 'IAboutDialog' interface -----------------------------------------------

    # Additional strings to be added to the dialog:
    additions = List( Unicode )

    # The image displayed in the dialog:
    image = Image

    #-- Facet Default Values ---------------------------------------------------

    def _image_default ( self ):
        from facets.ui.ui_facets import image_for

        return image_for( '@facets:pyface.jpg' )

#-------------------------------------------------------------------------------
#  'MAboutDialog' class:
#-------------------------------------------------------------------------------

class MAboutDialog ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IAboutDialog interface.
    """

#-- EOF ------------------------------------------------------------------------