"""
# Hello World 3 #

Another Hello World style demo, this one showing a simple use of Facets
property and animation capabilities.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Property, Int, View, UItem, CodeEditor, \
           property_depends_on

#-- HelloWorld Class -----------------------------------------------------------

class HelloWorld ( HasFacets ):

    hello  = Property
    length = Int
    view   = View( UItem( 'hello', style = 'readonly', editor = CodeEditor() ) )

    @property_depends_on( 'length' )
    def _get_hello ( self ):
        return ('Hello, world!\n' * 10)[ : self.length ] + '_'

    #-- Facet Event Handlers ---------------------------------------------------

    def facets_init ( self ):
        self.animate_facet( 'length', 14.0, 139, 0, repeat = 3 )

#-- Create the demo ------------------------------------------------------------

demo = HelloWorld

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
