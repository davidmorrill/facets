"""
Defines the OutputItem class used by the VIP Shell to represent data written to
'stdout' by a Python or shell command.
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
#  'OutputItem' class:
#-------------------------------------------------------------------------------

class OutputItem ( GeneratedItem ):
    """ The output produced by executing a command (i.e. stdout).
    """

    #-- Facet Definitions ------------------------------------------------------

    type       = 'output'
    icon       = '@facets:shell_output'
    color_code = '\x000'

#-- EOF ------------------------------------------------------------------------
