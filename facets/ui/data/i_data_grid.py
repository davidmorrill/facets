"""
Defines the IDataGrid interface used to bind scalar, 1D or 2D data groups and
optional labels for purposes of calculating geometry sizes and rendering the
data.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Interface, Instance, Enum, Int, Bool

from i_data_context \
    import IDataContext

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# Specify which data axes an attribute applies to:
Axes = Enum( None, 'primary', 'secondary', 'both' )

#-------------------------------------------------------------------------------
#  'IDataGrid' interface:
#-------------------------------------------------------------------------------

class IDataGrid ( Interface ):
    """ Defines the IDataGrid interface used to bind scalar, 1D or 2D data
        groups and optional labels for purposes of calculating geometry sizes
        and rendering the data.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The context the data grid is associated with:
    context = Instance( IDataContext )

    # The available label sets:
    # - None:        There are no labels.
    # - 'primary':   There are labels defined for the primary data axis.
    # - 'secondary': There are labels defined for the secondary data axis.
    # - 'both':      There are labels defined for both the primary and secondary
    #                data axes.
    # Note: 'secondary' and 'both' should only be used in cases where the data
    # is logically a 2D array.
    label = Axes

    # The number of primary cells (a value <= 0 means that the data consists of
    # a single scalar value, and is not a 1D vector or 2D array):
    primary = Int

    # The number of secondary cells (a value <= 0 means that there are no
    # secondary cells, and that the data is a 1D vector and not a 2D array):
    secondary = Int

    # Which data axis is laid out horizontally. This is only used cases where
    # the answer is ambiguous:
    # - The data is logically a 2D array.
    # - The data is logically a 1D vector, but the Theme supports a repeating
    #   grid layout.
    horizontal = Enum( 'primary', 'secondary' )

    # Can the user transpose the primary and secondary data axes? This only
    # applies in cases where the data is logically a 2D array.
    transpose = Bool

    # Which axes can the user resize?
    resize = Axes

    # Which axes can the user hide elements on?
    hide = Axes

    # Which axes can the user re-order elements on?
    reorder = Axes

    #-- Public Methods ---------------------------------------------------------

    def get_data ( self, primary, secondary ):
        """ Returns an object that implements the IDataCell interface for the
            data element specified by the *primary* and *secondary* indices.

            Note that the calling convention used for this method depends upon
            the 'primary' and 'secondary' values returned by the interface:
            - primary   <= 0: get_data()
            - secondary <= 0: get_data( primary )
            - otherwise:      get_data( primary, secondary )

            A result of None means no data will be rendered or computed for the
            specified data element.
        """


    def get_label ( self ):
        """ Returns an object that implements the IDataCell interface for the
            context's label element. This method is only called in the case
            where the interface's 'primary' attribute is <= 0 and 'label'
            attribute is not None.

            A result of None means no data will be rendered or computed for the
            specified label element.
        """


    def get_primary_label ( self, index ):
        """ Returns an object that implements the IDataCell interface for the
            primary axis label element specified by *index*. This method is only
            called in the case where the interface's 'primary' attribute is > 0,
            and the 'label' attribute is 'primary' or 'both'.

            A result of None means no data will be rendered or computed for the
            specified label element.
        """


    def get_secondary_label ( self, index ):
        """ Returns an object that implements the IDataCell interface for the
            secondary axis label element specified by *index*. This method is
            only called in the case where the interface's 'primary' attribute
            is > 0, the 'secondary' attribute is > 0, and the 'label' attribute
            is 'secondary' or 'both'.

            A result of None means no data will be rendered or computed for the
            specified label element.
        """

#-- EOF ------------------------------------------------------------------------
