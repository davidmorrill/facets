"""
Creates a GUI toolkit neutral modal dialog user interface that runs as a
complete application, using information from the specified UI object.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Any, Str, View, Item, Tabbed, Instance, \
           InstanceEditor, VIPShellEditor, FacetError

from facets.core.facets_env \
    import facets_env

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  'AppInfo' class:
#-------------------------------------------------------------------------------

class AppInfo ( HasPrivateFacets ):
    """ Defines an object containing the information to pass to the toolkit
        'run_application' method in order to create the initial Facets UI.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The UI context object or dictionary:
    context = Any

    # The UI view to display:
    view = Any

    # The kind of view to display:
    kind = Any

    # The view's Handler (if any):
    handler = Any

    # The id of the view:
    id = Str

    # Is the view scrollable?
    scrollable = Any

    # Optional arguments used to initialize the handler:
    args = Any( {} )

    # The UI object created from the specified view:
    ui = Any

    # The application object being viewed:
    application = Any

    #-- Public Methods ---------------------------------------------------------

    def run_app ( self ):
        """ Default method for launching a Facets UI.
        """
        toolkit().run_application( self )

        return self.ui


    def run_shell ( self ):
        """ Run the VIP Shell and the application within a single window,
            each in its own tab.
        """
        return self._run_shell( 'shell_view' )


    def run_shell_app ( self ):
        """ Run the application and the VIP Shell in separate windows.
        """
        return self._run_shell( 'shell_app_view' )


    def run_tools ( self ):
        """ Run the application and the developer tool suite in separate
            windows.
        """
        from facets.extra.tools.tools import tools

        ui = self.application.edit_facets(
            view       = self.view,
            context    = self.context,
            id         = self.id,
            kind       = self.kind,
            handler    = self.handler,
            scrollable = self.scrollable,
            **(self.args)
        )

        tools_object = tools( object = self.application, show = False )
        AppInfo(
            context = tools_object,
            view    = tools_object.facet_view()
        ).run_app()

        return ui

    #-- Facet Default Values ---------------------------------------------------

    def _application_default ( self ):
        object = self.context
        if isinstance( object, dict ):
            if len( dict ) == 1:
                object = dict.values()[0]
            else:
                object = object.get( 'object' )
                if object is None:
                    names = object.keys()
                    names.sort()
                    raise FacetError(
                        'Could not determine application object from context '
                        'with multiple keys: %s' % (', '.join( names ))
                    )

        return object

    #-- Private Methods --------------------------------------------------------

    def _run_shell ( self, view_name ):
        shell_app = VIPShellApplication( app_info = self )

        return AppInfo(
            context = shell_app,
            view    = shell_app.facet_view( view_name )
        ).run_app()

#-------------------------------------------------------------------------------
#  'VIPShellApplication' class:
#-------------------------------------------------------------------------------

class VIPShellApplication ( HasPrivateFacets ):
    """ Launches a client application embedded within a window that also
        contains a VIPShell used to debug/test it.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The information describing the application to embed:
    app_info = Instance( AppInfo )

    # The name of the application:
    app_name = Str

    # The application title that should appear in the title bar of the shell:
    app_title = Str

    # The application object being viewed:
    application = Any

    # The 'locals' dictionary to use for the VIP Shell:
    locals = Any( {} )

    #-- Default Facet Values ---------------------------------------------------

    def shell_view ( self ):
        return View(
            Tabbed(
                Item( 'application',
                      id         = 'application',
                      style      = 'custom',
                      show_label = False,
                      label      = 'Application',
                      dock       = 'tab',
                      export     = 'DockShellWindow',
                      editor     = InstanceEditor(
                                       view = self.app_info.view,
                                       id   = self._id_for( '.application' ) )
                ),
                Item( 'locals',
                      id         = 'shell',
                      show_label = False,
                      label      = 'Shell',
                      dock       = 'tab',
                      editor     = VIPShellEditor( share = True )
                ),
                id = 'tabbed'
            ),
            title     = self.app_title,
            id        = self._id_for(),
            width     = 0.5,
            height    = 0.5,
            resizable = True
        )


    def shell_app_view ( self ):
        app_info = self.app_info
        self.application.edit_facets(
            view       = app_info.view,
            context    = app_info.context,
            id         = app_info.id,
            kind       = app_info.kind,
            handler    = app_info.handler,
            scrollable = app_info.scrollable,
            **(app_info.args)
        )

        return View(
            Item( 'locals',
                  id         = 'shell',
                  show_label = False,
                  editor     = VIPShellEditor( share = True )
            ),
            title     = self.app_title,
            id        = self._id_for( '.shell_app' ),
            width     = 0.5,
            height    = 0.5,
            resizable = True
        )

    #-- Default Facet Values ---------------------------------------------------

    def _locals_default ( self ):
        locals = self.app_info.context
        if isinstance( locals, dict ):
            return locals

        return { 'object': locals }


    def _application_default ( self ):
        return self.app_info.application


    def _app_name_default ( self ):
        return self.application.__class__.__name__


    def _app_title_default ( self ):
        return ('VIP Shell [%s]' % (self.app_info.view.title or
                                    self.app_name))

    #-- Private Methods --------------------------------------------------------

    def _id_for ( self, modifier = '' ):
        """ Returns as ui ID based on a specified modifier and the application
            name.
        """
        return ('facets.ui.view_application.VIPShellApplication%s:%s' % (
                modifier, self.app_name ))

#-------------------------------------------------------------------------------
#  Creates a 'stand-alone' application to display a specified facets UI View:
#-------------------------------------------------------------------------------

def view_application ( context, view, kind, handler, id, scrollable, args ):
    """ Creates a stand-alone application to display a specified facets UI View.

        Parameters
        ----------
        context : object or dictionary
            A single object or a dictionary of string/object pairs, whose facet
            attributes are to be edited. If not specified, the current object is
            used.
        view : view object
            A View object that defines a user interface for editing facet
            attribute values.
        kind : string
            The type of user interface window to create. See the
            **facets.ui.ui_facets.AKind** facet for values and
            their meanings. If *kind* is unspecified or None, the **kind**
            attribute of the View object is used.
        handler : Handler object
            A handler object used for event handling in the dialog box. If
            None, the default handler for Facets UI is used.
        scrollable : Boolean
            Indicates whether the dialog box should be scrollable. When set to
            True, scroll bars appear on the dialog box if it is not large enough
            to display all of the items in the view at one time.
    """
    if (kind == 'panel') or ((kind is None) and (view.kind == 'panel')):
        kind = 'modal'

    if not toolkit().is_application_running():
        app_info = AppInfo(
            context    = context,
            view       = view,
            kind       = kind,
            handler    = handler,
            id         = id,
            scrollable = scrollable,
            args       = args
        )

        facets_fbi = facets_env.fbi
        if facets_fbi != 0:
            try:
                from facets.extra.helper.fbi import bp

                condition = True
                if facets_fbi < 0:
                    condition = None

                bp( condition, context )
            except:
                pass

        name   = facets_env.init
        method = getattr( app_info, 'run_' + name, None )
        if method is None:
            raise FacetError(
                ("Unrecognized value for 'FACETS_INIT' environment variable: "
                 "'%s'") % name
            )

        return method()

    return view.ui(
        context,
        kind       = kind,
        handler    = handler,
        id         = id,
        scrollable = scrollable,
        args       = args
    )

#-- EOF ------------------------------------------------------------------------