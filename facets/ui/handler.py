"""
Defines the Handler class used to manage and control the editing process in
a Facets-based user interface.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from help \
    import on_help_call

from view_element \
    import ViewElement

from helper \
    import user_name_for

from ui_info \
    import UIInfo

from i_ui_info \
    import IUIInfo

from helper \
    import position

from facets.core_api \
    import HasPrivateFacets, HasFacets, Instance, implements

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def close_dock_control ( dock_control ):
    """ Closes a DockControl (if allowed by the associated Facets UI Handler).
    """
    # Retrieve the facets UI object set when we created the DockControl:
    ui = dock_control.data

    # Ask the facets UI handler if it is OK to close the window:
    if not ui.handler.close( ui.info, True ):
        # If not, tell the DockWindow not to close it:
        return False

    # Otherwise, clean up and close the facets UI:
    ui.dispose()

    # And tell the DockWindow to remove the DockControl:
    return True

#-------------------------------------------------------------------------------
#  'Handler' class:
#-------------------------------------------------------------------------------

class Handler ( HasPrivateFacets ):
    """ Provides access to and control over the run-time workings of a
        Facets-based user interface.
    """

    #-- Public Methods ---------------------------------------------------------

    def init_info ( self, info ):
        """ Informs the handler what the UIInfo object for a View will be.

            This method is called before the UI for the View has been
            constructed. It is provided so that the handler can save the
            reference to the UIInfo object in case it exposes viewable facets
            whose values are properties that depend upon items in the context
            being edited.
        """
        pass


    def init ( self, info ):
        """ Initializes the controls of a user interface.

            Parameters
            ----------
            info : UIInfo object
                The UIInfo object associated with the view

            Returns
            -------
            A Boolean, indicating whether the user interface was successfully
            initialized. A True value indicates that the UI can be displayed;
            a False value indicates that the display operation should be
            cancelled. The default implementation returns True without taking
            any other action.

            Description
            -----------
            This method is called after all user interface elements have been
            created, but before the user interface is displayed. Override this
            method to customize the user interface before it is displayed.
        """
        # Get all context objects that implement the IUIInfo interface:
        objects = self._ui_info_objects( info )

        # Make sure that none of them currently have an active View open:
        for object in objects:
            if object.ui_info is not None:
                return False

        # Save the UIInfo object in each object implementing the interface:
        for object in objects:
            object.ui_info = info

        # Indicate the view can be opened:
        return True


    def position ( self, info ):
        """ Positions a dialog-based user interface on the display.

            Parameters
            ----------
            info : UIInfo object
                The UIInfo object associated with the window

            Returns
            -------
            Nothing.

            Description
            -----------
            This method is called after the user interface is initialized (by
            calling init()), but before the user interface is displayed.
            Override this method to position the window on the display device.
            The default implementation calls the position() method of the
            current toolkit.

            Usually, you do not need to override this method, because you can
            control the window's placement using the **x** and **y** attributes
            of the View object.
        """
        position( info.ui )


    def close ( self, info, is_ok ):
        """ Handles the user attempting to close a dialog-based user interface.

            Parameters
            ----------
            info : UIInfo object
                The UIInfo object associated with the view
            is_ok : Boolean
                Indicates whether the user confirmed the changes (such as by
                clicking **OK**.)

            Returns
            -------
            A Boolean, indicating whether the window should be allowed to close.

            Description
            -----------
            This method is called when the user attempts to close a window, by
            clicking an **OK** or **Cancel** button, or clicking a Close control
            on the window). It is called before the window is actually
            destroyed. Override this method to perform any checks before closing
            a window.

            While Facets UI handles "OK" and "Cancel" events automatically, you
            can use the value of the *is_ok* parameter to implement additional
            behavior.
        """
        return True


    def closed ( self, info, is_ok ):
        """ Handles a dialog-based user interface being closed by the user.

            Parameters
            ----------
            info : UIInfo object
                The UIInfo object associated with the view
            is_ok : Boolean
                Indicates whether the user confirmed the changes (such as by
                clicking **OK**.)

            Description
            -----------
            This method is called *after* the window is destroyed. Override this
            method to perform any clean-up tasks needed by the application.
        """
        # Disconnect all context objects that implement the IUIInfo interface
        # from their currently associated UIInfo object:
        for object in self._ui_info_objects( info ):
            object.ui_info = None


    def revert ( self, info ):
        """ Handles the **Revert** button being clicked.
        """
        return


    def apply ( self, info ):
        """ Handles the **Apply** button being clicked.
        """
        return


    def show_help ( self, info, control = None ):
        """ Shows the help associated with the view.

            Parameters
            ----------
            info : UIInfo object
                The UIInfo object associated with the view
            control : UI control
                The control that invokes the help dialog box

            Description
            -----------
            This method is called when the user clicks a **Help** button in a
            Facets user interface. The method calls the global help handler,
            which might be the default help handler, or might be a custom help
            handler. See **facets.ui.help** for details about the setting the
            global help handler.
        """
        if control is None:
            control = info.ui.control

        on_help_call()( info, control )


    def setattr ( self, info, object, name, value ):
        """ Handles the user setting a specified object facet's value.

            Parameters
            ----------
            object : object
                The object whose attribute is being set
            name : string
                The name of the attribute being set
            value
                The value to which the attribute is being set

            Description
            -----------
            This method is called when an editor attempts to set a new value for
            a specified object facet attribute. Use this method to control what
            happens when a facet editor tries to set an attribute value. For
            example, you can use this method to record a history of changes, in
            order to implement an "undo" mechanism. No result is returned. The
            default implementation simply calls the built-in setattr() function.
            If you override this method, make sure that it actually sets the
            attribute, either by calling the parent method or by setting the
            attribute directly
        """
        setattr( object, name, value )


    def facet_view_for ( self, info, view, object, object_name, facet_name ):
        """ Gets a specified View object.
        """
        # If a view element was passed instead of a name or None, return it:
        if isinstance( view, ViewElement ):
            return view

        # Generate a series of possible view or method names of the form:
        # - 'view'
        #   facet_view_for_'view'( object )
        # - 'class_view'
        #   facet_view_for_'class_view'( object )
        # - 'object_name_view'
        #   facet_view_for_'object_name_view'( object )
        # - 'object_name_class_view'
        #   facet_view_for_'object_name_class_view'( object )
        # where 'class' is the class name of 'object', 'object' is the object
        #       name, and 'name' is the facet name. It returns the first view
        #       or method result which is defined on the handler:
        klass = object.__class__.__name__
        cname = '%s_%s' % ( object_name, facet_name )
        aview = ''
        if view:
            aview = '_' + view
        names = [ '%s_%s%s' % ( cname, klass, aview ),
                  '%s%s'    % ( cname, aview ),
                  '%s%s'    % ( klass, aview ) ]
        if view:
            names.append( view )

        for name in names:
            result = self.facet_view( name )
            if result is not None:
                return result

            method = getattr( self, 'facet_view_for_%s' % name, None )
            if callable( method ):
                result = method( info, object )
                if result is not None:
                    return result

        # If nothing is defined on the handler, return either the requested
        # view on the object itself, or the object's default view:
        return object.facet_view( view ) or object.facet_view()

    #-- 'DockWindowHandler' Interface Implementation ---------------------------

    def can_drop ( self, info, object ):
        """ Can the specified object be inserted into the view?
        """
        from facets.ui.dock.api import DockControl

        if isinstance( object, DockControl ):
            return self.can_import( info, object.export )

        drop_class = info.ui.view.drop_class

        return ((drop_class is not None) and isinstance( object, drop_class ))


    def can_import ( self, info, category ):
        return (category in info.ui.view.imports)


    def dock_control_for ( self, info, parent, object ):
        """ Returns the DockControl object for a specified object.
        """
        from facets.ui.dock.api                   import IDockable, DockControl
        from facets.ui.dock.dockable_view_element import DockableViewElement

        try:
            name = object.name
        except:
            try:
                name = object.label
            except:
                name = ''

        if len( name ) == 0:
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

        dc = DockControl(
            control   = control,
            name      = name,
            export    = export,
            style     = parent.owner.style,
            image     = image,
            closeable = True
        )
        dockable.dockable_init_dockcontrol( dc )

        return dc


    def open_view_for ( self, control, use_mouse = True ):
        """ Creates a new view of a specified control.
        """
        from facets.ui.dock.api import DockWindowShell

        DockWindowShell( control, use_mouse = use_mouse )


    def dock_window_empty ( self, dock_window ):
        """ Handles a DockWindow becoming empty.
        """
        if dock_window.auto_close:
            dock_window.control.GetParent.Destroy()

    #-- HasFacets Overrides ----------------------------------------------------

    def edit_facets ( self, view       = None, parent  = None, kind = None,
                            context    = None, handler = None, id   = '',
                            scrollable = None, **args ):
        """ Edits the object's facets.
        """
        if context is None:
            context = self

        if handler is None:
            handler = self

        view = self.facet_view( view )

        from facets.ui.toolkit          import toolkit
        from facets.ui.view_application import view_application

        if toolkit().is_application_running():
            return view.ui( context, parent, kind, self.facet_view_elements(),
                            handler, id, scrollable, args )

        return view_application( context, view, kind, handler, id, scrollable,
                                 args )


    def configure_facets ( self, filename = None, view       = None,
                                 kind     = None, edit       = True,
                                 context  = None, handler    = None,
                                 id       = '',   scrollable = None, **args ):
        """ Configures the object's facets.
        """
        super( HasPrivateFacets, self ).configure_facets(
                       filename, view, kind, edit, context, handler or self, id,
                       scrollable, **args )

    #-- Private Methods --------------------------------------------------------

    def _on_undo ( self, info ):
        """ Handles an "Undo" change request.
        """
        if info.ui.history is not None:
            info.ui.history.undo()


    def _on_redo ( self, info ):
        """ Handles a "Redo" change request.
        """
        if info.ui.history is not None:
            info.ui.history.redo()


    def _on_revert ( self, info ):
        """ Handles a "Revert all changes" request.
        """
        if info.ui.history is not None:
            info.ui.history.revert()
            self.revert( info )


    def _on_close ( self, info ):
        """ Handles a "Close" request.
        """
        if (info.ui.owner is not None) and self.close( info, True ):
            info.ui.owner.close()


    def _ui_info_objects ( self, info ):
        """ Returns all context objects which implement the IUIInfo interface.
        """
        return [ object for name, object in info.ui.context.iteritems()
                        if (name != 'context') and
                           object.has_facets_interface( IUIInfo ) ]

#-------------------------------------------------------------------------------
#  Default handler:
#-------------------------------------------------------------------------------

_default_handler = Handler()

def default_handler ( handler = None ):
    """ Returns the global default handler.

        If *handler* is an instance of Handler, this function sets it as the
        global default handler.
    """
    global _default_handler

    if isinstance( handler, Handler ):
        _default_handler = handler

    return _default_handler

#-------------------------------------------------------------------------------
#  'Controller' class:
#-------------------------------------------------------------------------------

class Controller ( Handler ):
    """ Defines a handler class which provides a view and controller for a
        specified model.

        This class is used when implementing a standard MVC-based design. The
        **model** facet contains most, if not all, of the data being viewed,
        and can be referenced in a Controller instance's View definition using
        unadorned facet names. (e.g., ``Item('name')``).
    """

    #-- Facet Definitions ------------------------------------------------------

    # The model this handler defines a view and controller for
    model = Instance( HasFacets )

    # The Info object associated with the controller
    info = Instance( UIInfo )

    #-- HasFacets Method Overrides ---------------------------------------------

    def __init__ ( self, model = None, **metadata ):
        """ Initializes the object and sets the model (if supplied).
        """
        super( Controller, self ).__init__( **metadata )
        self.model = model


    def facet_context ( self ):
        """ Returns the default context to use for editing or configuring
            facets.
        """
        return { 'object': self.model, 'controller': self, 'handler': self }

    #-- Handler Method Overrides -----------------------------------------------

    def init_info ( self, info ):
        """ Informs the handler what the UIInfo object for a View will be.
        """
        self.info = info

#-------------------------------------------------------------------------------
#  'ModelView' class:
#-------------------------------------------------------------------------------

class ModelView ( Controller ):
    """ Defines a handler class which provides a view and controller for a
        specified model.

        This class is useful when creating a variant of the standard MVC-based
        design. A subclass of ModelView reformulates a number of facets on
        its **model** object as properties on the ModelView subclass itself,
        usually in order to convert them into a more user-friendly format. In
        this design, the ModelView subclass supplies not only the view and
        the controller, but also, in effect, the model (as a set of properties
        wrapped around the original model). Because of this, the ModelView
        context dictionary specifies the ModelView instance itself as the
        special *object* value, and assigns the original model object as the
        *model* value. Thus, the facets of the ModelView object can be
        referenced in its View definition using unadorned facet names.
    """

    #-- HasFacets Method Overrides ---------------------------------------------

    def facet_context ( self ):
        """ Returns the default context to use for editing or configuring
            facets.
        """
        return { 'object': self, 'handler': self, 'model': self.model }

#-------------------------------------------------------------------------------
#  'ViewHandler' class:
#-------------------------------------------------------------------------------

class ViewHandler ( Handler ):

    pass

#-------------------------------------------------------------------------------
#  'UIView' class:
#-------------------------------------------------------------------------------

class UIView ( HasPrivateFacets ):
    """ Defines the UIView class which allows any model subclass to
        automatically obtain a reference to the UIInfo object of any active View
        via its 'ui_info' facet whenever a View is opened on an instance. As a
        side effect, it also ensures that only one View can be open on an object
        at a time.
    """

    implements( IUIInfo )

    #-- IUIInfo Interface Facet Definitions ------------------------------------

    # The UIInfo object for an open View of the object:
    ui_info = Instance( 'facets.ui.ui_info.UIInfo' )

#-- EOF ------------------------------------------------------------------------