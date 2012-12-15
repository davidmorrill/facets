"""
Defines a StringGridEditor function that returns a custom GridEditor suitable
for displaying and selecting a string from a list of strings.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-------------------------------------------------------------------------------
#  'StringGridAdapter' class:
#-------------------------------------------------------------------------------

class StringGridAdapter ( GridAdapter ):

    columns      = [ ( 'Value', 'value' ) ]
    grid_color   = 0xD0D0D0
    odd_bg_color = 0xF0F0F0

    def value_content ( self ):
        return self.item

#-------------------------------------------------------------------------------
#  'StringGridEditor' function:
#-------------------------------------------------------------------------------

def StringGridEditor ( **facets ):
    """ Returns a custom GridEditor suitable for displaying and selecting a
        string from a list of strings.
    """
    facets[ 'adapter' ]     = StringGridAdapter
    facets[ 'show_titles' ] = False
    facets.setdefault( 'operations', [] )

    return GridEditor( **facets )

#-- EOF ------------------------------------------------------------------------
