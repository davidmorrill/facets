"""
Defines the BoundsPath class that implements animatable 2D bounds paths of the
form: (x,y,dx,dy). The path works by simply combining two 2D integer paths, one
for the position, and another for the size, thus allowing all of the various 2D
integer point paths to be re-used for animating 2D bounds.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, View, VGroup, UItem

from linear_2d_int_path \
    import Linear2DIntPath

#-------------------------------------------------------------------------------
#  'BoundsPath' class:
#-------------------------------------------------------------------------------

class BoundsPath ( Linear2DIntPath ):
    """ Defines the BoundsPath class that implements animatable 2D bounds paths
        of the form: (x,y,dx,dy). The path works by simply combining two 2D
        integer paths, one for the position, and another for the size, thus
        allowing all of the various 2D integer point paths to be re-used for
        animating 2D bounds.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The path used to animate the position:
    position = Instance( Linear2DIntPath, () )

    # The path used to animate the size:
    size = Instance( Linear2DIntPath, () )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            UItem( 'position', style = 'custom' ),
            label       = 'Position',
            group_theme = '@xform:btd?L25'
        ),
        VGroup(
            UItem( 'size', style = 'custom' ),
            label       = 'Size',
            group_theme = '@xform:btd?L25'
        )
    )

    #-- Path Method Overrides --------------------------------------------------

    def at ( self, v0, v1, t ):
        """ Returns the value along the bounds path at time t by combining the
            values for the 'position' and 'size' paths at time t.
        """
        return (self.position.at( v0[:2], v1[:2], t ) +
                self.size.at(     v0[2:], v1[2:], t ))

#-- EOF ------------------------------------------------------------------------
