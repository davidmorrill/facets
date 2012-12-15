"""
The interface for a dialog that allows the user to open/save files etc.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Any, Bool, Int, Str

from i_dialog \
    import IDialog

#-------------------------------------------------------------------------------
#  'IProgressDialog' class:
#-------------------------------------------------------------------------------

class IProgressDialog ( IDialog ):
    """ A simple progress dialog window which allows itself to be updated
    """

    #-- 'IProgressDialog' interface --------------------------------------------

    title        = Str
    message      = Str
    min          = Int
    max          = Int
    margin       = Int( 5 )
    can_cancel   = Bool( False )
    show_time    = Bool( False )
    show_percent = Bool( False )

    # Label for the 'cancel' button:
    cancel_button_label = Str

    #-- 'IProgressDialog' Interface --------------------------------------------

    def update ( self, value ):
        """ updates the progress bar to the desired value. If the value is >=
            the maximum and the progress bar is not contained in another panel
            the parent window will be closed
        """

#-------------------------------------------------------------------------------
#  'MProgressDialog' class:
#-------------------------------------------------------------------------------

class MProgressDialog ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IProgressDialog interface.

        Implements: update()
    """

    #-- Facet Definitions ------------------------------------------------------

    progress_bar = Any

    #-- 'IProgressDialog' Interface --------------------------------------------

    def update ( self, value ):
        """ updates the progress bar to the desired value. If the value is >=
            the maximum and the progress bar is not contained in another panel
            the parent window will be closed
        """
        if self.progress_bar is not None:
            self.progress_bar.update( value )

        if value >= self.max:
            self.close()

#-- EOF ------------------------------------------------------------------------