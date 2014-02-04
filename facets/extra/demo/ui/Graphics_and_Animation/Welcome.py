"""
# Welcome #
"""

#-- Imports --------------------------------------------------------------------

from random \
    import randint, choice, shuffle

from facets.api \
    import HasFacets, Str, Int, Any, Tuple, Bool, List, Theme, Color, View, \
           UItem, on_facet_set

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

from facets.animation.api \
    import Clock

#-- Constants ------------------------------------------------------------------

messages = [
    'validate',  'initialize',  'delegate',          'notify',
    'visualize', 'animate',     'HasFacets',         'Welcome to Facets',
    'Clock',     'Directory',   'File',              'PrototypedFrom',
    'Enum',      'Instance',    'DelegatesTo',       'GridEditor',
     'VIPShell', 'StackEditor', 'DockWindow',        'LightTableEditor',
    'Tweener',   'GridAdapter', 'RangeEditor',       'PropertySheetEditor',
    'MVC',       'ValueEditor', 'FileStackEditor',   'ColorPaletteEditor',
    'Event',     'ColorEditor', 'EnumEditor',        'ListCanvasEditor',
    'View',      'Item',        'edit_facets',       'ImageZoomEditor',
    'Group',     'HSplit',      'VSplit',            'on_facet_set',
    'Property',  'Any',         'Range',             'property_depends_on',
    'Code',      'metadata',    'LinearPath',        'MultipleInstanceEditor',
    'Theme',     'Image',       'DerivedImage',      'HLSATransform',
    'model',     'view model',  'the tao of Facets', 'reactive programming'
]
shuffle( messages )

#-- Helper functions -----------------------------------------------------------

def random_message ( index ):
    return Message(
        message   = messages[ index % len( messages ) ],
        index     = index,
        color     = random_color( index ),
        font_size = random_font_size(),
        position  = ( -10000, -10000 ),
        speed     = random_speed( index )
    )

def random_font_size ( ):
    return choice( [ 20, 30, 40 ] )

def random_speed ( index ):
    return ( (3 * (index % 2)) + randint( 4, 6 ), 0 )

def random_color ( index ):
    return ((65536 * random_rgb( index )) +
              (256 * random_rgb( index )) +
                     random_rgb( index ))

def random_rgb ( index ):
    return ((0x20 * (index % 2)) + randint( 0xB0, 0xDC ))

#-- Message class --------------------------------------------------------------

class Message ( HasFacets ):

    message   = Str
    index     = Int
    color     = Color( 0xFFFFFF )
    font_size = Int( 16 )
    text_size = Tuple( Int, Int )
    position  = Tuple( Int, Int )
    speed     = Tuple( Int, Int )

#-- _MessagesEditor class -------------------------------------------------------

class _MessagesEditor ( ControlEditor ):

    clock     = Any( Clock() )
    slots     = List
    new_frame = Bool( False )

    def paint_content ( self, g ):
        self.clock.time
        for message in self.value:
            self._paint_message( g, message )

        self.new_frame = False

    def _paint_message ( self, g, message ):
        x, y  = message.position
        if (x <= -10000) or (y <= -10000):
            message.index = index = message.index + len( self.value )
            message.set(
                text_size = ( 0, 0 ),
                message   = messages[ index % len( messages ) ],
                font_size = random_font_size(),
                color     = random_color( index ),
                speed     = random_speed( index )
        )

        g.font   = message.font_size
        text     = message.message
        tdx, tdy = self._message_size( g, message )
        dx, dy   = message.speed
        cdx, cdy = self.control.client_size
        if x <= -10000:
            if dx == 0:
                x = self._slot_for( message.index, cdx - tdx )
            else:
                x = -(randint( tdx, max( 2000, 4 * tdx ) ) + 2)

        if y <= -10000:
            if dy == 0:
                y = self._slot_for( message.index, cdy - tdy )
            else:
                y = -(randint( tdy, 6 * tdy ) + 2)

        g.text_color = 0x202020
        g.draw_text( message.message, x + 2, y + 2 )
        g.text_color = message.color
        g.draw_text( message.message, x, y )

        if self.new_frame:
            x += dx
            y += dy

            if (x > cdx) or (y > cdy):
                x = y = -10000

            message.position = ( x, y )

    def _message_size ( self, g, message ):
        if message.text_size[0] == 0:
            message.text_size = g.text_size( message.message )

        return message.text_size

    def _slot_for ( self, index, size ):
        n = 20
        if len( self.slots ) == 0:
            slots = range( 20 )
            shuffle( slots )
            self.slots = slots
        dxy = (size - 10.0) / n

        return (5 + int( round( dxy * self.slots[ index % n ] ) ))

    @on_facet_set( 'clock:time' )
    def _update ( self ):
        self.new_frame = True
        self.refresh()

#-- MessagesEditor class --------------------------------------------------------

class MessagesEditor ( CustomControlEditor ):

    klass = _MessagesEditor
    theme = Theme( '@tiles:FibreBoard1.jpg?s99l45a15', tiled = True )

#-- Messages class -------------------------------------------------------------

class Messages ( HasFacets ):

    messages = List( Message )

    view = View(
        UItem( 'messages', editor = MessagesEditor() ),
        width  = 0.67,
        height = 0.67
    )

    def _messages_default ( self ):
        return [ random_message( i ) for i in xrange( 25 ) ]

#-- Create the demo ------------------------------------------------------------

demo = Messages

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------