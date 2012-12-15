"""
Defines a GUI toolkit neutral Pen class used to describe the properties that a
GUI toolkit specific pen should have.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/L8ICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Color, Range, Enum

#-------------------------------------------------------------------------------
#  'Pen' class:
#-------------------------------------------------------------------------------

class Pen ( HasPrivateFacets ):
    """ Defines an abstract Pen object that can be assigned as a value of the
        Graphics 'pen' facet. This allows assigning properties such as pen
        color, line style and line width in a GUI toolkit neutral manner.

        Note that it is the responsibility of the GUI toolkit specific
        subclasses of Graphics to correctly interpret the values of a Pen object
        for their toolkit.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The color of the pen:
    color = Color

    # The line width of the pen:
    width = Range( 0, 20, 1 )

    # The line style of the pen:
    style = Enum( 'solid', 'dash', 'dot' )

#-- EOF ------------------------------------------------------------------------
