"""
Defines the LocalsItem class used by the VIP Shell to represent debug
show_locals entries.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from result_item \
    import ResultItem

from facets.ui.vip_shell.helper \
    import max_len

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The maximum length of a local symbol name to do alignment on:
MaxAlignment = 10

#-------------------------------------------------------------------------------
#  'LocalsItem' class:
#-------------------------------------------------------------------------------

class LocalsItem ( ResultItem ):
    """ Defines the LocalsItem class used by the VIP Shell to represent debug
        show_locals entries.
    """

    #-- Facet Definitions ------------------------------------------------------

    icon = '@facets:shell_locals'

    #-- ResultItem Method Overrides --------------------------------------------

    def as_dict ( self, item, indent, name = '<dict>' ):
        """ Returns the dictionary *item* pretty_printed as a string.
        """
        if len( indent ) > 0:
            return super( LocalsItem, self ).as_dict( item, indent, name )

        if len( item ) == 0:
            return ''

        items     = item.items()
        n         = 0
        separator = ','
        if self.lod > 0:
            n         = max_len( item.keys(), MaxAlignment )
            separator = ''

        try:
            items.sort( lambda l, r: cmp( l[0], r[0] ) )
        except:
            pass

        return (separator.join( [
            '\n%s = %s' % ( key.ljust( n ), self.as_str( value ).strip() )
            for key, value in items
        ] ))

#-- EOF ------------------------------------------------------------------------
