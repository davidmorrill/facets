"""
# Hello World 1 #

This is the perennial favorite Hello World program written using Facets. 'Nough
said...

An even simpler version can be run directly from the command line:

    python -c "from facets.api import *; HasFacets(m='Hello, world!').edit_facets(view=View(UItem('m')))"
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, View, UItem

#-- HelloWorld Class Definition ------------------------------------------------

class HelloWorld ( HasFacets ):

    hello = Str( 'Hello, world!' )
    view  = View( UItem( 'hello' ) )

#-- Create the demo ------------------------------------------------------------

demo = HelloWorld

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
