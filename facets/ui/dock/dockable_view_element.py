"""
Defines the DockableViewElement class, which allows Facets UIs and Facets UI
elements to be docked in external DockWindow windows.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Instance, Bool

from facets.ui.ui \
    import UI

from facets.ui.group \
    import Group

from facets.ui.view \
    import View

from facets.ui.view_element \
    import ViewSubElement

from idockable \
    import BaseIDockable

#-------------------------------------------------------------------------------
#  'DockableViewElement' class:
#-------------------------------------------------------------------------------

class DockableViewElement ( BaseIDockable ):
    """ Allows Facets UIs and Facets UI elements to be docked in external
        DockWindow windows.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The Facets UI that can be docked with an external DockWindow
    ui = Instance( UI )

    # The (optional) element of the Facets UI that can be docked
    element = Instance( ViewSubElement )

    # Should the DockControl be closed on redocking?
    should_close = Bool( False )

    #-- IDockable interface ----------------------------------------------------

    def dockable_should_close ( self ):
        """ Should the current DockControl be closed before creating the new
            one?
        """
        element = self.element
        if element is None:
            element = self.ui.view.content

        if not isinstance( element, Group ):
            element = Group().set( content = [ element ] )

        group         = Group().set( content = [ element ] )
        ui            = self.ui
        self._view    = View().set( **ui.view.get() ).set( content = group,
                                                           title   = '' )
        self._context = ui.context.copy()
        self._handler = ui.handler

        return (self.should_close or (self.element is None))


    def dockable_get_control ( self, parent ):
        """ Gets a control that can be docked into a DockWindow.
        """
        # Create the new UI:
        ui = self._view.ui( self._context, parent  = parent,
                                           kind    = 'editor',
                                           handler = self._handler )

        # Discard the reference to the view created previously:
        self._view = self._context = self._handler = None

        # If the old UI was closed, then switch to using the new one:
        if self.element is None:
            self.ui = ui
        else:
            self._ui = ui

        return ui.control


    def dockable_init_dockcontrol ( self, dock_control ):
        """ Allows the object to override the default DockControl settings.
        """
        dockable = self
        if self.element is not None:
            dockable = DockableViewElement( ui           = self._ui,
                                            element      = self.element,
                                            should_close = True )
            self._ui = None

        dock_control.set( dockable = dockable,
                          on_close = dockable.close_dock_control )


    def close_dock_control ( self, dock_control, abort ):
        """ Handles the closing of a DockControl containing a Facets UI.
        """
        ui = self.ui

        # Ask the facets UI handler if it is OK to close the window:
        if (not abort) and (not ui.handler.close( ui.info, True )):
            # If not, tell the DockWindow not to close it:
            return False

        # Otherwise, clean up and close the facets UI:
        ui.dispose( abort = abort )

        # Break our linkage to the UI and ViewElement object:
        self.ui = self.element = None

        # And tell the DockWindow to remove the DockControl:
        return True

#-- EOF ------------------------------------------------------------------------