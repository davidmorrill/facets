"""
This is a variation on the Hello World program using a <b>GridEditor</b> and
<b>GridAdapter</b>.

This example is purposely kept short. For a more detailed, and realistic,
example of the use of the <b>GridEditor</b> and <b>GridAdapter</b>, refer to the
<i>Grid editor demo</i> in the <i>Advanced</i> section.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, View, UItem, GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- HelloWorldAdapter Class Definition -----------------------------------------

class HelloWorldAdapter ( GridAdapter ):

    columns       = [ ( a, a ) for a in 'ABCDEF' ]
    even_bg_color = 0xF0F0F0

    def text ( self ):
        return 'Hello, world! (%d,%d)' % ( self.row + 1, self.column + 1 )

    def len ( self ):
        return 10000

#-- HelloWorld Class Definition ------------------------------------------------

class HelloWorld ( HasFacets ):

    hello = Str( 'Value not used' )

    view = View(
        UItem( 'hello',
               editor = GridEditor(
                   adapter    = HelloWorldAdapter,
                   operations = [] )
        )
    )

#-- Create the demo ------------------------------------------------------------

demo = HelloWorld

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
