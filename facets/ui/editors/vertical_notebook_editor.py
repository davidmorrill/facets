"""
Defines a GUI toolkit neutral Facets UI vertical notebook editor for editing
lists of objects with facets.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, Str, Any, List, Bool, Undefined, on_facet_set, Editor, \
           BasicEditorFactory

from facets.core.facet_base \
    import user_name_for

from facets.ui.ui_facets \
    import AView, ATheme

from facets.ui.controls.vertical_notebook \
    import VerticalNotebook

#-------------------------------------------------------------------------------
#  '_VerticalNotebookEditor' class:
#-------------------------------------------------------------------------------

class _VerticalNotebookEditor ( Editor ):
    """ Facets UI vertical notebook editor for editing lists of objects with
        facets.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the notebook editor scrollable? This values overrides the default:
    scrollable = True

    #-- Private Facets ---------------------------------------------------------

    # The currently selected notebook page object (or objects):
    selected_item = Any
    selected_list = List

    # The VerticalNotebook we use to manage the notebook:
    notebook = Instance( VerticalNotebook )

    # Dictionary of page counts for all unique names:
    pages = Any( {} )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory
        self.notebook = notebook = VerticalNotebook( **factory.get(
            'multiple_open', 'scrollable', 'double_click'
        ) )

        if factory.closed_theme is not None:
            notebook.closed_theme = factory.closed_theme

        if factory.open_theme is not None:
            notebook.open_theme = factory.open_theme

        notebook.editor = self
        self.adapter = self.notebook.create_control( parent )

        # Set up the additional 'list items changed' event handler needed for
        # a list based facet:
        self.context_object.on_facet_set(
            self.update_editor_item, self.extended_name + '_items?',
            dispatch = 'ui'
        )

        # Synchronize the editor selection with the user selection:
        if factory.multiple_open:
            self.sync_value( factory.selected, 'selected_list', 'both',
                             is_list = True )
        else:
            self.sync_value( factory.selected, 'selected_item', 'both' )

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        # Replace all of the current notebook pages:
        pages = [ self._create_page( object ) for object in self.value ]
        if len( pages ) > 0:
            pages[0].is_open = True

        self.notebook.pages = pages


    def update_editor_item ( self, event ):
        """ Handles an update to some subset of the facet's list.
        """
        # Replace the updated notebook pages:
        self.notebook.pages[ event.index: event.index + len( event.removed ) ] \
            = [ self._create_page( object ) for object in event.added ]


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_facet_set(
            self.update_editor_item, self.name + '_items?', remove = True
        )
        del self.notebook.pages[:]

        super( _VerticalNotebookEditor, self ).dispose()

    #-- Facet Event Handlers ---------------------------------------------------

    def _selected_item_set ( self, old, new ):
        """ Handles the selected item being changed.
        """
        if new is not None:
            self.notebook.open( self._find_page( new ) )
        elif old is not None:
            self.notebook.close( self._find_page( old ) )


    def _selected_list_set ( self, old, new ):
        """ Handles the selected list being changed.
        """
        notebook = self.notebook
        for object in old:
            notebook.close( self._find_page( object ) )

        for object in new:
            notebook.open( self._find_page( object ) )


    def _selected_list_items_set ( self, event ):
        self._selected_list_set( event.removed, event.added )

    @on_facet_set( 'notebook:pages:is_open' )
    def _page_state_modified ( self, object, is_open ):
        if self.factory.multiple_open:
            object = object.data
            if is_open:
                if object not in self.selected_list:
                    self.selected_list.append( object )
            elif object in self.selected_list:
                self.selected_list.remove( object )
        elif is_open:
            self.selected_item = object.data
        else:
            self.selected_item = None

    #-- Private Methods --------------------------------------------------------

    def _create_page ( self, object ):
        """ Creates and returns a notebook page for a specified object with
            facets.
        """
        # Create a new notebook page:
        page = self.notebook.create_page().set( data = object )

        # Create the Facets UI for the object to put in the notebook page:
        ui = object.edit_facets( parent = page.parent,
                                 view   = self.factory.view,
                                 kind   = 'editor' ).set(
                                 parent = self.ui )

        # Get the name of the page being added to the notebook:
        name      = ''
        page_name = self.factory.page_name
        if page_name[:1] == '.':
            if getattr( object, page_name[1:], Undefined ) is not Undefined:
                page.register_name_listener( object, page_name[1:] )
        else:
            name = page_name

        if name == '':
            name = user_name_for( object.__class__.__name__ )

        # Make sure the name is not a duplicate, then save it in the page:
        if page.name == '':
            self.pages[ name ] = count = self.pages.get( name, 0 ) + 1
            if count > 1:
                name += (' %d' % count)

            page.name = name

        # Save the Facets UI in the page so it can dispose of it later:
        page.ui = ui

        # Return the new notebook page:
        return page


    def _find_page ( self, object ):
        """ Find the notebook page corresponding to a specified object. Returns
            the page if found, and **None** otherwise.
        """
        for page in self.notebook.pages:
            if object is page.data:
                return page

        return None

#-------------------------------------------------------------------------------
#  'VerticalNotebookEditor' class:
#-------------------------------------------------------------------------------

class VerticalNotebookEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _VerticalNotebookEditor

    # The theme to use for closed notebook pages:
    closed_theme = ATheme

    # The theme to use for open notebook pages:
    open_theme = ATheme

    # Allow multiple open pages at once?
    multiple_open = Bool( False )

    # Should the notebook be scrollable?
    scrollable = Bool( False )

    # Use double clicks (True) or single clicks (False) to open/close pages:
    double_click = Bool( False )

    # Extended name to use for each notebook page. It can be either the actual
    # name or the name of an attribute on the object in the form:
    # '.name[.name...]'
    page_name = Str

    # Name of the view to use for each page:
    view = AView

    # Name of the [object.]facet[.facet...] to synchronize notebook page
    # selection with:
    selected = Str

#-- EOF ------------------------------------------------------------------------