"""
Defines the GeneratedTool class, which is the base class for all perspectives
converted into Python tool modules by the tools frameowrk.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from cPickle \
    import loads

from facets.api \
    import HasFacets, HasPrivateFacets, Any, Str, Float, Enum, List, Instance, \
           View, UItem, NotebookEditor

from facets.extra.tools.tools \
    import Tool, XTool

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def ToolInstance ( klass, name ):
    """ Returns a custom Instance facet used for instantiating tools.
    """
    return Instance( klass, { 'name': name }, is_tool = True )

#-------------------------------------------------------------------------------
#  'Connection' class:
#-------------------------------------------------------------------------------

class Connection ( HasPrivateFacets ):
    """ Defines a connection between one tool facet and another.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The direction of the connection:
    connection = Enum( 'to', 'from', 'both' )

    # The first object in the connection:
    object1 = Instance( HasFacets )

    # The name of the facet connected on that object:
    name1 = Str

    # The second object in the connection:
    object2 = Instance( HasFacets )

    # The name of the facet on that object:
    name2 = Str

    #-- Public Methods ---------------------------------------------------------

    def facets_init ( self ):
        """ Finishes initializing the object.
        """
        connection = self.connection
        if connection in ( 'from', 'both' ):
            self.object1.on_facet_set( self.connect_from, self.name1,
                                       dispatch = 'ui' )
            self.connect_from( getattr( self.object1, self.name1 ) )

        if connection in ( 'to', 'both' ):
            self.object2.on_facet_set( self.connect_to, self.name2,
                                       dispatch = 'ui' )
            if connection == 'to':
                self.connect_to( getattr( self.object2, self.name2 ) )


    def disconnect ( self ):
        """ Disconnects the objects.
        """
        connection = self.connection
        if connection in ( 'from', 'both' ):
            self.object1.on_facet_set( self.connect_from, self.name1,
                                       remove = True )

        if connection in ( 'to', 'both' ):
            self.object2.on_facet_set( self.connect_to, self.name2,
                                       remove = True )


    def connect_from ( self, value ):
        """ Copies a value from object1 to object2.
        """
        if not self._frozen:
            self._frozen = True
            try:
                setattr( self.object2, self.name2, value )
            except:
                pass
            self._frozen = False


    def connect_to ( self, value ):
        """ Copies a value from object1 to object2.
        """
        if not self._frozen:
            self._frozen = True
            try:
                setattr( self.object1, self.name1, value )
            except:
                pass

            self._frozen = False

#-------------------------------------------------------------------------------
#  'GeneratedTool' class:
#-------------------------------------------------------------------------------

class GeneratedTool ( HasPrivateFacets ):
    """ Defines the base class for all generated tools.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str

    # The View id for the tool:
    id = Str

    # The DockWindow features used by the tool:
    features = List

    # The list of all component tools:
    tools = List

    # The DockWindow tab style the NotebookEditor should use:
    dock_style = Str

    # The default width for the tool view:
    width = Float( 0.8 )

    # The default height for the tool view:
    height = Float( 0.8 )

    # The layout template for the tools:
    template = Any

    # The list of tool connections:
    connections = List

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        """ Returns the View to use with this perspective.
        """
        return View(
            UItem( 'tools',
                  style  = 'custom',
                  id     = 'tools',
                  editor = NotebookEditor(
                      features   = self.features,
                      dock_style = self.dock_style,
                      page_name  = '.name',
                      template   = 'template'
                  )
            ),
            title     = self.name,
            id        = self.id,
            width     = self.width,
            height    = self.height,
            resizable = True
        )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        # Force connections to be initialized:
        self.connections

        # Create unique ids for each component tool:
        tools = self.tools
        for tool in tools:
             if isinstance( tool, Tool ):
                 tool.id = '%s:%s.view' % ( self.id, tool.name )

                 # If this is an XTool, provide it with a list of all other
                 # tools (excluding itself):
                 if isinstance( tool, XTool ):
                     copy_tools = tools[:]
                     copy_tools.remove( tool )
                     tool.tools = copy_tools

    #-- Facet Default Values ---------------------------------------------------

    def _id_default ( self ):
        return ('facets.extra.tools.tools.generated.' + self.__class__.__name__)


    def _tools_default ( self ):
        return [ getattr( self, name )
                 for name in self.facet_names( is_tool = True ) ]


    def _template_default ( self ):
        return loads( self._template )

#-- EOF ------------------------------------------------------------------------
