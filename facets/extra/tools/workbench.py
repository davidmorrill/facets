"""
Provides a workbench application for instantiating and using stand-alone tools
created using the tools framework.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import isfile

from facets.api \
    import Handler, Any, List, Bool, Instance, View, UItem, NotebookEditor, \
           SetEditor, on_facet_set

from facets.ui.menu \
    import MenuBar, Menu, Action, ActionGroup

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The Facets UI database key for all exported tools:
ExportedTools = 'facets.extra.tools.tools.ExportedTools'

# The Facets UI database key for all available tools:
AvailableTools = 'facets.extra.tools.workbench.AvailableTools'

#-------------------------------------------------------------------------------
#  Menu actions:
#-------------------------------------------------------------------------------

edit_action        = Action( name   = 'Select available tools...',
                             action = '_select_available_tools' )

single_mode_action = Action( name         = 'Single tool mode',
                             action       = '_single_tool_mode_toggle',
                             style        = 'toggle',
                             checked_when = 'single_tool' )

#-------------------------------------------------------------------------------
#  'Workbench' class:
#-------------------------------------------------------------------------------

class Workbench ( Handler ):
    """ Provides a workbench for instantiating and using stand-alone tools
        created using the tools framework.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Mapping of all known exported tool titles to their corresponding file and
    # class names:
    exported_tools = Any # { tool_title: ( file_name, class_name ) }

    # The list of all known exported tool titles:
    exported_titles = List

    # The ordered list of all available tools titles:
    available_tools = List # ( Str )

    # The set of currently active tools:
    active_tools = List # ( HasFacets )

    # Are we in single tool mode (True) or multi-tool mode (False)?
    single_tool = Bool( True )

    # The contents of the 'Tools' menu group:
    tools_group = Instance( ActionGroup, () )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'active_tools',
                   editor = NotebookEditor(
                       deletable  = True,
                       dock_style = 'auto',
                       export     = 'DockWindowShell',
                       layout     = 'tabs',
                       page_name  = '.name'
                   )
             ),
             title     = 'Facets Tools Workbench',
             id        = 'facets.extra.tools.workbench.Workbench',
             width     = 0.8,
             height    = 0.8,
             resizable = True,
             menubar   = MenuBar(
                             Menu( self.tools_group,   name = 'Tools' ),
                             Menu( edit_action,        name = 'Edit' ),
                             Menu( single_mode_action, name = 'Options' )
                         )
          )


    def available_tools_view ( self ):
        return View(
            UItem( 'available_tools',
                   editor = SetEditor( values   = self.exported_titles,
                                       ordering = 'user' )
            ),
            title     = 'Available Tools',
            id        = 'facets.extra.tools.workbench.AvailableToolsView',
            width     = 150,
            height    = 0.4,
            resizable = True
        )

    #-- Facet Default Values ---------------------------------------------------

    def _exported_tools_default ( self ):
        exported = self.facet_db_get( ExportedTools, {} )
        delete   = []
        for name, value in exported.iteritems():
            file_name, class_name = value
            if not isfile( file_name ):
                delete.append( name )

        if len( delete ) > 0:
            for name in delete:
                del exported[ name ]

            self.facet_db_set( ExportedTools, result )

        return exported


    def _exported_titles_default ( self ):
        return [ title for title in self.exported_tools.iterkeys() ]


    def _available_tools_default ( self ):
        available = self.facet_db_get( AvailableTools, None )
        exported  = self.exported_tools
        if available is None:
            result = sorted( exported.keys() )
        else:
            result = [ name for name in available if name in exported ]

        if result != available:
            self.facet_db_set( AvailableTools, result )

        return result

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        self._rebuild_tools_menu()


    def add_tool ( self, title ):
       """ Adds the tool with the specified *title* to the workbench.
       """
       namespace = {}
       file_name, class_name = self.exported_tools[ title ]
       execfile( file_name, namespace )
       tool = namespace[ class_name ]()

       if self.single_tool:
           self.active_tools = [ tool ]
       else:
           self.active_tools.append( tool )

    #-- Facet Event Handlers ---------------------------------------------------

    def _single_tool_set ( self, single_tool ):
        """ Handles the 'single_tool' facet being changed.
        """
        if single_tool:
            del self.active_tools[:-1]


    @on_facet_set( 'available_tools[]' )
    def _available_tools_modified ( self ):
        """ Handles the 'available_tools' facet being changed.
        """
        self.facet_db_set( AvailableTools, self.available_tools[:] )
        self._rebuild_tools_menu()

    #-- Private Methods --------------------------------------------------------

    def _rebuild_tools_menu ( self ):
        """ Rebuilds the 'Tools' menu based on the current list of available
            tools.
        """
        group = self.tools_group
        group.clear()
        for title in self.available_tools:
            group.append( ToolAction( name = title, workbench = self ) )

        if group.parent is not None:
            group.parent.changed = True


    def _select_available_tools ( self, info ):
        self.edit_facets( view = 'available_tools_view' )


    def _single_tool_mode_toggle ( self, info ):
        self.single_tool = not self.single_tool

#-------------------------------------------------------------------------------
#  'ToolAction' class:
#-------------------------------------------------------------------------------

class ToolAction ( Action ):
    """ Adds a new tool to the workbench.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The Workbench object this action is associated with:
    workbench = Instance( Workbench )

    #-- Action Interface -------------------------------------------------------

    def perform ( self ):
        """ Adds the associated tool to the workbench.
        """
        self.workbench.add_tool( self.name )

#-- Run the tool (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    Workbench().edit_facets()

#-- EOF ------------------------------------------------------------------------
