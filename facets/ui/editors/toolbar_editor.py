"""
Defines a GUI toolkit neutral Facets UI toolbar editor based on the
ToolbarControl for editing lists of objects with facets.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, Range, Enum, Bool, BasicEditorFactory

from facets.ui.ui_facets \
    import AView, Orientation

from facets.ui.controls.toolbar_control \
    import ToolbarControl

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  '_ToolbarEditor' class:
#-------------------------------------------------------------------------------

class _ToolbarEditor ( Editor ):
    """ Facets UI toolbar editor for editing lists of objects with facets using
        a ToolbarControl.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the notebook editor scrollable? This values overrides the default:
    scrollable = True

    #-- Private Facets ---------------------------------------------------------

    # The ToolbarControl we use to manage the notebook:
    toolbar = Instance( ToolbarControl )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        factory = self.factory

        # Create the toolbar control:
        self.toolbar = toolbar = ToolbarControl(
            parent      = parent,
            orientation = factory.orientation,
            spacing     = factory.spacing,
            margin      = factory.margin,
            alignment   = factory.alignment,
            full_size   = factory.full_size
        )
        control = toolbar.container

        # Make sure the toolbar has been initialized:
        toolbar.init()

        self.adapter = toolbar()

        # Set up the additional 'list items changed' event handler needed for
        # a list based facet:
        self.context_object.on_facet_set(
            self.update_editor_item, self.extended_name + '_items?',
            dispatch = 'ui'
        )

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.toolbar.items = [ self._create_item( object )
                               for object in self.value ]


    def update_editor_item ( self, event ):
        """ Handles an update to some subset of the facet's list.
        """
        # Replace the updated notebook pages:
        self.toolbar.items[ event.index: event.index + len( event.removed ) ] \
            = [ self._create_item( object ) for object in event.added ]


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_facet_set(
            self.update_editor_item, self.name + '_items?', remove = True
        )

        super( _ToolbarEditor, self ).dispose()

    #-- Private Methods --------------------------------------------------------

    def _create_item ( self, object ):
        """ Creates and returns a toolbar item for a specified object with
            facets.
        """
        control =  object.edit_facets(
            parent = self.toolbar.container,
            view   = self.factory.view,
            kind   = 'editor' ).set(
            parent = self.ui
        ).control
        control.editor = None

        return control

#-------------------------------------------------------------------------------
#  'ToolbarEditor' class:
#-------------------------------------------------------------------------------

class ToolbarEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ToolbarEditor

    # The orientation of the editor:
    orientation = Orientation

    # The spacing between adjacent toolbar controls:
    spacing = Range( 0, 32 )

    # The amount of margin to allow at the ends of the toolbar:
    margin = Range( 0, 32 )

    # The alignment of the toolbar controls along the non-layout axis:
    alignment = Enum( 'fill', 'center', 'left', 'top', 'right', 'bottom' )

    # Should the toolbar expand to use extra space along its non-layout axis?
    full_size = Bool( True )

    # Name of the view to use for each item:
    view = AView

#-------------------------------------------------------------------------------
#  'ToolbarEditorTest' class:
#-------------------------------------------------------------------------------

if __name__ == '__main__':

    from random \
         import choice, randint

    from facets.api \
        import HasFacets, Str, Range, Enum, List, View, VGroup, HGroup, \
               VSplit, HSplit, UItem, Item, Button, Code, spring

    class Person ( HasFacets ):
        name   = Str
        age    = Range( 0, 99 )
        gender = Enum( 'Male', 'Female' )
        view   = View(
            VGroup(
                Item( 'name' ),
                Item( 'age' ),
                Item( 'gender' ),
                group_theme = '@xform:b?L40'
            )
        )

    class ToolbarEditorTest ( HasFacets ):
        code   = Code
        people = List
        add    = Button( 'Add' )
        delete = Button( 'Delete' )
        view   = View(
            VSplit(
                UItem( 'people',
                       editor = ToolbarEditor( orientation = 'horizontal' ),
                       height = -80
                ),
                HSplit(
                    UItem( 'people', editor = ToolbarEditor(), width = 0.33 ),
                    UItem( 'code', width = 0.67, height = -300, springy = True )
                )
            ),
            HGroup(
                spring,
                UItem( 'add' ),
                UItem( 'delete', enabled_when = 'len(people)>0' ),
                group_theme = '@xform:b?L25'
            ),
            width  = 0.5,
            height = 0.5
        )

        def _people_default ( self ):
            return [ self._random_person() for i in xrange( 1 ) ]

        def _random_person ( self ):
            return Person(
                name   = '%s %s' % (
                         choice( [ 'Joe', 'Tom', 'Mike', 'Ralph', 'Albert' ] ),
                         choice( [ 'Smith', 'Adams', 'Thompson', 'Borg' ] ) ),
                age    = randint( 0, 99 ),
                gender = choice( [ 'Male', 'Female' ] )
            )

        def _add_set ( self ):
            self.people.append( self._random_person() )

        def _delete_set ( self ):
            del self.people[0]

    ToolbarEditorTest().edit_facets()

#-- EOF ------------------------------------------------------------------------
