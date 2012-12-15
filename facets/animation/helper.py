"""
Defines common values used within the 'facets.animation' package.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from math \
    import tanh, pi

from facets.api \
    import ATheme, Item, ScrubberEditor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Precompute the Ease In/Ease Out constant:
tanh25 = tanh( 2.5 )

# Precompute 2 * pi:
two_pi = 2.0 * pi

# Precompute pi / 2:
pi_two = pi / 2.0

# Degress to radians conversion factor:
d2r = two_pi / 360.0

#-------------------------------------------------------------------------------
#  'IRange' class:
#-------------------------------------------------------------------------------

class IRange ( Item ):
    """ Defines a custom ScrubberEditor Item class for integer values.
    """

    #-- Facet Definitions ------------------------------------------------------

    width      = -40
    editor     = ScrubberEditor()
    item_theme = ATheme( '#themes:ScrubberEditor' )

#-------------------------------------------------------------------------------
#  'FRange' class:
#-------------------------------------------------------------------------------

class FRange ( IRange ):
    """ Defines a custom ScrubberEditor Item class for float values.
    """

    #-- Facet Definitions ------------------------------------------------------

    editor = ScrubberEditor( increment = 0.01 )

#-- EOF ------------------------------------------------------------------------
