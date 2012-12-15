"""
Defines the ErrorItem class used by the VIP Shell to represent data written to
'stderr' by a Python or shell command.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from generated_item \
    import GeneratedItem

#-------------------------------------------------------------------------------
#  'ErrorItem' class:
#-------------------------------------------------------------------------------

class ErrorItem ( GeneratedItem ):
    """ The error output produced by executing a command (i.e. stderr).
    """

    #-- Facet Definitions ------------------------------------------------------

    type       = 'error'
    icon       = '@facets:shell_error'
    color_code = '\x001'

#-- EOF ------------------------------------------------------------------------
