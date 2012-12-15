"""
Defines the tuple editor and the tuple editor factory
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, List, Tuple, Str, Int, Any, View, Group, Item, \
           EditorFactory, BasicEditorFactory, Bool, FacetType

from facets.core.facet_base \
    import SequenceTypes

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  'TupleStructure' class:
#-------------------------------------------------------------------------------

class TupleStructure ( HasFacets ):
    """ Creates a view containing items for each field in a tuple.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Editor this structure is linked to:
    editor = Any

    # The constructed View for the tuple:
    view = Any

    # Number of tuple fields:
    fields = Int

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        factory = editor.factory
        types   = factory.types
        labels  = factory.labels
        editors = factory.editors
        cols    = factory.cols

        # Save the reference to the editor:
        self.editor = editor

        # Get the tuple we are mirroring:
        object = editor.value

        # For each tuple field, add a facet with the appropriate facet
        # definition and default value:
        content     = []
        self.fields = len( object )
        len_labels  = len( labels )
        len_editors = len( editors )

        if types is None:
            type = editor.value_facet.handler
            if isinstance( type, Tuple ):
                types = type.types

        if not isinstance( types, SequenceTypes ):
            types = [ types ]

        len_types = len( types )
        if len_types == 0:
            types     = [ Any ]
            len_types = 1

        for i, value in enumerate( object ):
            type = types[ i % len_types ]

            auto_set = enter_set = None
            if isinstance( type, FacetType ):
                auto_set  = type.auto_set
                enter_set = type.enter_set

            if auto_set is None:
                auto_set = factory.auto_set

            if enter_set is None:
                enter_set = factory.enter_set

            label = ''
            if i < len_labels:
                label = labels[i]

            editor = None
            if i < len_editors:
                editor = editors[i]

            name = 'f%d' % i
            self.add_facet( name, type( value, event = 'field',
                                        auto_set     = auto_set,
                                        enter_set    = enter_set  ) )
            item = Item( name        = name,
                         label       = label,
                         editor      = editor,
                         format_str  = factory.format_str,
                         format_func = factory.format_func )

            if cols <= 1:
                content.append( item )
            else:
                if (i % cols) == 0:
                    group = Group( orientation = 'horizontal',
                                   show_labels = (len_labels != 0))
                    content.append( group )

                group.content.append( item )
                # Set this as the container for its content. Lack of this
                # statement did not handle 'show_labels' correctly.
                group.set_container()

        self.view = View(
            Group( show_labels = (len_labels != 0), *content )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _field_set ( self ):
        """ Updates the underlying tuple when any field changes value.
        """
        self.editor.value = tuple( [ getattr( self, 'f%d' % i )
                                     for i in range( self.fields ) ] )

#-------------------------------------------------------------------------------
#  '_TupleEditor' class:
#-------------------------------------------------------------------------------

class _TupleEditor ( Editor ):
    """ Editor for editing tuples.

        The editor displays an editor for each of the fields in the tuple,
        based on the type of each field.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._ts     = ts = TupleStructure( self )
        self._ui     = ui = ts.view.ui( ts, parent, kind = 'editor' ).set(
                                        parent = self.ui )
        self.adapter = ui.control

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        ts = self._ts
        for i, value in enumerate( self.value ):
            setattr( ts, 'f%d' % i, value )


    def get_error_control ( self ):
        """ Returns the editor's control for indicating error status.
        """
        return self._ui.get_error_controls()

#-------------------------------------------------------------------------------
#  'TupleEditor' class:
#-------------------------------------------------------------------------------

class TupleEditor ( BasicEditorFactory ):
    """ Editor factory for tuple editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the Editor class to be instantiated:
    klass = _TupleEditor

    # Facet type definitions for each tuple field:
    types = Any

    # Labels for each of the tuple fields:
    labels = List( Str )

    # Editors for each of the tuple fields:
    editors = List( EditorFactory )

    # Number of tuple fields or rows:
    cols = Int( 1 )

    # Is user input set on every keystroke? This is applied to every field
    # of the tuple, provided the field does not already have an 'auto_set'
    # metadata or an editor defined.
    auto_set = Bool( True )

    # Is user input set when the Enter key is pressed? This is applied to
    # every field of the tuple, provided the field does not already have an
    # 'enter_set' metadata or an editor defined.
    enter_set = Bool( False )

#-- EOF ------------------------------------------------------------------------