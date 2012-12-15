"""
Defines the DockWindowHandler base class used to provide customizable behavior
to a DockWindow.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets

from facets.core.facet_base \
    import user_name_for

from dockable_view_element \
    import DockableViewElement

from dock_control \
    import DockControl

from idockable \
    import IDockable

#-------------------------------------------------------------------------------
#  'DockWindowHandler' class/interface:
#-------------------------------------------------------------------------------

class DockWindowHandler ( HasPrivateFacets ):

    #-- Public Methods ---------------------------------------------------------

    def can_drop ( self, object ):
        """ Returns whether or not a specified object can be inserted into the
            view.
        """
        return True


    def dock_control_for ( self, parent, object ):
        """ Returns the DockControl object for a specified object.
        """
        try:
            name = object.name
        except:
            try:
                name = object.label
            except:
                name = ''

        if name == '':
            name = user_name_for( object.__class__.__name__ )

        image  = None
        export = ''
        if isinstance( object, DockControl ):
            dock_control = object
            image        = dock_control.image
            export       = dock_control.export
            dockable     = dock_control.dockable
            close        = dockable.dockable_should_close()
            if close:
                dock_control.close( force = True )

            control = dockable.dockable_get_control( parent )

            # If DockControl was closed, then reset it to point to the new
            # control:
            if close:
                dock_control.set( control = control,
                                  style   = parent.owner.style )
                dockable.dockable_init_dockcontrol( dock_control )
                return dock_control

        elif isinstance( object, IDockable ):
            dockable = object
            control  = dockable.dockable_get_control( parent )
        else:
            ui       = object.get_dockable_ui( parent )
            dockable = DockableViewElement( ui = ui )
            export   = ui.view.export
            control  = ui.control

        dc = DockControl( control   = control,
                          name      = name,
                          export    = export,
                          style     = parent.owner.style,
                          image     = image,
                          closeable = True )

        dockable.dockable_init_dockcontrol( dc )

        return dc


    def open_view_for ( self, control, use_mouse = True ):
        """ Creates a new view of a specified control.
        """
        from dock_window_shell import DockWindowShell

        DockWindowShell( control, use_mouse = use_mouse )


    def dock_window_empty ( self, dock_window ):
        """ Handles the DockWindow becoming empty.
        """
        if dock_window.auto_close:
            dock_window.control.parent.destroy()

#-- EOF ------------------------------------------------------------------------
