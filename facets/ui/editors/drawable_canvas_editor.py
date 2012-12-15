"""
Defines an editor that displays a DrawableCanvas object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Instance, Event, ATheme, BasicEditorFactory, Editor, \
           on_facet_set, inn

from facets.ui.drawable.drawable \
    import DrawableCanvas

from facets.ui.controls.themed_window \
    import ThemedWindow

#-------------------------------------------------------------------------------
#  'DrawableCanvasControl' class:
#-------------------------------------------------------------------------------

class DrawableCanvasControl ( ThemedWindow ):
    """ Defines a GUI toolkit independent DrawableCanvasControl for creating
        themed controls which display the contents of DrawableCanvas objects.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The DrawableCanvas object being rendered:
    canvas = Instance( DrawableCanvas )

    # The canvas item currently having the mouse capture (if any):
    capture = Any

    # The canvas item the most recent mouse event was sent to (if any):
    mouse_item = Any

    # Event fired when any attribute affecting the visual appearance of the
    # control's content is modified:
    modified = Event

    #-- ThemedWindow Method Overrides ------------------------------------------

    def paint_content ( self, g ):
        """ Paints the content of the window into the device context specified
            by *g*.
        """
        inn( self.canvas ).draw( g )

    #-- ThemedWindow Method Overrides ------------------------------------------

    def resize ( self, event ):
        """ Handles the control being resized.
        """
        super( DrawableCanvasControl, self ).resize( event )

        inn( self.canvas ).set( bounds = self.content_bounds )

    #-- Facet Event Handlers ---------------------------------------------------

    def _canvas_set ( self, old, new ):
        """ Handles the 'canvas' facet being changed.
        """
        inn( old ).set( owner = None )
        inn( new ).set( owner = self, bounds = self.content_bounds )
        self.controller = new


    def _modified_set ( self ):
        """ Handles the content of the canvas being changed.
        """
        self.refresh()

    #-- Control Event Handlers -------------------------------------------------

    def normal_mouse ( self, x, y, event ):
        """ Handles routing a mouse event to the appropriate canvas item (if
            any).
        """
        name = event.name
        if name == 'leave':
            self._mouse_leave( event )
        elif name != 'enter':
            item = self.capture
            if item is None:
                item = self._item_at( x, y )

            # Check to see if we entered a new item:
            self._mouse_enter( event, item )

            if item is not None:
                # Send event to item:
                self._item_event_for( item, name, event )

                # Synchronize the item's cursor with the control's cursor:
                cursor = getattr( item, 'cursor', None )
                if cursor is not None:
                    self.control.cursor = cursor

                # Set the current mouse capture:
                self.capture = (item if getattr( item, 'capture', False ) else
                                None)

                self._mouse_enter( event, self._item_at( x, y ) )

    #-- Private Methods --------------------------------------------------------

    def _mouse_enter ( self, event, item ):
        if item is not self.mouse_item:
            self._mouse_leave( event )
            self._item_event_for( item, 'enter', event )
            self.mouse_item = item


    def _mouse_leave ( self, event ):
        """ If there is a current mouse item, send it a mouse 'leave' event.
        """
        self._item_event_for( self.mouse_item, 'leave', event )
        self.mouse_item = None


    def _item_event_for ( self, item, name, event ):
        """ Handles routing an *event* called *name* for the specified *item*.
        """
        if item is not None:
            name, event.name = event.name, name
            self._route_event(
                self._handler_for(
                    item, getattr( item, 'state', 'normal' ), event.name
                ),
                event
            )
            event.name = name


    def _item_at ( self, x, y ):
        """ Returns the topmost canvas item (if any) containing the point
            specified by (*x*,*y*).
        """
        return (inn( self.canvas ).item_at( x, y ) or self.canvas)

#-------------------------------------------------------------------------------
#  '_DrawableCanvasEditor' class:
#-------------------------------------------------------------------------------

class _DrawableCanvasEditor ( Editor ):
    """ Defines an editor that displays a DrawableCanvas object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Indicate the editor is scrollable:
    scrollable = True

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._control = DrawableCanvasControl(
            parent = parent,
            theme  = self.factory.theme
        )
        self.adapter = self._control()

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        self._control.canvas = self.value

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:theme' )
    def _theme_modified ( self ):
        self._control.theme = self.factory.theme

#-------------------------------------------------------------------------------
#  Create the editor factory object:
#-------------------------------------------------------------------------------

class DrawableCanvasEditor ( BasicEditorFactory ):
    """ Editor factory for drawable canvas editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the Editor class to be instantiated:
    klass = _DrawableCanvasEditor

    # The theme to use for displaying the content:
    theme = ATheme( facet_value = True )

#-- EOF ------------------------------------------------------------------------
