"""
# Statusbar Demo #

This program demonstrates adding and using a status bar in a Facets UI window.

A status bar may contain one or more fields, and each field can be of a fixed
or variable size. Fixed width fields are specified in pixels, while variable
width fields are specified as fractional values relative to other variable
width fields.

The content of a status bar field is specified via the extended facet name of
the object attribute that will contain the status bar information.

In this example, there are two status bar fields:

- The current length of the text input data (variable width)
- The current time (fixed width, updated once a second).

Note that there is actually nothing special about a status bar. A **StatusBar**
is simply a specialized type of **Group** that:

- Performs horizontal layout.
- Suppresses item labels.
- Uses a special item theme.

Similarly, a **Status** item is a specialized type of **Item** that:

- Is read-only.
- Has a default width of 0.1 (making it stretchable).
- Has reduced padding to allow adjacent status items to fit more tightly
  together.

Although a status bar would normally be the last thing added to a **View**,
there is nothing preventing you from placing it wherever you want with a View.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from time \
    import sleep, strftime

from threading \
    import Thread

from facets.core_api \
    import HasPrivateFacets, Str, Property

from facets.api \
    import View, Item, StatusBar, Status

#-- The demo class -------------------------------------------------------------

class TextEditor ( HasPrivateFacets ):

    # The text being edited:
    text = Str

    # The current length of the text being edited:
    length = Property( depends_on = 'text' )

    # The current time:
    time = Str

    # The view definition:
    view = View(
        Item( 'text', style = 'custom', show_label = False ),
        StatusBar(
            Status( 'length' ),
            Status( 'time', width = 86 )
        ),
        title     = 'Text Editor',
        id        = 'facets.extra.demo.ui.Advanced.Statusbar_demo',
        width     = 0.4,
        height    = 0.4,
        resizable = True
    )

    #-- Property Implementations -----------------------------------------------

    def _get_length ( self ):
        return ( 'Length: %d characters' % len( self.text ) )

    #-- Default Facet Values ---------------------------------------------------

    def _time_default ( self ):
        thread = Thread( target = self._clock )
        thread.setDaemon( True )
        thread.start()

        return ''

    #-- Private Methods --------------------------------------------------------

    def _clock ( self ):
        """ Update the status bar time once every second.
        """
        while True:
            self.time = strftime( '%I:%M:%S %p' )
            sleep( 1.0 )

#-- Create the demo ------------------------------------------------------------

demo = TextEditor

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------