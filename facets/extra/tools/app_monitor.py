"""
Defines the AppMonitor tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, Instance, List, Enum, Property, View, \
           VGroup, Item, ValueEditor, NotebookEditor

from facets.ui.adapters.control \
    import Control

from facets.ui.dock.api \
    import DockControl, dock_control_for

from facets.extra.features.api \
    import CustomFeature

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'AppMonitor' class:
#-------------------------------------------------------------------------------

class AppMonitor ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Application Monitor'

    # The view style used to display the data:
    view_style = Enum( 'Tree', 'Notebook', save_state = True )

    feature = CustomFeature(
        image   = '@facets:refresh',
        click   = 'refresh',
        tooltip = 'Click to refresh view.'
    )

    # The control whose associated DockControl specifies which application
    # objects to display:
    control = Instance( Control, connect = 'to' )

    # Our DockControl object:
    dock_control = Instance( DockControl, dock_control = True )

    # The list of application objects being monitored:
    objects = List

    # The current view_object:
    view_object = Instance( HasFacets )

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'view_object@',
              show_label = False,
              resizable  = True
        )
    )

    options = View(
        VGroup(
            Item( 'view_style', width = 180 ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def refresh ( self ):
        """ Refreshes the contents of the view.
        """
        self.objects = [ dc.object for dc in self.dock_control.dock_controls
                                   if isinstance( dc.object, HasFacets ) ]
        self.set_view_object()

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self ):
        """ Handles the 'control' facet being changed.
        """
        dock_control = dock_control_for( self.control )
        if dock_control is not None:
            self.dock_control = dock_control


    def _dock_control_set ( self ):
        """ Handles the 'dock_control' facet being changed.
        """
        self.refresh()


    def _view_style_set ( self ):
        """ Handles the 'view_style' facet being changed.
        """
        self.set_view_object()

    #-- Private Methods --------------------------------------------------------

    def set_view_object ( self ):
        """ Sets the current view object based on the current view style.
        """
        if self.view_style == 'Tree':
            self.view_object = AppTreeView( objects = self.objects )
        else:
            self.view_object = AppNotebookView( objects = self.objects )

#-------------------------------------------------------------------------------
#  'AppTreeView' class:
#-------------------------------------------------------------------------------

class AppTreeView ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The list of objects to display:
    objects = List

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'objects',
              show_label = False,
              editor     = ValueEditor()
        )
    )

#-------------------------------------------------------------------------------
#  'AppNotebookView' class:
#-------------------------------------------------------------------------------

class AppNotebookView ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The list of objects to display:
    objects = List

    # The list of NotebookItems corresponding to the list of objects:
    items = List

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'items@',
              show_label = False,
              editor     = NotebookEditor( deletable  = True,
                                           page_name  = '.name',
                                           export     = 'DockWindowShell',
                                           dock_style = 'auto' )
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _objects_set ( self, objects ):
        """ Handles the 'objects' facet being changed.
        """
        self.items = [ NotebookItem( object = object ) for object in objects ]

#-------------------------------------------------------------------------------
#  'NotebookItem' class:
#-------------------------------------------------------------------------------

class NotebookItem ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The object being displayed:
    object = Instance( HasFacets )

    # The name of the object:
    name = Property

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'object',
              show_label = False,
              editor     = ValueEditor()
        )
    )

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        return self.object.__class__.__name__

#-- EOF ------------------------------------------------------------------------