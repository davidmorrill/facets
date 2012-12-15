"""
Defines the PersistedCommandItem class used by the VIP Shell to represent Python
and shell commands that have been persisted across shell sessions.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from command_item \
    import CommandItem

#-------------------------------------------------------------------------------
#  'PersistedCommandItem' class:
#-------------------------------------------------------------------------------

class PersistedCommandItem ( CommandItem ):
    """ A persisted version of a command item.
    """

#-- EOF ------------------------------------------------------------------------
