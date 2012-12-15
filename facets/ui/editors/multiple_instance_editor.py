"""
Facets UI editor for editing multiple instances as if they were a single object.
That is, the user appears to be editing a single object, but all changes made
to the edited object are made on all object instances being edited
simultaneously. This editor is useful in cases where the user may want to adjust
some or all of the properties of a group of related objects without having to
edit each object instance individually.

The value edited by this editor must have list semantics and only contain
instances which derive from HasFacets.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, Instance, List, Str, Any, UIEditor, BasicEditorFactory, \
           on_facet_set, View, Item, InstanceEditor

from facets.ui.ui_facets \
    import AView

#-------------------------------------------------------------------------------
#  '_MultipleInstanceEditor' class:
#-------------------------------------------------------------------------------

class _MultipleInstanceEditor ( UIEditor ):
    """ Facets UI editor for editing multiple instances as if they were a single
        object. That is, the user appears to be editing a single object, but all
        changes made to the edited object are made on all object instances being
        edited simultaneously. This editor is useful in cases where the user may
        want to adjust some or all of the properties of a group of related
        objects without having to edit each object instance individually.

        The value edited by this editor must have list semantics and only
        contain instances which derive from HasFacets.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current item being edited:
    item = Instance( HasFacets )

    # The set of facets being ignored:
    ignore = Any

    # The set of facets being watched:
    watch = Any

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            Item( 'item',
                  style      = 'custom',
                  show_label = False,
                  editor     = InstanceEditor( view = self.factory.view )
            )
        )

    #-- Method Definitions -----------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Set up the facet ignore and watch sets:
        factory = self.factory
        if len( factory.ignore ) > 0:
            self.ignore = set( factory.ignore )

        if len( factory.watch ) > 0:
            self.watch = set( factory.watch )

        # Make sure we have initialized the editor state by this point:
        self.update_editor()

        super( _MultipleInstanceEditor, self ).init( parent )


    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        return self.edit_facets( parent = parent, kind = 'editor' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        items = self.value
        if self.item is None:
            if len( items ) > 0:
                self.item = items[0]
        elif len( items ) > 0:
            if self.item not in items:
                self.item = items[0]
        else:
            self.item = None

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'item:-' )
    def _item_modified ( self, object, facet, new ):
        """ Handles any facet on the edited item being modified.
        """
        # Filter out any facets that don't match our criteria:
        if (self.ignore is not None) and (facet in self.ignore):
            return

        if (self.watch is not None) and (facet not in self.watch):
            return

        # Make the change on all of the other objects in the group:
        for item in self.value:
            if item is not object:
                try:
                    setattr( item, facet, new )
                except:
                    pass

#-------------------------------------------------------------------------------
#  'MultipleInstanceEditor' class:
#-------------------------------------------------------------------------------

class MultipleInstanceEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _MultipleInstanceEditor

    # The (optional) view to use for editing objects:
    view = AView

    # The (optional) list of facet names to ignore:
    ignore = List( Str )

    # The (optional) list of facet names to watch:
    watch = List( Str )

#-- EOF ------------------------------------------------------------------------