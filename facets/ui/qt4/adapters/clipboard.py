"""
Defines an PyQt4 specific QtClipboard class that provides a concrete
implementation of the Clipboard interface.

The QtClipboard class adapts the PyQt4 clipboard to provide a set of toolkit
neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
    import SIGNAL

from PyQt4.QtGui \
    import QApplication, QPixmap

from facets.core_api \
    import Any, FacetError

from facets.ui.adapters.clipboard \
    import Clipboard

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.ui.qt4.pyface.image_resource \
    import ImageResource

from drag \
    import PyMimeData

#-------------------------------------------------------------------------------
#  'QtClipboard' class:
#-------------------------------------------------------------------------------

class QtClipboard ( Clipboard ):
    """ Defines a PyQt4 specific QtClipboard class that provides a concrete
        implementation of the Clipboard interface.

        The QtClipboard class adapts the PyQt4 clipboard to provide a set of
        toolkit neutral properties and methods.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The reference to the Qt clipboard object:
    clipboard = Any

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        clipboard = self.clipboard = QApplication.clipboard()
        clipboard.connect( clipboard, SIGNAL( 'dataChanged()' ),
                           self._clipboard_set )
        self._last_text = ''

    #-- Concrete Property Implementations --------------------------------------

    def _get_text ( self ):
        return str( self.clipboard.text() )

    def _set_text ( self, text ):
        self.clipboard.setText( text )


    def _get_image ( self ):
        bitmap = self.clipboard.pixmap()
        if bitmap.isNull():
            return None

        return ImageResource( bitmap = bitmap )

    def _set_image ( self, image ):
        if isinstance( image, AnImageResource ):
            image = image.bitmap

        if not isinstance( image, QPixmap ):
            raise FacetError(
                'Expected an ImageResource object or a QPixmap, but received a '
                '%s' % image.__class__.__name__
            )

        self.clipboard.setPixmap( image )


    def _get_object ( self ):
        data = PyMimeData.coerce( self.clipboard.mimeData() )
        if data is None:
            return None

        return data.instance()

    def _set_object ( self, object ):
        self.clipboard.setMimeData( PyMimeData( object ) )

    #-- Event Handlers ---------------------------------------------------------

    def _clipboard_set ( self ):
        """ Handles the contents of the clipboard being changed.
        """
        try:
            text = self.text
            if (text != '') and (text != self._last_text):
                self.facet_property_set( 'text', self._last_text )
                self._last_text = text

            image = self.image
            if (image is not None) and (image is not self._last_image):
                self.facet_property_set( 'image', self._last_image )
                self._last_image = image

            object = self.object
            if (object is not None) and (object is not self._last_object):
                self.facet_property_set( 'object', self._last_object )
                self._last_object = object
        except TypeError:
            # When quitting an application, the clipboard is modified, which
            # can result in a TypeError here due to some of the underlying
            # Facets modules already having been deleted...
            pass

#-- EOF ------------------------------------------------------------------------