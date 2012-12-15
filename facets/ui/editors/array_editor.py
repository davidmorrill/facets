"""
Defines array editors and the array editor factory.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import numpy

from facets.api \
    import HasFacets, Int, Float, Instance, Bool, View, Group, Item, FacetError

from facets.ui.editor_factory \
    import EditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'ArrayEditor' class:
#-------------------------------------------------------------------------------

class ArrayEditor ( EditorFactory ):
    """ Editor factory for array editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Width of the individual fields
    width = Int( -80 )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

    def readonly_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             readonly    = True )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style of editor for arrays.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the editor read-only?
    readonly = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._as     = _as = ArrayStructure( self )
        ui           = _as.view.ui( _as, parent, kind = 'subpanel' )
        ui.parent    = self.ui
        self.control = ui.control


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        if not self._busy:
            object = self.value
            shape  = object.shape
            _as    = self._as

            # 1D
            if len( shape ) == 1:
                for i in range( shape[0] ):
                    setattr( _as, 'f%d' % i, object[ i ] )
            # 2D
            elif len( shape ) == 2:
                for i in range( shape[0] ):
                    for j in range( shape[1] ):
                        setattr( _as, 'f%d_%d' % ( i, j ), object[ i, j ] )


    def update_array ( self, value ):
        """ Updates the array value associated with the editor.
        """
        self._busy = True
        self.value = value
        self._busy = False

#-------------------------------------------------------------------------------
#  'ArrayStructure' class:
#-------------------------------------------------------------------------------

class ArrayStructure ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # Editor that this structure is linked to
    editor = Instance( Editor )

    # The constructed View for the array
    view = Instance( View )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        # Save the reference to the editor:
        self.editor = editor

        # Set up the field width for each item:
        width = editor.factory.width

        # Set up the correct style for each filed:
        style = 'simple'
        if editor.readonly:
            style = 'readonly'

        # Get the array we are mirroring:
        object = editor.value

        # Determine the correct facet type to use for each element:
        facet = Float

        if object.dtype.type == 'i':
            facet = Int

        if len( object.shape ) == 1:
            self.view = self._one_dim_view( object, style, width, facet )
        elif len( object.shape ) == 2:
            self.view = self._two_dim_view( object, style, width, facet )
        else:
            raise FacetError( 'Only 1D or 2D arrays supported' )

    #-- 1D view ----------------------------------------------------------------

    def _one_dim_view ( self, object, style, width, facet ):
        content     = []
        shape       = object.shape
        items       = []
        format_func = self.editor.factory.format_func
        format_str  = self.editor.factory.format_str

        for i in range( shape[0] ):
            name = 'f%d' % i
            self.add_facet( name, facet( object[i], event = 'field' ) )
            items.append( Item( name        = name,
                                style       = style,
                                width       = width,
                                format_func = format_func,
                                format_str  = format_str,
                                padding     = -3 ) )

        group = Group( orientation = 'horizontal',
                       show_labels = False,
                       *items )
        content.append( group )

        return View( Group( show_labels = False, *content ) )

    #-- 2D view ----------------------------------------------------------------

    def _two_dim_view ( self, object, style, width, facet ):
        content     = []
        shape       = object.shape
        format_func = self.editor.factory.format_func
        format_str  = self.editor.factory.format_str

        for i in range( shape[0] ):
            items = []
            for j in range( shape[1] ):
                name = 'f%d_%d' % ( i, j )
                self.add_facet( name, facet( object[ i, j ], event = 'field' ) )
                items.append( Item( name        = name,
                                    style       = style,
                                    width       = width,
                                    format_func = format_func,
                                    format_str  = format_str,
                                    padding     = -3 ) )

            group = Group( orientation = 'horizontal',
                           show_labels = False,
                           *items )
            content.append( group )

        return View( Group( show_labels = False, *content ) )

    #-- Facet Event Handlers ---------------------------------------------------

    def _field_set ( self ):
        """ Updates the underlying array when any field changes value.
        """
        # Get the array we are mirroring:
        object = self.editor.value
        shape  = object.shape
        value  = numpy.zeros( shape, object.dtype )

        # 1D:
        if len( shape ) == 1:
            for i in range( shape[0] ):
                value[i] = getattr( self, 'f%d' % i )
        # 2D:
        elif len( shape ) == 2:
            for i in range( shape[0] ):
                for j in range( shape[1] ):
                    value[ i, j ] = getattr( self, 'f%d_%d' % ( i, j ) )

        self.editor.update_array( value )

#-- EOF ------------------------------------------------------------------------