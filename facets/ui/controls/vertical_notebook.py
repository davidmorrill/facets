"""
Defines a GUI toolkit independent VerticalNotebook class for displaying a series
of pages organized vertically, as opposed to horizontally like a standard
notebook.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, Instance, List, Str, Bool, Property, \
           Any, Control, UI, Theme, cached_property, implements

from facets.ui.ui_facets \
    import ATheme

from facets.ui.editor \
    import Editor

from facets.ui.toolkit \
    import toolkit

from facets.ui.constants \
    import screen_dy

from facets.ui.i_abstract_layout \
    import IAbstractLayout

from facets.ui.adapters.abstract_adapter \
    import AbstractAdapter

from image_panel \
    import ImagePanel

from themed_control \
    import ThemedControl

#-------------------------------------------------------------------------------
#  'ThemedPage' class:
#-------------------------------------------------------------------------------

class ThemedPage ( HasPrivateFacets ):
    """ A class representing a themed page within a notebook.
    """

    #-- Public Facets ----------------------------------------------------------

    # The name of the page (displayed on its 'tab') [Set by client]:
    name = Str

    # The optional Facets UI associated with this page [Set by client]:
    ui = Instance( UI )

    # The adapted control the page represents [Set by client]:
    control = Instance( AbstractAdapter )

    # Optional client data associated with the page [Set/Get by client]:
    data = Any

    # The optional object defining the page name [Set by client]:
    object = Instance( HasFacets )

    # The name of the object facet that signals a page name change [Set by
    # client]:
    facet_name = Str

    # The parent window for the client page [Get by client]:
    parent = Property

    #-- Facets for use by the Notebook/Sizer -----------------------------------

    # The current open status of the notebook page:
    is_open = Bool( False )

    # The minimum size for the page:
    min_size = Property

    # The open size property for the page:
    open_size = Property

    # The closed size property for the page:
    closed_size = Property

    #-- Private Facets ---------------------------------------------------------

    # The notebook this page is associated with:
    notebook = Instance(
                    'facets.ui.controls.vertical_notebook.VerticalNotebook' )

    # The theme used to display a closed page:
    closed_theme = ATheme

    # The theme use to display an open page:
    open_theme = ATheme

    # The control representing the closed page:
    closed_page = Property( depends_on = 'closed_theme' )

    # The control representing the open page:
    open_page = Property( depends_on = 'open_theme' )

    #-- Public Methods ---------------------------------------------------------

    def close ( self ):
        """ Closes the notebook page.
        """
        if self.object is not None:
            self.object.on_facet_set( self._name_updated, self.facet_name,
                                      remove = True )
            self.object = None

        if self.ui is not None:
            self.ui.dispose()
            self.ui = None

        if self.closed_page is not None:
            self.closed_page.control.destroy()
            self.open_page.control.destroy()
            self.control = None


    def set_size ( self, x, y, dx, dy ):
        """ Sets the size of the current active page.
        """
        if self.is_open:
            self.open_page.control.bounds = ( x, y, dx, dy )
        else:
            self.closed_page.control.bounds = ( x, y, dx, dy )


    def register_name_listener ( self, object, facet_name ):
        """ Registers a listener on the specified object facet for a page name
            change.
        """
        # Save the information, so we can unregister it later:
        self.object, self.facet_name = object, facet_name

        # Register the listener:
        object.on_facet_set( self._name_updated, facet_name )

        # Make sure the name gets initialized:
        self._name_updated()

    #-- Property Implementations -----------------------------------------------

    def _get_min_size ( self ):
        """ Returns the minimum size for the page.
        """
        dxo, dyo = self.open_page.best_size
        dxc, dyc = self.closed_page.best_size
        if self.is_open:
            return ( max( dxo, dxc ), dyo )

        return ( max( dxo, dxc ), dyc )


    def _get_open_size ( self ):
        """ Returns the open size for the page.
        """
        return self.open_page.best_size


    def _get_closed_size ( self ):
        """ Returns the closed size for the page.
        """
        return self.closed_page.best_size


    @cached_property
    def _get_closed_page ( self ):
        """ Returns the 'closed' form of the notebook page.
        """
        result = ThemedControl(
            theme      = self.closed_theme,
            text       = self.name,
            controller = self,
            alignment  = 'center',
            state      = 'closed',
            parent     = self.notebook.control
        )

        # Make sure the underlying control has been created:
        result()

        return result


    @cached_property
    def _get_open_page ( self ):
        """ Returns the 'open' form of the notebook page.
        """
        result = ImagePanel(
            theme             = self.open_theme,
            text              = self.name,
            controller        = self,
            default_alignment = 'center',
            state             = 'open',
            parent            = self.notebook.control
        )

        # Make sure the underlying control has been created:
        result()

        return result


    def _get_parent ( self ):
        """ Returns the parent window for the client's window.
        """
        return self.open_page.control

    #-- Facet Event Handlers ---------------------------------------------------

    def _ui_set ( self, ui ):
        """ Handles the ui facet being changed.
        """
        if ui is not None:
            self.control = ui.control


    def _control_set ( self, control ):
        """ Handles the control for the page being changed.
        """
        if control is not None:
            self.open_page.control.layout.add( control, stretch = 1 )
            self._is_open_set( self.is_open )


    def _is_open_set ( self, is_open ):
        """ Handles the 'is_open' state of the page being changed.
        """
        self.closed_page.control.visible = (not is_open)
        self.open_page.control.visible   = is_open

        if is_open:
            self.closed_page.control.size = ( 0, 0 )
        else:
            self.open_page.control.size   = ( 0, 0 )


    def _name_set ( self ):
        """ Handles the name facet being changed.
        """
        self.closed_page.text = self.open_page.text = self.name


    def _name_updated ( self ):
        """ Handles a signal that the associated object's page name has changed.
        """
        nb           = self.notebook
        handler_name = None

        method = None
        editor = nb.editor
        if editor is not None:
            method = getattr( editor.ui.handler,
                 '%s_%s_page_name' % ( editor.object_name, editor.name ), None )

        if method is not None:
            handler_name = method( editor.ui.info, self.object )

        if handler_name is not None:
            self.name = handler_name
        else:
            self.name = getattr( self.object, self.facet_name ) or '???'

    #-- ThemedControl Mouse Event Handlers -------------------------------------

    def open_left_down ( self, x, y, event ):
        """ Handles the user clicking on an open notebook page to close it.
        """
        if not self.notebook.double_click:
            self.notebook.close( self )


    def open_left_dclick ( self, x, y, event ):
        """ Handles the user double clicking on an open notebook page to close
            it.
        """
        if self.notebook.double_click:
            self.notebook.close( self )


    def open_right_down ( self, x, y, event ):
        """ Handles the user right clicking on an open notebook page to open it
            in 'solo' mode.
        """
        self.closed_right_down( x, y, event )


    def open_right_dclick ( self, x, y, event ):
        """ Handles the user right double clicking on an open notebook page to
            open it in 'solo' mode.
        """
        self.closed_right_dclick( x, y, event )


    def closed_left_down ( self, x, y, event ):
        """ Handles the user clicking on a closed notebook page to open it.
        """
        if not self.notebook.double_click:
            self.notebook.open( self )


    def closed_left_dclick ( self, x, y, event ):
        """ Handles the user double clicking on a closed notebook page to open
            it.
        """
        if self.notebook.double_click:
            self.notebook.open( self )


    def closed_right_down ( self, x, y, event ):
        """ Handles the user right clicking on a closed notebook page to open
            it in 'solo' mode.
        """
        if not self.notebook.double_click:
            self.notebook.open( self, True )


    def closed_right_dclick ( self, x, y, event ):
        """ Handles the user right double clicking on a closed notebook page to
            open it in 'solo' mode.
        """
        if self.notebook.double_click:
            self.notebook.open( self, True )

#-------------------------------------------------------------------------------
#  'VerticalNotebook' class:
#-------------------------------------------------------------------------------

class VerticalNotebook ( HasPrivateFacets ):
    """ Defines a VerticalNotebook class for displaying a series of pages
        organized vertically, as opposed to horizontally like a standard
        notebook.
    """

    #-- Public Facets ----------------------------------------------------------

    # The theme to use for 'closed' notebook pages:
    closed_theme = ATheme( Theme( '@facets:tab_gradient7?H55l2S14',
                                  label = ( 5, 5, 1, 0 ) ) )

    # The theme to use for 'open' notebook pages:
    open_theme = ATheme( Theme( '@xform:nb?L14~L40s|H44',
                                content = 0, label = ( 5, 5, 0, 1 ) ) )

    # Allow multiple open pages at once?
    multiple_open = Bool( False )

    # Should the notebook be scrollable?
    scrollable = Bool( False )

    # Use double clicks (True) or single clicks (False) to open/close pages:
    double_click = Bool( False )

    # The pages contained in the notebook:
    pages = List( ThemedPage )

    # The facets UI editor this notebook is associated with (if any):
    editor = Instance( Editor )

    # The layout manager for this notebook:
    layout = Instance(
                 'facets.ui.controls.vertical_notebook.VerticalNotebookLayout' )

    #-- Private Facets ---------------------------------------------------------

    # The adapted control used to represent the notebook:
    control = Instance( Control )

    #-- Public Methods ---------------------------------------------------------

    def create_control ( self, parent ):
        """ Creates the underlying window used for the notebook.
        """
        # Create the correct type of window based on whether or not it should
        # be scrollable:
        root = parent
        if self.scrollable:
            root = toolkit().create_scrolled_panel( parent )

        self.control = control = toolkit().create_panel( root )
        control._image_slice   = getattr( parent, '_image_slice', None )
        self.layout            = VerticalNotebookLayout( notebook = self )

        # Set up the painting event handler:
        control.set_event_handler( paint = self._paint )

        if root is parent:
            return control

        root.content = control

        return root


    def create_page ( self ):
        """ Creates a new **ThemedPage** object representing a notebook page and
            returns it as the result.
        """
        return ThemedPage( notebook     = self ).set(
                           closed_theme = self.closed_theme,
                           open_theme   = self.open_theme )


    def open ( self, page, solo = False ):
        """ Handles opening a specified **ThemedPage** notebook page.
        """
        if (page is not None) and (solo or (not page.is_open)):
            if solo or (not self.multiple_open):
                for a_page in self.pages:
                    a_page.is_open = False

            page.is_open = True

            self._refresh()


    def close ( self, page ):
        """ Handles closing a specified **ThemedPage** notebook page.
        """
        if (page is not None) and page.is_open:
            page.is_open = False
            self._refresh()

    #-- Facet Event Handlers ---------------------------------------------------

    def _pages_set ( self, old, new ):
        """ Handles the notebook's pages being changed.
        """
        for page in old:
            page.close()

        self._refresh()


    def _pages_items_set ( self, event ):
        """ Handles some of the notebook's pages being changed.
        """
        for page in event.removed:
            page.close()

        self._refresh()


    def _multiple_open_set ( self, multiple_open ):
        """ Handles the 'multiple_open' flag being changed.
        """
        if not multiple_open:
            first = True
            for page in self.pages:
                if first and page.is_open:
                    first = False
                else:
                    page.is_open = False

        self._refresh()


    def _layout_set ( self, layout ):
        """ Handles the 'layout' facet being changed by linking the
            underlying toolkit specific control and layout objects together.
        """
        self.control.layout = toolkit().layout_adapter_for( layout )

    #-- Control Event Handlers -------------------------------------------------

    def _paint ( self, event ):
        """ Paint the background using the associated ImageSlice object.
        """
        self.control.graphics_buffer.copy()

    #-- Private Methods --------------------------------------------------------

    def _refresh ( self ):
        """ Refresh the layout and contents of the notebook.
        """
        control = self.control
        if control is not None:
            # Set the virtual size of the canvas (so scroll bars work right):
            layout = self.layout
            if control.size[0] == 0:
                control.size = layout.calculate_initial()

            control.virtual_size = layout.calculate_minimum()
            control.update()

#-------------------------------------------------------------------------------
#  'VerticalNotebookLayout' class:
#-------------------------------------------------------------------------------

class VerticalNotebookLayout ( HasPrivateFacets ):
    """ Defines a sizer that correctly sizes a themed vertical notebook's
        children to implement the vertical notebook UI model.
    """

    implements( IAbstractLayout )

    #-- Facet Definitions ------------------------------------------------------

    # The notebook for which this is the layout manager:
    notebook = Instance( VerticalNotebook )

    # The GUI toolkit specific layout manager associated with this layout
    # manager (part of the IAbstractLayout interface):
    layout = Any

    #-- Public Methods ---------------------------------------------------------

    def calculate_initial ( self ):
        """ Calculates a reasonable initial size of the control by aggregating
            the sizes of the open and closed pages.
        """
        tdx, tdy = 0, 0
        open_dy  = closed_dy = 0
        for page in self.notebook.pages:
            dxo, dyo = page.open_size
            dxc, dyc = page.closed_size
            tdx      = max( tdx, dxo, dxc )
            if dyo > open_dy:
                tdy += ( dyo - open_dy + closed_dy )
                open_dy, closed_dy = dyo, dyc
            else:
                tdy += dyc

        return ( tdx, min( tdy, screen_dy / 2 ) )

    #-- IAbstractLayout Interface Implementation -------------------------------

    def calculate_minimum ( self ):
        """ Calculates the minimum size needed by the sizer.
        """
        tdx, tdy = 0, 0
        for page in self.notebook.pages:
            dx, dy = page.min_size
            tdx    = max( tdx, dx )
            tdy   += dy

        return ( tdx, tdy )


    def perform_layout ( self, x, y, tdx, tdy ):
        """ Layout the contents of the sizer based on the sizer's current size
            and position.
        """
        cdy = ody = 0
        for page in self.notebook.pages:
            dx, dy = page.min_size
            if page.is_open:
                ody += dy
            else:
                cdy += dy

        ady = max( 0, tdy - cdy )

        for page in self.notebook.pages:
            dx, dy = page.min_size
            if page.is_open:
                ndy  = ( ady * dy ) / ody
                ady -= ndy
                ody -= dy
                dy   = ndy

            page.set_size( x, y, tdx, dy )
            y += dy

#-- EOF ------------------------------------------------------------------------