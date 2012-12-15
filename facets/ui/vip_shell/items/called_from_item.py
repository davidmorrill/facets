"""
Defines the CalledFromItem class used by the VIP Shell to represent debug
called_from entries.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from exception_item \
    import ExceptionItem

#-------------------------------------------------------------------------------
#  'CalledFromItem' class:
#-------------------------------------------------------------------------------

class CalledFromItem ( ExceptionItem ):
    """ Defines the CalledFromItem class used by the VIP Shell to represent
        debug called_from entries.
    """

    #-- Facet Definitions ------------------------------------------------------

    icon = '@facets:shell_called_from'

#-- EOF ------------------------------------------------------------------------
