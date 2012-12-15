"""
Defines the ThemeContext class which implements the IDataContext interface and
is used to render data defined by an object implementing the IDataGrid interface
using a specified Theme object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance

from theme \
    import Theme

from facets.ui.data.api \
    import DataContext

#-------------------------------------------------------------------------------
#  'ThemeContext' class:
#-------------------------------------------------------------------------------

class ThemeContext ( DataContext ):
    """ Defines the ThemeContext class which implements the IDataContext
        interface and is used to render data defined by an object implementing
        the IDataGrid interface using a specified Theme object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The Theme used to render the data with:
    theme = Instance( Theme )

#-- EOF ------------------------------------------------------------------------
