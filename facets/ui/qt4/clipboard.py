"""
Implements a wrapper around the PyQt clipboard that handles Python objects
using pickle.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtGui \
    import QClipboard, QApplication

from facets.core_api \
    import HasFacets, Instance, Property

from facets.ui.qt4.adapters.drag \
    import PyMimeData

#-------------------------------------------------------------------------------
#  '_Clipboard' class:
#-------------------------------------------------------------------------------

class _Clipboard ( HasFacets ):
    """ The _Clipboard class provides a wrapper around the PyQt clipboard.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The instance on the clipboard (if any):
    instance = Property

    # Set if the clipboard contains an instance:
    has_instance = Property

    # The type of the instance on the clipboard (if any):
    instance_type = Property

    # The application clipboard:
    clipboard = Instance( QClipboard )

    #-- Property Implementations -----------------------------------------------

    def _get_instance ( self ):
        """ The instance getter.
        """
        md = PyMimeData.coerce( self.clipboard.mimeData() )
        if md is None:
            return None

        return md.instance()

    def _set_instance ( self, data ):
        """ The instance setter.
        """
        self.clipboard.setMimeData( PyMimeData( data ) )


    def _get_has_instance ( self ):
        """ The has_instance getter.
        """
        return self.clipboard.mimeData().hasFormat( PyMimeData.MIME_TYPE )


    def _get_instance_type ( self ):
        """ The instance_type getter.
        """
        md = PyMimeData.coerce( self.clipboard.mimeData() )
        if md is None:
            return None

        return md.instanceType()

    #-- Facet Default Values ---------------------------------------------------

    def _clipboard_default ( self ):
        """ Initialise the clipboard.
        """
        return QApplication.clipboard()

#-------------------------------------------------------------------------------
#  The singleton clipboard instance:
#-------------------------------------------------------------------------------

clipboard = _Clipboard()

#-- EOF ------------------------------------------------------------------------