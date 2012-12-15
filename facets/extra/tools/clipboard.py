"""
Defines the clipboard tool that allows copying and pasting text to the system
clipboard.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, Image, Any, View, Item, on_facet_set, toolkit

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'Clipboard' class:
#-------------------------------------------------------------------------------

class Clipboard ( Tool ):
    """ Defines the clipboard tool that allows copying and pasting text to the
        system clipboard.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Clipboard' )

    # Text to be copied to/from the clipboard:
    text = Str( connect = 'both' )

    # Image to be copied to/from the clipboard:
    image = Image( connect = 'both' )

    # Object to be copied to/from the clipboard:
    object = Any( connect = 'both' )

    # The system clipboard object:
    clipboard = Any( toolkit().clipboard() )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        Item( 'text',
              show_label = False,
              style      = 'readonly'
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        # fixme: Why doesn't the @on_facet_set decorator below work?...
        self.clipboard.on_facet_set( self._text_modified,   'text'   )
        self.clipboard.on_facet_set( self._image_modified,  'image'  )
        self.clipboard.on_facet_set( self._object_modified, 'object' )

    #-- Facet Event Handlers ---------------------------------------------------

    def _text_set ( self, text ):
        self._ignore_event  = True
        self.clipboard.text = text
        self._ignore_event  = False


    #@on_facet_set( 'clipboard:text' )
    def _text_modified ( self ):
        if not self._ignore_event:
            self.text = self.clipboard.text


    def _image_set ( self, image ):
        self._ignore_event   = True
        self.clipboard.image = image
        self._ignore_event   = False


    #@on_facet_set( 'clipboard:image' )
    def _image_modified ( self ):
        if not self._ignore_event:
            self.image = self.clipboard.image


    def _object_set ( self, value ):
        self._ignore_event    = True
        self.clipboard.object = value
        self._ignore_event    = False


    #@on_facet_set( 'clipboard:object' )
    def _object_modified ( self ):
        if not self._ignore_event:
            self.object = self.clipboard.object

#-- EOF ------------------------------------------------------------------------