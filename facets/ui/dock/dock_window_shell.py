"""
Defines the DockWindowShell class used to house drag and drag DockWindow
items that are dropped on the desktop or on the DockWindowShell window.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Control, toolkit

from facets.ui.colors \
    import WindowColor

from facets.ui.ui_facets \
    import image_for

from dock_constants \
    import DOCK_RIGHT

from dock_window \
    import DockWindow

from dock_sizer \
    import DockSizer

from dock_control \
    import DockControl

from dock_region \
    import DockRegion

from dock_section \
    import DockSection

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# DockWindowShell frame icon:
FrameIcon = image_for( '@facets:shell.ico' ).create_icon()

# DockWindowShell window style:
shell_style = set( [ 'frame', 'resizable', 'min_max', 'float' ] )

#-------------------------------------------------------------------------------
#  'DockWindowShell' class:
#-------------------------------------------------------------------------------

class DockWindowShell ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The adapted toolkit window which is the actual shell:
    control = Instance( Control )

    # The DockWindow object contained inside this shell:
    dock_window = Instance( DockWindow )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, dock_control, use_mouse = False, **facets ):
        """ Initializes the object.
        """
        super( DockWindowShell, self ).__init__( **facets )

        control      = dock_control.control
        self.control = shell = toolkit().create_frame( control.root_parent(),
                                   shell_style, dock_control.name )
        shell.icon             = FrameIcon
        shell.background_color = WindowColor

        shell.set_event_handler( close = self._on_close )

        theme = dock_control.theme
        self.dock_window = dw = DockWindow(
            shell,
            auto_close = True,
            theme      = theme ).set(
            style      = 'tab'
        )

        shell.layout = layout = toolkit().create_box_layout()
        layout.add( dw.control, stretch = 1, fill = True )

        if use_mouse:
            x, y = shell.mouse_position
        else:
            x, y = dock_control.control.screen_position

        dx, dy = control.size
        tis    = theme.tab.image_slice
        tc     = theme.tab.content
        tdy    = theme.tab_active.image_slice.dy
        dx    += (tis.xleft + tc.left + tis.xright  + tc.right)
        dy    += (tis.xtop  + tc.top  + tis.xbottom + tc.bottom + tdy)

        self.add_control( dock_control )

        # Set the correct window size and position, accounting for the tab size
        # and window borders:
        shell.bounds  = ( x, y, dx, dy )
        cdx, cdy      = shell.client_size
        ex_dx         = dx - cdx
        ex_dy         = dy - cdy
        shell.bounds  = ( x - (ex_dx / 2) - tis.xleft - tc.left,
                          y - ex_dy + (ex_dx / 2) - tdy - tis.xtop - tc.top,
                          dx + ex_dx, dy + ex_dy )
        shell.visible = True


    def add_control ( self, dock_control ):
        """ Adds a new DockControl to the shell window.
        """
        dock_window = self.dock_window
        dw          = dock_window.control
        dockable    = dock_control.dockable

        # If the current DockControl should be closed, then do it:
        close = dockable.dockable_should_close()
        if close:
            dock_control.close( force = True )

        # Create the new control:
        control = dockable.dockable_get_control( dw )

        # If the DockControl was closed, then reset it to point to the new
        # control:
        if close:
            dock_control.set( control = control, style = 'tab' )
        else:
            # Create a DockControl to describe the new control:
            dock_control = DockControl( control   = control,
                                        name      = dock_control.name,
                                        export    = dock_control.export,
                                        style     = 'tab',
                                        image     = dock_control.image,
                                        closeable = True )

        # Finish initializing the DockControl:
        dockable.dockable_init_dockcontrol( dock_control )

        # Get the current layout adapter (if any):
        dock_sizer = dock_window.dock_sizer
        if dock_sizer is None:
            # Create the initial DockSizer:
            dock_window.dock_sizer = DockSizer( DockSection(
                  contents = [ DockRegion( contents = [ dock_control ] ) ] ) )
        else:
            # DockSizer already exists, try to add the DockControl as a new
            # notebook tab. If the user has reorganized the layout, then just
            # dock it on the right side somewhere:
            section = dock_sizer.contents
            region  = section.contents[0]
            if isinstance( region, DockRegion ):
                region.add( dock_control )
            else:
                section.add( dock_control, region, DOCK_RIGHT )

            # Force the control to update its layout:
            dw.update()

    #-- Control Event Handlers -------------------------------------------------

    def _on_close ( self, event ):
        """ Handles the user attempting to close the window.
        """
        section = self.dock_window.dock_sizer.contents
        n       = len( section.contents )

        # Try to close each individual control:
        for control in section.get_controls():
            control.close( layout = False )

        # If some, but not all, were closed, make sure the window gets updated:
        if 0 < len( section.contents ) < n:
            self.dock_window.control.update()

#-- EOF ------------------------------------------------------------------------