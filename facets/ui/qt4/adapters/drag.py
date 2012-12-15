"""
Defines the Qt specific QtDrag class that provides a concrete implementation of
the Drag base class.

The QtDrag class adapts a GUI toolkit drag and drop related event to provide a
set of toolkit neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from cPickle \
    import dumps, load, loads

from cStringIO \
    import StringIO

from PyQt4.QtCore \
    import Qt, QUrl, QMimeData, QString

from facets.core_api \
    import Bool

from facets.ui.adapters.drag \
    import Drag

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from Qt drop actions to a GUI toolkit neutral version:
RequestAction = {
    Qt.CopyAction:   'copy',
    Qt.MoveAction:   'move',
    Qt.LinkAction:   'link',
    Qt.IgnoreAction: 'ignore'
}

# Mapping from GUI toolkit neutral drop actions to the Qt version:
ResultAction = {
    'copy':   Qt.CopyAction,
    'move':   Qt.MoveAction,
    'link':   Qt.LinkAction,
    'ignore': Qt.IgnoreAction
}

#-------------------------------------------------------------------------------
#  'QtDrag' class:
#-------------------------------------------------------------------------------

class QtDrag ( Drag ):

    #-- Public Facet Definitions -----------------------------------------------

    # Was the event completely handled by the event handler?
    handled = Bool( True )

    #-- Property Implementations -----------------------------------------------

    def _get_x ( self ):
        return self.event.pos().x()


    def _get_y ( self ):
        return self.event.pos().y()


    def _get_request ( self ):
        return RequestAction[ self.event.proposedAction() ]


    def _get_result ( self ):
        return RequestAction[ self.event.dropAction() ]

    def _set_result ( self, result ):
        event  = self.event
        action = ResultAction.get( result, Qt.IgnoreAction )
        if action == self.event.proposedAction():
            event.acceptProposedAction()
        elif action != Qt.IgnoreAction:
            event.setDropAction( action )
            event.accept()
        else:
            event.ignore()


    def _get_has_color ( self ):
        return self.event.mimeData().hasColor()


    def _get_has_image ( self ):
        return self.event.mimeData().hasImage()


    def _get_has_text ( self ):
        return self.event.mimeData().hasText()


    def _get_has_html ( self ):
        return self.event.mimeData().hasHtml()


    def _get_has_files ( self ):
        return self.event.mimeData().hasUrls()


    def _get_has_urls ( self ):
        return self.event.mimeData().hasUrls()


    def _get_has_object ( self ):
        return (self.event.mimeData().hasFormat( PyMimeData.MIME_TYPE ) or
                self.has_files)


    def _get_color ( self ):
        return self.event.mimeData().colorData().toPyObject()


    def _get_image ( self ):
        return self.event.mimeData().imageData().toPyObject()


    def _get_text ( self ):
        return str( self.event.mimeData().text() )


    def _get_html ( self ):
        return str( self.event.mimeData().html() )


    def _get_files ( self ):
        urls = self.event.mimeData().urls()

        files = []
        for url in self.event.mimeData().urls():
            file = str( url.toString( QUrl.RemoveScheme ) )
            if file[:3] == '///':
                file = file[3:]

            files.append( file )

        return files


    def _get_urls ( self ):
        urls = self.event.mimeData().urls()

        return [ str( url.toString() ) for url in urls ]


    def _get_object ( self ):
        if self.has_files:
            from facets.lib.io.file import File

            result = [ File( file ) for file in self.files ]
            if len( result ) == 1:
                return result[0]

            return result

        return PyMimeData.coerce( self.event.mimeData() ).instance()

#-------------------------------------------------------------------------------
#  'PyMimeData' class:
#-------------------------------------------------------------------------------

class PyMimeData ( QMimeData ):
    """ A PyMimeData instance wraps a Python instance as MIME data.
    """

    #-- Class Constants --------------------------------------------------------

    # The MIME type for instances.
    MIME_TYPE = QString( 'application/x-facets-qt4-instance' )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, data = None ):
        """ Initialise the instance.
        """
        QMimeData.__init__( self )

        # Keep a local reference to be returned if possible:
        self._local_instance = data

        if data is not None:
            # Pickle both the class and the data. This format (as opposed to
            # using a single sequence) allows the type to be extracted without
            # unpickling the data itself.

            # We may not be able to pickle the data:
            try:
                pdata = dumps( data.__class__ ) + dumps( data )
            except:
                pdata = dumps( None ) + dumps( None )

            self.setData( self.MIME_TYPE, pdata )


    def instance ( self ):
        """ Returns the instance.
        """
        if self._local_instance is not None:
            return self._local_instance

        io = StringIO( str( self.data( self.MIME_TYPE ) ) )

        try:
            # Skip the type:
            load( io )

            # Recreate the instance:
            return load( io )
        except:
            return None


    def instanceType ( self ):
        """ Return the type of the instance.
        """
        if self._local_instance is not None:
            return self._local_instance.__class__

        try:
            return loads( str( self.data( self.MIME_TYPE ) ) )
        except:
            pass

        return None

    #-- Class Methods ----------------------------------------------------------

    @classmethod
    def coerce ( cls, mime_data ):
        """ Coerce a QMimeData instance specified by *mime_data* to a PyMimeData
            instance if possible.
        """
        # See if the data is already of the right type. If it is, then we know
        # we are in the same process:
        if isinstance( mime_data, cls ):
            return mime_data

        # See if the data type is supported:
        if not mime_data.hasFormat( cls.MIME_TYPE ):
            return None

        new_mime_data = cls()
        new_mime_data.setData( cls.MIME_TYPE, mime_data.data( cls.MIME_TYPE ) )

        return new_mime_data

#-- EOF ------------------------------------------------------------------------
