"""
Defines the View class used to represent the structural content of a
    Facets-based user interface.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Str, Int, Float, Bool, Instance, List, Tuple, Any, Callable, Event, \
           Enum

from view_element \
    import ViewElement, ViewSubElement

from ui \
    import UI

from ui_facets \
    import SequenceTypes, AKind, ATheme, AnObject, EditorStyle, DockStyle, \
           Image, ExportType, HelpId, Buttons, ViewStatus

from handler \
    import Handler, default_handler

from group \
    import Group

from item \
    import Item

from include \
    import Include

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Name of the view facet:
AnId = Str( desc = 'the name of the view' )

# Contents of the view facet (i.e., a single Group object):
Content = Instance( Group, desc = 'the content of the view' )

# An optional model/view factory for converting the model into a viewable
# 'model_view' object
AModelView = Callable( desc = 'the factory function for converting a model '
                              'into a model/view object' )

# Reference to a Handler object facet:
AHandler = Any( desc = 'the handler for the view' )

# Dialog window title facet:
ATitle = Str( desc = 'the window title for the view' )

# Dialog window icon facet
#icon_facet = Instance( 'facets.ui.pyface.image_resource.ImageResource',
#                     desc = 'the ImageResource of the icon file for the view' )

# Apply changes handler:
OnApply = Callable( desc = 'the routine to call when modal changes are applied '
                           'or reverted' )

# Is the dialog window resizable?
IsResizable = Bool( False, desc = 'whether dialog can be resized or not' )

# Is the view scrollable?
IsScrollable = Bool( False, desc = 'whether view should be scrollable or not' )

# The valid categories of imported elements that can be dragged into the view:
ImportTypes = List( Str, desc = 'the categories of elements that can be '
                                'dragged into the view' )

# The view position and size facets:
Unspecified = -1E6
Width       = Float( Unspecified, desc = 'the width of the view window' )
Height      = Float( Unspecified, desc = 'the height of the view window' )
XCoordinate = Float( Unspecified, desc = 'the x coordinate of the view window' )
YCoordinate = Float( Unspecified, desc = 'the y coordinate of the view window' )

# The view popup bounds:
Bounds = Tuple( Int, Int, Int, Int )

# The result that should be returned if the user clicks the window or dialog
# close button or icon
CloseResult = Enum( None, True, False,
                    desc = 'the result to return when the user clicks the '
                           'window or dialog close button or icon' )

# The KeyBindings facet:
AKeyBindings = Instance( 'facets.ui.key_bindings.KeyBindings',
                         desc = 'the global key bindings for the view' )

#-------------------------------------------------------------------------------
#  'View' class:
#-------------------------------------------------------------------------------

class View ( ViewElement ):
    """ A Facets-based user interface for one or more objects.

        The attributes of the View object determine the contents and layout of
        an attribute-editing window. A View object contains a set of Group,
        Item, and Include objects. A View object can be an attribute of an
        object derived from HasFacets, or it can be a standalone object.
    """

    #-- Facet Definitions ------------------------------------------------------

    # A unique identifier for the view:
    id = AnId

    # The top-level Group object for the view:
    content = Content

    # The menu bar for the view. Usually requires a custom **handler**:
    menubar = Any # Instance( facets.ui.pyface.action.MenuBarManager )

    # The toolbar for the view. Usually requires a custom **handler**:
    toolbar = Any # Instance( facets.ui.pyface.action.ToolBarManager )

    # Status bar items to add to the view's status bar. The value can be:
    #
    #   - **None**: No status bar for the view (the default).
    #   - string: Same as [ StatusItem( name = string ) ].
    #   - StatusItem: Same as [ StatusItem ].
    #   - [ [StatusItem|string], ... ]: Create a status bar with one field for
    #     each StatusItem in the list (or tuple). The status bar fields are
    #     defined from left to right in the order specified. A string value is
    #     converted to: StatusItem( name = string ):
    statusbar = ViewStatus

    # List of button actions to add to the view. The
    # **facets.ui.menu** module defines standard buttons, such as
    # **OKButton**, and standard sets of buttons, such as **ModalButtons**,
    # which can be used to define a value for this attribute. This value can
    # also be a list of button name strings, such as ``['OK', 'Cancel',
    # 'Help']``. If set to the empty list, the view contains a default set of
    # buttons (equivalent to **LiveButtons**: Undo/Redo, Revert, OK, Cancel,
    # Help). To suppress buttons in the view, use the **NoButtons** variable,
    # defined in **facets.ui.menu**.
    buttons = Buttons

    # The set of global key bindings for the view. Each time a key is pressed
    # while the view has keyboard focus, the key is checked to see if it is one
    # of the keys recognized by the KeyBindings object. If it is, the matching
    # KeyBinding's method name is checked to see if it is defined on any of the
    # object's in the view's context. If it is, the method is invoked. If the
    # result of the method is **False**, then the search continues with the
    # next object in the context. If any invoked method returns a non-False
    # value, processing stops and the key is marked as having been handled. If
    # all invoked methods return **False**, or no matching KeyBinding object is
    # found, the key is processed normally. If the view has a non-empty *id*
    # facet, the contents of the **KeyBindings** object will be saved as part
    # of the view's persistent data:
    key_bindings = AKeyBindings

    # The Handler object that provides GUI logic for handling events in the
    # window. Set this attribute only if you are using a custom Handler. If
    # not set, the default Facets UI Handler is used.
    handler = AHandler

    # The factory function for converting a model into a model/view object:
    model_view = AModelView

    # Title for the view, displayed in the title bar when the view appears as a
    # secondary window (i.e., dialog or wizard). If not specified, "Edit
    # properties" is used as the title.
    title = ATitle

    # The name of the icon to display in the dialog window title bar:
    icon = Any

    # The kind of user interface to create:
    kind = AKind

    # The default object being edited:
    object = AnObject

    # The default editor style of elements in the view:
    style = EditorStyle

    # The default docking style to use for sub-groups of the view. The following
    # values are possible:
    #
    # * 'fixed': No rearrangement of sub-groups is allowed.
    # * 'horizontal': Moveable elements have a visual "handle" to the left by
    #   which the element can be dragged.
    # * 'vertical': Moveable elements have a visual "handle" above them by
    #   which the element can be dragged.
    # * 'tabbed': Moveable elements appear as tabbed pages, which can be
    #   arranged within the window or "stacked" so that only one appears at
    #   at a time.
    dock = DockStyle

    # The image to display on notebook tabs:
    image = Image

    # Called when modal changes are applied or reverted:
    on_apply = OnApply

    # Can the user resize the window?
    resizable = IsResizable

    # Can the user scroll the view? If set to True, window-level scroll bars
    # appear whenever the window is too small to show all of its contents at
    # one time. If set to False, the window does not scroll, but individual
    # widgets might still contain scroll bars.
    scrollable = IsScrollable

    # The category of exported elements:
    export = ExportType

    # The valid categories of imported elements:
    imports = ImportTypes

    # External help context identifier, which can be used by a custom help
    # handler. This attribute is ignored by the default help handler.
    help_id = HelpId

    # Requested x-coordinate (horizontal position) for the view window. This
    # attribute can be specified in the following ways:
    #
    # * A positive integer: indicates the number of pixels from the left edge
    #   of the screen to the left edge of the window.
    # * A negative integer: indicates the number of pixels from the right edge
    #   of the screen to the right edge of the window.
    # * A floating point value between 0 and 1: indicates the fraction of the
    #   total screen width between the left edge of the screen and the left edge
    #   of the window.
    # * A floating point value between -1 and 0: indicates the fraction of the
    #   total screen width between the right edge of the screen and the right
    #   edge of the window.
    x = XCoordinate

    # Requested y-coordinate (vertical position) for the view window. This
    # attribute behaves exactly like the **x** attribute, except that its value
    # indicates the position of the top or bottom of the view window relative
    # to the top or bottom of the screen.
    y = YCoordinate

    # Requested width for the view window, as an (integer) number of pixels, or
    # as a (floating point) fraction of the screen width.
    width = Width

    # Requested height for the view window, as an (integer) number of pixels, or
    # as a (floating point) fraction of the screen height.
    height = Height

    # The absolute screen bounds of the region a popup-style view should be
    # displayed relative to. The value is in the form: ( x, y, dx, dy ) (Not
    # used if the view is not a popup-style view):
    popup_bounds = Bounds

    # Class of dropped objects that can be added:
    drop_class = Any

    # Event when the view has been updated:
    updated = Event

    # What result should be returned if the user clicks the window or dialog
    # close button or icon?
    close_result = CloseResult

    # The default theme to use for a contained item:
    item_theme = ATheme

    # The default theme to use for a contained item's label:
    label_theme = ATheme

    # Note: Group objects delegate their 'object' and 'style' facets to the View

    # Should the view support undo/redo operations?
    undo = Bool( True )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, *values, **facets ):
        """ Initializes the object.
        """
        ViewElement.__init__( self, **facets )
        self.set_content( *values )


    def set_content ( self, *values ):
        """ Sets the content of a view.
        """
        content = []
        accum   = []
        for value in values:
            if isinstance( value, ViewSubElement ):
                content.append( value )
            elif type( value ) in SequenceTypes:
                content.append( Group( * value ) )
            elif (isinstance( value, basestring ) and
                 (value[:1] == '<') and (value[-1:] == '>')):
                # Convert string to an Include value:
                content.append( Include( value[1:-1].strip() ) )
            else:
                content.append( Item( value ) )

        # If there are any 'Item' objects in the content, wrap the content in a
        # Group:
        for item in content:
            if isinstance( item, Item ):
                content = [ Group( *content ) ]
                break

        # Wrap all of the content up into a Group and save it as our content:
        self.content = Group( container = self, *content )


    def ui ( self, context, parent        = None, kind       = None,
                            view_elements = None, handler    = None,
                            id            = '',   scrollable = None,
                            args          = None ):
        """ Creates a **UI** object, which generates the actual GUI window or
            panel from a set of view elements.

            Parameters
            ----------
            context : object or dictionary
                A single object or a dictionary of string/object pairs, whose
                facet attributes are to be edited. If not specified, the current
                object is used.
            parent : window component
                The window parent of the View object's window
            kind : string
                The kind of window to create. See the **AKind** facet for
                details. If *kind* is unspecified or None, the **kind**
                attribute of the View object is used.
            view_elements : ViewElements object
                The set of Group, Item, and Include objects contained in the
                view. Do not use this parameter when calling this method
                directly.
            handler : Handler object
                A handler object used for event handling in the dialog box. If
                None, the default handler for Facets UI is used.
            id : string
                A unique ID for persisting preferences about this user
                interface, such as size and position. If not specified, no user
                preferences are saved.
            scrollable : Boolean
                Indicates whether the dialog box should be scrollable. When set
                to True, scroll bars appear on the dialog box if it is not large
                enough to display all of the items in the view at one time.

        """
        handler = handler or self.handler or default_handler()
        if not isinstance( handler, Handler ):
            handler = handler()

        if args is not None:
            handler.set( **args )

        if not isinstance( context, dict ):
            context = context.facet_context()

        context.setdefault( 'handler', handler )
        handler = context[ 'handler' ]

        if self.model_view is not None:
            context[ 'object' ] = self.model_view( context[ 'object' ] )

        self_id = self.id
        if self_id != '':
            if id != '':
                id = '%s:%s' % ( self_id, id )
            else:
                id = self_id

        if scrollable is None:
            scrollable = self.scrollable

        if kind is None:
            kind = self.kind

        ui = UI(
            view          = self,
            context       = context,
            handler       = handler,
            view_elements = view_elements,
            title         = self.title,
            id            = id,
            kind          = kind,
            scrollable    = scrollable
        )

        ui.ui( parent )

        return ui


    def replace_include ( self, view_elements ):
        """ Replaces any items that have an ID with an Include object with
            the same ID, and puts the object with the ID into the specified
            ViewElements object.
        """
        if self.content is not None:
            self.content.replace_include( view_elements )


    def __repr__ ( self ):
        """ Returns a "pretty print" version of the View.
        """
        return self._repr_format( self.content.content, 'title', 'id', 'kind',
            'resizable', 'scrollable', 'x', 'y', 'width', 'height'
        )

#-- EOF ------------------------------------------------------------------------