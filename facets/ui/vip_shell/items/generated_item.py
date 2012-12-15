"""
Defines the GeneratedItem class used by the VIP Shell to represent any type of
data that has been generated from another shell item (for exampe, as the result
of executing a Python or shell command).
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance

from shell_item \
    import ShellItem

#-------------------------------------------------------------------------------
#  'GeneratedItem'
#-------------------------------------------------------------------------------

class GeneratedItem ( ShellItem ):
    """ Base class for all items generated from another item in some way (e.g.
        by executing a CommandItem).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The parent item this item was generated from:
    parent = Instance( ShellItem )

#-- EOF ------------------------------------------------------------------------
