"""
Defines the stub functions used for creating concrete implementations of
the standard EditorFactory subclasses supplied with the Facets package.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from facets.core_api \
    import HasPrivateFacets, FacetError

from facets.core.facets_config \
    import facets_config

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# List of implemented UI toolkits:
FacetUIToolkits = [ 'qt4', 'side', 'wx', 'null' ]

#-------------------------------------------------------------------------------
#  Data:
#-------------------------------------------------------------------------------

# The current GUI toolkit object being used:
_toolkit = None

#-------------------------------------------------------------------------------
#  Low-level GUI toolkit selection function:
#-------------------------------------------------------------------------------

def _import_toolkit ( name ):
    module = __import__( 'facets.ui.%s.toolkit' % name )

    return getattr( module.ui, name ).toolkit.GUIToolkit()


def toolkit_object ( name ):
    """ Return the toolkit specific object with the given name.  The name
        consists of the relative module path and the object name separated by a
        colon.
    """

    mname, oname = name.split( ':' )

    class Unimplemented ( object ):
        """ This is returned if an object isn't implemented by the selected
            toolkit.  It raises an exception if it is ever instantiated.
        """

        def __init__ ( self, *args, **kwargs ):
            raise NotImplementedError(
                "The %s facets backend doesn't implement %s" %
                ( facets_config.toolkit, oname )
            )

    be_obj   = Unimplemented
    be_mname = toolkit().__module__.rstrip( '.toolkit' ) + '.' + mname

    try:
        __import__( be_mname )
        try:
            be_obj = getattr( sys.modules[ be_mname ], oname )
        except AttributeError:
            pass

    except ImportError:
        pass

    return be_obj


def toolkit ( *toolkits ):
    """ Selects and returns a low-level GUI toolkit.

        Use this function to get a reference to the current toolkit.
    """

    global _toolkit

    # If _toolkit has already been set, simply return it:
    if _toolkit is not None:
        return _toolkit

    # If a toolkit has already been set for facets_config, then check if we can
    # use it:
    if facets_config.toolkit:
        toolkits = ( facets_config.toolkit, )
    elif len( toolkits ) == 0:
        toolkits = FacetUIToolkits

    for toolkit_name in toolkits:
        try:
            _toolkit = _import_toolkit( toolkit_name )

            # In case we have just decided on a toolkit, tell everybody else:
            facets_config.toolkit = toolkit_name

            return _toolkit

        except ImportError:
            import traceback
            traceback.print_exc()
    else:
        # Try using the null toolkit and printing a warning:
        try:
            _toolkit = _import_toolkit( 'null' )

            import warnings
            warnings.warn(
                "Unable to import the '%s' backend for facets UI; using the "
                "'null' toolkit instead." % toolkit_name
            )

            return _toolkit

        except ImportError:
            raise FacetError(
                "Could not find any UI toolkit called '%s'" % toolkit_name
            )

#-------------------------------------------------------------------------------
#  'Toolkit' class (abstract base class):
#-------------------------------------------------------------------------------

class Toolkit ( HasPrivateFacets ):
    """ Abstract base class for GUI toolkits.
    """

    def ui_wizard ( self, ui, parent ):
        """ Creates a GUI-toolkit-specific wizard dialog user interface using
            information from the specified UI object.
        """
        raise NotImplementedError


    def show_help ( self, ui, control ):
        """ Shows a Help window for a specified UI and control.
        """
        raise NotImplementedError


    def key_event_to_name ( self, event ):
        """ Converts a keystroke event into a corresponding key name.
        """
        raise NotImplementedError


    def hook_events ( self, ui, control, events = None, handler = None ):
        """ Hooks all specified events for all controls in a UI so that they
            can be routed to the correct event handler.
        """
        raise NotImplementedError


    def route_event ( self, ui, event ):
        """ Routes a "hooked" event to the corrent handler method.
        """
        raise NotImplementedError


    def event_loop ( self, exit_code = None ):
        """ Enters or exits a user interface event loop. If *exit_code* is
            omitted, a new event loop is started. If *exit_code*, which should
            be an integer, is specified, the most recent event loop started is
            exited with the specified *exit_code* as the result. Control does
            not return from a call to start an event loop until a corresponding
            request to exit an event loop is made. Event loops may be nested.
        """
        raise NotImplementedError


    def image_size ( self, image ):
        """ Returns a (width,height) tuple containing the size of a specified
            toolkit image.
        """
        raise NotImplementedError


    def constants ( self ):
        """ Returns a dictionary of useful constants.

            Currently, the dictionary should have the following key/value pairs:
            - WindowColor': the standard window background color in the toolkit
              specific color format.
        """
        raise NotImplementedError


    def to_toolkit_color ( self, color ):
        """ Returns a specified GUI toolkit neutral color as a toolkit specific
            color object.
        """
        raise NotImplementedError


    def from_toolkit_color ( self, color ):
        """ Returns a toolkit specific color object as a GUI toolkit neutral
            color.
        """
        raise NotImplementedError


    def beep ( self ):
        """ Makes a beep to alert the user to a situation requiring their
            attention.
        """
        raise NotImplementedError


    def screen_size ( self ):
        """ Returns a tuple of the form (width,height) containing the size of
            the user's display.
        """
        raise NotImplementedError


    def screen_info ( self ):
        """ Returns a list of tuples of the form: ( x, y, dx, dy ), which
            describe the available screen area (excluding system managed areas
            like the Mac Dock or Windows launch bar) for all of the system's
            displays. There is one tuple for each display. The first tuple in
            the list is always for the system's primary display.
        """
        raise NotImplementedError


    def screen ( self ):
        """ Returns a Control object representing the entire display.
        """
        raise NotImplementedError


    def scrollbar_size ( self ):
        """ Returns a tuple of the form (width,height) containing the standard
            width of a vertical scrollbar, and the standard height of a
            horizontal scrollbar.
        """
        raise NotImplementedError


    def mouse_position ( self ):
        """ Returns the current mouse position (in screen coordinates) as a
            tuple of the form: (x,y).
        """
        raise NotImplementedError


    def mouse_buttons ( self ):
        """ Returns a set containing the mouse buttons currently being pressed.
            The possible set values are: 'left', 'middle', 'right'.
        """
        raise NotImplementedError


    def control_at ( self, x, y ):
        """ Returns the Control at the specified screen coordinates, or None if
            there is no control at that position.
        """
        raise NotImplementedError


    def is_application_running ( self ):
        """ Returns whether or not the application object has been created and
            is running its event loop.
        """
        raise NotImplementedError


    def run_application ( self, app_info ):
        """ Runs the application described by the *app_info* object as a Facets
            UI modal application.
        """
        raise NotImplementedError


    # fixme: We should be able to delete this after everything is debugged...
    def as_toolkit_adapter ( self, control ):
        """ Returns the GUI toolkit specific control adapter associated with
            *control*.
        """
        raise NotImplementedError


    def clipboard ( self ):
        """ Returns the GUI toolkit specific implementation of the clipboard
            object that implements the Clipboard interface.
        """
        raise NotImplementedError


    def font_names ( self ):
        """ Returns a list containing the names of all available fonts.
        """
        raise NotImplementedError


    def font_fixed ( self, font_name ):
        """ Returns **True** if the font whose name is specified by *font_name*
            is a fixed (i.e. monospace) font. It returns **False** if
            *font_name* is a proportional font.
        """
        raise NotImplementedError

    #-- GUI Toolkit Dependent Facet Definitions --------------------------------

    def color_facet ( self, *args, **facets ):
        raise NotImplementedError


    def rgb_color_facet ( self, *args, **facets ):
        raise NotImplementedError


    def font_facet ( self, *args, **facets ):
        raise NotImplementedError

    #-- 'EditorFactory' Factory Methods ----------------------------------------

    def check_list_editor ( self, *args, **facets ):
        raise NotImplementedError


    def code_editor ( self, *args, **facets ):
        raise NotImplementedError


    def directory_editor ( self, *args, **facets ):
        raise NotImplementedError


    def drop_editor ( self, *args, **facets ):
        raise NotImplementedError


    def enum_editor ( self, *args, **facets ):
        raise NotImplementedError


    def file_editor ( self, *args, **facets ):
        raise NotImplementedError


    def font_editor ( self, *args, **facets ):
        raise NotImplementedError


    def grid_editor ( self, *args, **facets ):
        raise NotImplementedError


    def html_editor ( self, *args, **facets ):
        raise NotImplementedError


    def image_enum_editor ( self, *args, **facets ):
        raise NotImplementedError


    def list_editor ( self, *args, **facets ):
        raise NotImplementedError


    def list_str_editor ( self, *args, **facets ):
        raise NotImplementedError


    def ordered_set_editor ( self, *args, **facets ):
        raise NotImplementedError


    def plot_editor ( self, *args, **facets ):
        raise NotImplementedError


    def tree_editor ( self, *args, **facets ):
        raise NotImplementedError

    #-- Create GUI Toolkit Neutral Common Controls -----------------------------

    def create_application ( self ):
        raise NotImplementedError


    def create_control ( self, parent, tab_stop = False, handle_keys = False ):
        raise NotImplementedError


    def create_frame ( self, parent, style, title = '' ):
        raise NotImplementedError


    def create_panel ( self, parent ):
        raise NotImplementedError


    def create_scrolled_panel ( self, parent ):
        raise NotImplementedError


    def create_label ( self, parent, label = '', align = 'left' ):
        raise NotImplementedError


    def create_text_input ( self, parent, read_only = False, password = False,
                                  handle_enter = False, multi_line = False,
                                  align = 'left' ):
        raise NotImplementedError


    def create_button ( self, parent, label = '' ):
        raise NotImplementedError


    def create_checkbox ( self, parent, label = '' ):
        raise NotImplementedError


    def create_combobox ( self, parent, editable = False ):
        raise NotImplementedError


    def create_heading_text ( self, parent, text = '' ):
        """ Returns an ImageText control for use as a heading.
        """
        from facets.ui.controls.image_text import ImageText

        return ImageText( text = text ).create_control( parent )


    def create_separator ( self, parent, is_vertical = True ):
        raise NotImplementedError

    #-- Create GUI Toolkit Neutral Common Layout Managers ----------------------

    def create_box_layout ( self, is_vertical = True, align = '' ):
        """ Returns a new GUI toolkit neutral 'box' layout manager.
        """
        raise NotImplementedError


    def create_groupbox_layout ( self, is_vertical, parent, label, owner ):
        raise NotImplementedError


    def create_flow_layout ( self, is_vertical ):
        raise NotImplementedError


    def create_grid_layout ( self, rows = 0, columns = 1, v_margin = 0,
                                   h_margin = 0 ):
        """ Returns a new GUI toolkit neutral grid layout manager which
            supports a (rows,columns) sized grid, with each grid element
            having (v_margin,h_margin) pixels of space around it.

            If rows is 0, the number of rows is not predefined, but will be
            determined by the actual number of controls added to the layout.
        """
        raise NotImplementedError

    #-- Create GUI Toolkit Neutral Miscellaneous Objects -----------------------

    def create_bitmap ( self, buffer, width, height ):
        """ Create a GUI toolkit specific bitmap of the specified width and
            height from the specified buffer 'bgra' data in row order.
        """
        raise NotImplementedError


    def create_timer ( self, milliseconds, handler ):
        """ Creates and returns a timer which will call *handler* every
            *milliseconds* milliseconds. The timer can be cancelled by calling
            the returned object with no arguments.
        """
        raise NotImplementedError

    #-- GUI Toolkit Neutral Adapter Methods ------------------------------------

    def adapter_for ( self, item ):
        """ Returns the correct type of adapter (control or layout) for the
            specified item.
        """
        raise NotImplementedError


    def control_adapter_for ( self, control ):
        """ Returns the GUI toolkit neutral adapter for the specified GUI
            toolkit specific control.
        """
        raise NotImplementedError


    def layout_adapter_for ( self, layout ):
        """ Returns the GUI toolkit neutral adapter for the specified GUI
            toolkit specific layout manager.
        """
        raise NotImplementedError

#-- EOF ------------------------------------------------------------------------
