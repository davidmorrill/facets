"""
Defines the toolkit specific implementation of a SplashScreen.  See the
ISplashScreen interface for the API documentation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

from logging \
    import DEBUG

from PyQt4 \
    import QtCore, QtGui

from facets.core_api \
    import Any, Bool, implements, Instance, Int

from facets.core_api \
    import Tuple, Unicode

from facets.ui.pyface.i_splash_screen \
    import ISplashScreen, MSplashScreen

from facets.ui.pyface.image_resource \
    import ImageResource

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from window \
    import Window

#-------------------------------------------------------------------------------
#  'SplashScreen' class:
#-------------------------------------------------------------------------------

class SplashScreen ( MSplashScreen, Window ):
    """ The toolkit specific implementation of a SplashScreen.  See the
        ISplashScreen interface for the API documentation.
    """

    implements( ISplashScreen )

    #-- Facet Definitions ------------------------------------------------------

    image             = Instance( AnImageResource, ImageResource( 'splash' ) )
    log_level         = Int( DEBUG )
    show_log_messages = Bool( True )
    text              = Unicode
    text_color        = Any
    text_font         = Any
    text_location     = Tuple( 5, 5 )

    #-- Protected 'IWidget' Interface ------------------------------------------

    def _create_control ( self, parent ):
        """ Creates and returns the splash screen control.
        """
        splash_screen = QtGui.QSplashScreen( self.image.create_image() )
        self._qt4_show_message( splash_screen )

        return splash_screen

    #-- Facet Event Handlers ---------------------------------------------------

    def _text_set ( self ):
        """ Handles the 'text' facet being changed.
        """
        if self.control is not None:
            self._qt4_show_message( self.control )

    #-- Private Interface ------------------------------------------------------

    def _qt4_show_message ( self, control ):
        """ Sets the message text for a splash screen control.
        """
        if self.text_font is not None:
            control.setFont( self.text_font )

        if self.text_color is None:
            text_color = QtCore.Qt.black
        else:
            # Until we get the type of this facet finalised (ie. when FacetsUI
            # supports PyQt) convert it explcitly to a colour.
            text_color = QtGui.QColor( self.text_color )

        control.showMessage( self.text, QtCore.Qt.AlignLeft, text_color )

#-- EOF ------------------------------------------------------------------------