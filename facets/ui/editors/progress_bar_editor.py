"""
Defines a ProgressBarEditor for tracking the progress of long-running processes.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Float, Int, Str, Range, Theme, ATheme, on_facet_set

from facets.ui.custom_control_editor \
    import CustomControlEditor, ControlEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The themes uses to draw the progress bar track:
track = Theme( '@xform:pt' )

#-------------------------------------------------------------------------------
#  '_ProgressBarEditor' class:
#-------------------------------------------------------------------------------

class _ProgressBarEditor ( ControlEditor ):
    """ Defines the _ProgressBarEditor for tracking the progress of long-running
        processes.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current width of the progress bar (in pixels):
    width = Int( -1 )

    # The current percentage complete value:
    percent = Str

    # The fixed size of the control:
    fixed_size = ( -1, 23 )

    # The theme to use for the progress bar:
    bar = ATheme

    #-- Public Methods ---------------------------------------------------------

    def init ( self ):
        """ Initialize the control.
        """
        hue      = min( int( round( (self.factory.hue % 360) / 3.6 ) ), 99 )
        self.bar = Theme( '@xform:pb?H%dl4S41|l66' % hue )


    def paint ( self, g ):
        """ Paints the contents of the editor control.
        """
        dx, dy = self.control.size
        track.fill( g, 0, 0, dx, dy )
        self.bar.fill(   g, 0, 0, self.width, dy )
        track.draw_text( g, self.percent, 'right', 0, 0, dx - 3, dy )


    def resize ( self, event ):
        """ Handles the editor control being resized.
        """
        self._value_set()

        super( _ProgressBarEditor, self ).resize( event )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self ):
        """ Handles the 'value' facet being changed.
        """
        low, high    = self.factory.low, self.factory.high
        value        = min( max( self.value, low ), high )
        fraction     = ((value - low) / (high - low))
        self.percent = '%.0f%%' % (100.0 * fraction)
        self.width   = int( round( self.control.size[0] * fraction ) )


    @on_facet_set( 'width, percent' )
    def _update_display ( self ):
        """ Handles any value affecting the contents of the editor control being
            changed.
        """
        self.refresh()

#-------------------------------------------------------------------------------
#  'ProgressBarEditor' class:
#-------------------------------------------------------------------------------

class ProgressBarEditor ( CustomControlEditor ):
    """ Defines the ProgressBarEditor for tracking the progress of long-running
        processes.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The custom control editor class:
    klass = _ProgressBarEditor

    # The lowest value the progress bar can have:
    low = Float( 0.0 )

    # The highest value the progress bar can have:
    high = Float( 100.0 )

    # The hue to use for the progress bar:
    hue = Range( 0, 360, 180 )

#-- EOF ------------------------------------------------------------------------
