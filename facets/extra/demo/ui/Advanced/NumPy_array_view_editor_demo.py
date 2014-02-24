"""
# NumPy ArrayViewEditor Demo #

A demonstration of how the **ArrayViewEditor** can be used to display (large)
*NumPy* arrays, in this case 100,000 random 3D points from a unit cube.

Note that the ArrayViewEditor has the following facets:

    # Should an index column be displayed:
    show_index = Bool( True )

    # List of (optional) column titles:
    titles = List( Str )

    # Should the array be logically transposed:
    transpose = Bool( False )

    # The format used to display each array element:
    format = Str( '%s' )

By default, the array row index will be shown in column one. If *show_index* is
*False*, then the row index column is omitted.

If the list of *titles* is empty, no column headers will be displayed.

If the number of column headers is less than the number of array columns, then
there are two cases:

- If *(number of array_columns) % (number of titles) == 0*, then the titles are
  used to construct a series of repeating column headers with increasing
  subscripts (e.g. an *(n x 6)* array with titles of *['x','y','z']* would
  result in column headers of: *x0*, *y0*, *z0*, *x1*, *y1*, *z1*).

- In all other cases the titles are used as the column headers for the
  first set of columns, and the remaining column headers are set to the
  empty string (e.g. an *(n x 5)* array with titles of *['x','y','z']* would
  result in column headers of: *x*, *y*, *z*, *''*, *''*).

Setting *transpose* to *True* will logically transpose the input array (e.g. an
*(3 x n)* array will be displayed as an *(n x 3)* array).
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from numpy.random \
    import random

from facets.api \
    import HasFacets, Array, View, Item, ArrayViewEditor

#-- NumpyArrayDemo class -------------------------------------------------------

class NumpyArrayDemo ( HasFacets ):

    data = Array

    view = View(
        Item( 'data',
              show_label = False,
              editor     = ArrayViewEditor( titles = [ 'x', 'y', 'z' ],
                                            format = '%.4f',
                                            font   = 'Arial 8' )
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