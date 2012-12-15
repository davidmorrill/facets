"""
Defines the IDataContext interface used to render data defined by an object
implementing the IDataGrid interface.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Interface, Instance, Control

#-------------------------------------------------------------------------------
#  'IDataContext' class:
#-------------------------------------------------------------------------------

class IDataContext ( Interface ):
    """ Defines the IDataContext interface used to render data defined by an
        object implementing the IDataGrid interface.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The implementation of the IDataGrid interface used to defined the data to
    # to render:
    grid = Instance( 'facets.ui.data.i_data_grid.IDataGrid' )

    # The control the data is rendered into:
    control = Instance( Control )

#-- EOF ------------------------------------------------------------------------
