"""
Defines the MultiPageTool base class used to construct tools which allow
creating and managing a notebook of sub-tool pages derived from PageTool, which
is also defined in this module.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Instance, Any, Range, List, DelegatesTo, View, \
           VGroup, HGroup, Include, Item, UItem, NotebookEditor,            \
           ScrubberEditor, spring, on_facet_set

from facets.extra.features.connect_feature \
    import can_connect

from facets.extra.tools.tools \
    import Tool

#-------------------------------------------------------------------------------
#  Facet Definitions:
#-------------------------------------------------------------------------------

# Define a value that delegates from a PageTool to its owning MultiPageTool:
OwnerValue = DelegatesTo( 'owner' )

#-------------------------------------------------------------------------------
#  'MultiPageTool' class:
#-------------------------------------------------------------------------------

class MultiPageTool ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The page tool class this tool creates and manages:
    page_tool_class = Any

    # The currently selected page tool:
    selected = Any # Instance( page tool )

    # The names of the input facets:
    input_names = List # ( Str )

    # The names of the output facets:
    output_names = List # ( Str )

    # The current set of active page tools:
    page_tools = List # ( page tool )

    # The maximum number of page tools that can be created:
    max_pages = Range( 1, 20, 1, save_state = True )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'page_tools',
                   editor = NotebookEditor(
                       selected   = 'selected',
                       page_name  = '.page_name',
                       dock_style = 'auto',
                       deletable  = True
                   )
            )
        )


    def options ( self ):
        hgroup = HGroup(
            Item( 'max_pages',
                editor     = ScrubberEditor(),
                width      = -30,
                item_theme = '#themes:ScrubberEditor'
            ),
            spring
        )
        page_options = self.facet_view( 'page_options' )
        if isinstance( page_options, HGroup ):
            hgroup.content[0:0] = page_options.content

        return View(
            VGroup( hgroup, group_theme = '#themes:tool_options_group' )
        )

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        items = self.page_tool_class.class_facets( connect = can_connect )
        for name, facet in items.iteritems():
            if facet.connect.startswith( 'to' ):
                #self.add_facet( name, facet )
                self.on_facet_set( self._create_page, name )
                self.input_names.append( name )

            elif facet.connect.startswith( 'from' ):
                self.add_facet( name, facet )
                self.output_names.append( name )

    #-- Default Facet Values ---------------------------------------------------

    def _subtool_class_default ( self ):
        klass = self.__class__.__name__ + 'Page'

    #-- Facet Event Handlers ---------------------------------------------------

    def _max_pages_set ( self ):
        """ Handles the 'max_pages' facet being changed.
        """
        del self.page_tools[ self.max_pages: ]


    def _selected_set ( self, selected ):
        """ Handles the 'selected' facet being changed.
        """
        if selected is not None:
            for name in self.output_names:
                setattr( self, name, getattr( selected, name ) )


    def _create_page ( self ):
        """ Handles an input facet being changed by creating a new page tool for
            handle the input.
        """
        page_tool = self.page_tool_class( owner = self )
        for name in self.output_names:
            page_tool.on_facet_set( self._output_modified, name )

        for name in self.input_names:
            setattr( page_tool, name, getattr( self, name ) )

        if len( self.page_tools ) >= self.max_pages:
            del self.page_tools[0]

        self.page_tools.append( page_tool )


    def _output_modified ( self, object, facet, new ):
        """ Handles one of the output facets being modified on a page tool.
        """
        if self.selected is object:
            setattr( self, facet, new )


    @on_facet_set( 'page_tools[]' )
    def _page_tools_modified ( self, removed ):
        """ Handles the 'page_tools' list being changed.
        """
        for page_tool in removed:
            for name in self.output_names:
                page_tool.on_facet_set(
                    self._output_modified, name, remove = True
                )

        if self.selected in removed:
            self.selected = (None if len( self.page_tools ) == 0 else
                             self.page_tools[-1])

#-------------------------------------------------------------------------------
#  'PageTool' class:
#-------------------------------------------------------------------------------

class PageTool ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The owner of this page tool:
    owner = Instance( MultiPageTool )

#-- EOF ------------------------------------------------------------------------