"""
Defines the LogItem class used by the VIP Shell to represent debug log entries.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core.debug \
    import DebugLevel

from result_item \
    import ResultItem

#-------------------------------------------------------------------------------
#  'LogItem' class:
#-------------------------------------------------------------------------------

class LogItem ( ResultItem ):
    """ Defines the LogItem class used by the VIP Shell to represent debug log
        entries.
    """

    #-- Facet Definitions ------------------------------------------------------

    icon = '@facets:shell_debug'

    # The level of logging information being displayed:
    level = DebugLevel

    #-- Facet Event Handlers ---------------------------------------------------

    def _level_set ( self, level ):
        """ Handles the 'level' facet being changed.
        """
        self.icon = '@facets:shell_' + level

#-- EOF ------------------------------------------------------------------------
