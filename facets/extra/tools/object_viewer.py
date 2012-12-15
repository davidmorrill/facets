"""
Defines the ObjectViewer tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets, HasPrivateFacets, Any, Str, List, Range, Instance, \
           Theme, View, HToolbar, VGroup, Item, NotebookEditor,          \
           InstanceEditor, spring

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.api \
    import HasPayload

from facets.extra.helper.themes \
    import TTitle, Scrubber

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ObjectViewer' class:
#-------------------------------------------------------------------------------

class ObjectViewer ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Object Viewer'

    # Maximum number of open viewers allowed:
    max_viewers = Range( 1, 50, 3, save_state = True )

    # The current item being viewed:
    object = Instance( HasFacets,
                      droppable = 'Drop an object with facets here to view it.',
                      connect   = 'to: object with facets' )

    # Current list of objects viewed:
    viewers = List

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        Item( 'viewers@',
              show_label = False,
              editor     = NotebookEditor( deletable  = True,
                                           page_name  = '.name',
                                           export     = 'DockWindowShell',
                                           dock_style = 'auto' )
        )
    )

    options = View(
        HToolbar(
            spring,
            Scrubber( 'max_viewers', 'Maximum number of open viewers',
                width = 50,
                label = 'Max viewers'
            ),
            group_theme = Theme( '@xform:b?L10', content = ( 4, 0, 4, 4 ) ),
            id          = 'tb'
        ),
        id = 'facets.extra.tools.object_viewer.ObjectViewer.options'
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _max_viewers_set ( self, max_viewers ):
        """ Handles the 'max_viewers' facet being changed.
        """
        delta = len( self.viewers ) - max_viewers
        if delta > 0:
            del self.viewers[ : delta ]


    def _object_set ( self, value ):
        """ Handles the 'object' facet being changed.
        """
        if value is not None:
            # Reset the current object to None, so we are ready for a new one:
            do_later( self.set, object = None )

            name = title = ''
            if isinstance( value, HasPayload ):
                name  = value.payload_name
                title = value.payload_full_name
                value = value.payload

            viewers = self.viewers
            for i, viewer in enumerate( viewers ):
                if value is viewer.object:
                    if i == (len( viewers ) - 1):
                        return

                    del viewers[ i ]

                    break
            else:
                # Create the viewer:
                viewer = AnObjectViewer( name   = name,
                                         title  = title ).set(
                                         object = value )

                # Make sure the # of viewers doesn't exceed the maximum allowed:
                if len( viewers ) >= self.max_viewers:
                    del viewers[0]

            # Add the new viewer to the list of viewers (which will cause it to
            # appear as a new notebook page):
            viewers.append( viewer )

#-------------------------------------------------------------------------------
#  'AnObjectViewer' class:
#-------------------------------------------------------------------------------

class AnObjectViewer ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The viewer page name:
    name = Str

    # The object associated with this view:
    object = Any

    # The title of this view:
    title = Str

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            TTitle( 'title', visible_when = "title != ''" ),
            Item( 'object',  style = 'custom', editor = InstanceEditor() ),
            show_labels = False
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _object_set ( self, value ):
        """ Updates the 'object' facet being changed.
        """
        if self.name == '':
            try:
                name = getattr( value, 'name', None )
                if not isinstance( name, str ):
                    name = None
            except:
                name = None

            if name is None:
                name = value.__class__.__name__

            self.name = name

        if self.title == '':
            try:
                self.title = getattr( value, 'title', None )
            except:
                pass

#-- EOF ------------------------------------------------------------------------