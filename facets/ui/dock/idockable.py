"""
Defines the IDockable interface which objects contained in a DockWindow
DockControl can implement in order to allow themselves to be dragged into
a different DockWindow.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Interface, implements

#-------------------------------------------------------------------------------
#  'IDockable' interface:
#-------------------------------------------------------------------------------

class IDockable ( Interface ):

    #-- IDockable Interface ----------------------------------------------------

    def dockable_should_close ( self ):
        """ Should the current DockControl be closed before creating the new
            one.
        """


    def dockable_close ( self, dock_control, force ):
        """ Returns whether or not it is OK to close the control, and if it is
            OK, then it closes the DockControl itself.
        """


    def dockable_get_control ( self, parent ):
        """ Gets a control that can be docked into a DockWindow.
        """


    def dockable_init_dockcontrol ( self, dock_control ):
        """ Allows the object to override the default DockControl settings.
        """


    def dockable_menu ( self, dock_control, event ):
        """ Returns the right-click popup menu for a DockControl (if any).
        """


    def dockable_dclick ( self, dock_control, event ):
        """ Handles the user double-clicking on the DockControl.
            A result of False indicates the event was not handled; all other
            results indicate that the event was handled successfully.
        """


    def dockable_tab_activated ( self, dock_control, activated ):
        """ Handles a notebook tab being activated or deactivated.

            'dock_control' is the control being activated or deactivated.

            If 'activated' is True, the control is being activated; otherwise
            the control is being deactivated.
        """


    def dockable_bind ( self, dock_control ):
        """ Handles the dockable being bound to a specified DockControl.
        """

#-------------------------------------------------------------------------------
#  'BaseIDockable' class:
#-------------------------------------------------------------------------------

class BaseIDockable ( HasPrivateFacets ):
    """ Concrete base class implementation of the IDockable interface.
    """

    implements( IDockable )

    #-- IDockable Interface ----------------------------------------------------

    def dockable_should_close ( self ):
        """ Should the current DockControl be closed before creating the new
            one.
        """
        return True


    def dockable_close ( self, dock_control, force ):
        """ Returns whether or not it is OK to close the control.
        """
        if force:
            dock_control.control.destroy()

        return force


    def dockable_get_control ( self, parent ):
        """ Gets a control that can be docked into a DockWindow.
        """
        print "The 'IDockable.dockable_get_control' method must be overridden"
        panel = wx.Panel( parent, -1 )
        panel.SetBackgroundColour( wx.RED )
        return panel


    def dockable_init_dockcontrol ( self, dock_control ):
        """ Allows the object to override the default DockControl settings.
        """
        pass


    def dockable_menu ( self, dock_control, event ):
        """ Returns the right-click popup menu for a DockControl (if any).
        """
        return None


    def dockable_dclick ( self, dock_control, event ):
        """ Handles the user double-clicking on the DockControl.
            A result of False indicates the event was not handled; all other
            results indicate that the event was handled successfully.
        """
        return False


    def dockable_tab_activated ( self, dock_control, activated ):
        """ Handles a notebook tab being activated or deactivated.

            'dock_control' is the control being activated or deactivated.

            If 'activated' is True, the control is being activated; otherwise
            the control is being deactivated.
        """
        pass


    def dockable_bind ( self, dock_control ):
        """ Handles the dockable being bound to a specified DockControl.
        """
        pass

#-- EOF ------------------------------------------------------------------------