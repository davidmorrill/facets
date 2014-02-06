"""
# NumPy Array GridEditor Demo #

A demonstration of how the **GridEditor** can be used to display (large) *NumPy*
arrays, in this case 100,000 random 3D points from a unit cube.

In addition to showing the coordinates of each point, it also displays the
index of each point in the array, as well as a red flag if the point lies within
0.25 of the center of the cube.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from numpy \
    import sqrt

from numpy.random \
    import random

from facets.core_api \
    import HasFacets, Property, Array

from facets.api \
    import View, Item, GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- Tabular Adapter Definition -------------------------------------------------

class ArrayAdapter ( GridAdapter ):

    columns = [ ( 'i', 'index' ), ( 'x', 0 ), ( 'y', 1 ),  ( 'z', 2 ) ]

    font        = 'Courier 10'
    alignment   = 'right'
    format      = '%.4f'
    index_text  = Property
    index_image = Property

    def _get_index_text ( self ):
        return str( self.row )

    def _get_index_image ( self ):
        x, y, z = self.item
        if sqrt( (x - 0.5) ** 2 + (y - 0.5) ** 2 + (z - 0.5) ** 2) <= 0.25:
            return '@icons:red_ball'

        return None

#-- NumpyArrayDemo class -------------------------------------------------------

class NumpyArrayDemo ( HasFacets ):

    data = Array

    view = View(
        Item( 'data',
              show_label = False,
              style      = 'readonly',
              editor     = GridEditor( adapter = ArrayAdapter, operations = [] )
        ),
        title     = 'Array Viewer',
        width     = 0.3,
        height    = 0.8,
        resizable = True
    )

    def _data_default ( self ):
        return random( ( 100000, 3 ) )

#-- Create the demo ------------------------------------------------------------

demo = NumpyArrayDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------