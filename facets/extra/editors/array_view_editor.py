""" Defines an ArrayViewEditor for displaying 1-d or 2-d arrays of values.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Property, List, Str, Bool, Font, Callable, View, Item, GridEditor, \
           UIEditor, BasicEditorFactory

from facets.ui.grid_adapter \
    import GridAdapter

#-------------------------------------------------------------------------------
#  'ArrayViewAdapter' class:
#-------------------------------------------------------------------------------

class ArrayViewAdapter ( GridAdapter ):

    #-- Facet Definitions ------------------------------------------------------

    # Is the array 1D or 2D?
    is_2d = Bool( True )

    # Should array rows and columns be transposed:
    transpose  = Bool( False )

    alignment  = 'right'
    index_text = Property

    #-- Property Implementations -----------------------------------------------

    def _get_index_text ( self ):
        return str( self.row )


    def _get_content ( self ):
        if self.is_2d:
            return self.item[ self.column_id ]

        return self.item

    #-- Public Methods ---------------------------------------------------------

    def get_item ( self, row ):
        """ Returns the value of the *object.facet[row]* item.
        """
        if self.is_2d:
            if self.transpose:
                return getattr( self.object, self.name )[:, row]

            return super( ArrayViewAdapter, self ).get_item( row )

        return getattr( self.object, self.name )[ row ]


    def len ( self ):
        """ Returns the number of items in the specified *object.facet* list.
        """
        if self.transpose:
            return getattr( self.object, self.name ).shape[1]

        return super( ArrayViewAdapter, self ).len()

#-------------------------------------------------------------------------------
#  '_ArrayViewEditor' class:
#-------------------------------------------------------------------------------

class _ArrayViewEditor ( UIEditor ):

    #-- Facet Definitions ------------------------------------------------------

    # Indicate that the editor is scrollable/resizable:
    scrollable = True

    # Should column titles be displayed:
    show_titles = Bool( False )

    # The grid adapter being used for the editor view:
    av_adapter = Callable

    #-- Public Methods ---------------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the Facets UI for displaying the array.
        """
        # Make sure that the value is an array of the correct shape:
        shape     = self.value.shape
        len_shape = len( shape )
        if (len_shape == 0) or (len_shape > 2):
            raise ValueError(
                "ArrayViewEditor can only display 1D or 2D arrays"
            )

        factory          = self.factory
        cols             = 1
        titles           = factory.titles
        n                = len( titles )
        self.show_titles = (n > 0)
        is_2d            = (len_shape == 2)
        if is_2d:
            index = 1
            if factory.transpose:
                index = 0

            cols = shape[ index ]
            if self.show_titles:
                if n > cols:
                    titles = titles[: cols]
                elif n < cols:
                    if (cols % n) == 0:
                        titles, old_titles, i = [], titles, 0
                        while len( titles ) < cols:
                            titles.extend( '%s%d' % ( title, i )
                                           for title in old_titles )
                            i += 1
                    else:
                        titles.extend( [''] * (cols - n) )
            else:
                titles = [ 'Data %d' % i for i in range( cols ) ]

        columns = [ ( title, i ) for i, title in enumerate( titles ) ]

        if factory.show_index:
            columns.insert( 0, ( 'Index', 'index' ) )

        def create_adapter ( *args, **traits ):
            return ArrayViewAdapter(
                *args,
                is_2d     = is_2d,
                columns   = columns,
                transpose = factory.transpose,
                format    = factory.format,
                font      = factory.font,
                **traits
           )

        self.av_adapter = create_adapter

        return self.edit_facets(
            view   = '_array_view',
            parent = parent,
            kind   = 'editor'
        )

    #-- Private Methods --------------------------------------------------------

    def _array_view ( self ):
        """ Return the view used by the editor.
        """
        return View(
            Item( 'object.object.' + self.name,
                  id         = 'grid_editor',
                  show_label = False,
                  editor     = GridEditor( show_titles = self.show_titles,
                                           operations  = [],
                                           adapter     = self.av_adapter )
        ),
        id        = 'array_view_editor',
        resizable = True
    )

#-------------------------------------------------------------------------------
#  'ArrayViewEditor' class:
#-------------------------------------------------------------------------------

class ArrayViewEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor implementation class:
    klass = _ArrayViewEditor

    # Should an index column be displayed:
    show_index = Bool( True )

    # List of (optional) column titles:
    titles = List( Str )

    # Should the array be logically transposed:
    transpose = Bool( False )

    # The format used to display each array element:
    format = Str( '%s' )

    # The font to use for displaying each array element:
    font = Font( 'Courier 10' )

#-- EOF ------------------------------------------------------------------------