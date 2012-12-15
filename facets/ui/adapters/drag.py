"""
Defines an Drag base class that each GUI toolkit backend must provide a concrete
implementation of.

The Drag class adapts a GUI toolkit drag and drop related event to provide a set
of toolkit neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Str, Property, Any

#-------------------------------------------------------------------------------
#  'Drag' class:
#-------------------------------------------------------------------------------

class Drag ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The GUI toolkit specific drag and drop event being adapted:
    event = Any

    # The name of the event (i.e. 'drag_enter', 'drag_leave', 'drag_move',
    # 'drag_drop'):
    name = Str

    # The x position of the drag event (if any):
    x = Property

    # The y position of the drag event (if any):
    y = Property

    # The type of drag operation being requested ('copy', 'move', 'link'):
    request = Property

    # The type of drag operation result ('copy', 'move', 'link', 'ignore'):
    result = Property

    # Does the drag operation have color data?
    has_color = Property

    # Does the drag operation have image data?
    has_image = Property

    # Does the drag operation have text data?
    has_text = Property

    # Does the drag operation have HTML data?
    has_html = Property

    # Does the drag operation have file data?
    has_files = Property

    # Does the drag operation have URL data?
    has_urls = Property

    # Does the drag operation have Python object data?
    has_object = Property

    # The color associated with the drag operation:
    color = Property

    # The image associated with the drag operation:
    image = Property

    # The text associated with the drag operation:
    text = Property

    # The html associated with the drag operation:
    html = Property

    # The list of file names associated with the drag operation:
    files = Property

    # The list of URLs associated with the drag operation:
    urls = Property

    # The Python object associated with the drag operation:
    object = Property

    #-- Method Implementations -------------------------------------------------

    def __init__ ( self, event, **facets ):
        """ Initializes the object by saving the drag and drop event being
            adapted.
        """
        super( Drag, self ).__init__( **facets )

        self.event = event


    def __call__ ( self ):
        """ Returns the drag and drop event being adapted.
        """
        return self.event

    #-- Property Implementations -----------------------------------------------

    def _get_x ( self ):
        raise NotImplementedError

    def _get_y ( self ):
        raise NotImplementedError

    def _get_request ( self ):
        raise NotImplementedError

    def _get_result ( self ):
        raise NotImplementedError

    def _set_result ( self, result ):
        raise NotImplementedError

    def _get_has_color ( self ):
        raise NotImplementedError

    def _get_has_image ( self ):
        raise NotImplementedError

    def _get_has_text ( self ):
        raise NotImplementedError

    def _get_has_html ( self ):
        raise NotImplementedError

    def _get_has_files ( self ):
        raise NotImplementedError

    def _get_has_urls ( self ):
        raise NotImplementedError

    def _get_has_object ( self ):
        raise NotImplementedError

    def _get_color ( self ):
        raise NotImplementedError

    def _get_image ( self ):
        raise NotImplementedError

    def _get_text ( self ):
        raise NotImplementedError

    def _get_html ( self ):
        raise NotImplementedError

    def _get_files ( self ):
        raise NotImplementedError

    def _get_urls ( self ):
        raise NotImplementedError

    def _get_object ( self ):
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------