"""
The event passed to an action's 'perform' method.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import time

from facets.core_api \
    import Float, HasFacets

#-------------------------------------------------------------------------------
#  'ActionEvent' class:
#-------------------------------------------------------------------------------

class ActionEvent ( HasFacets ):
    """ The event passed to an action's 'perform' method.
    """

    #-- 'ActionEvent' interface ------------------------------------------------

    # When the action was performed (time.time()).
    when = Float

    #-- 'object' Interface -----------------------------------------------------

    def __init__ ( self, **facets ):
        """ Creates a new action event.

            Note: Every keyword argument becoames a public attribute of the
            event.
        """
        # Base-class constructor:
        super( ActionEvent, self ).__init__( **facets )

        # fixme: We currently allow anything to be tagged onto the event, which
        # is going to make code very hard to read.
        self.__dict__.update( facets )

        # When the action was performed:
        self.when = time.time()

#-- EOF ------------------------------------------------------------------------