"""
Defines the DropZone tool that allows objects dragged and dropped onto the tool
to be exported to other tools.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import exists

from facets.api \
    import Str, Any, View, HGroup, UItem, DNDEditor, spring

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'DropZone' class:
#-------------------------------------------------------------------------------

class DropZone ( Tool ):
    """ The DropZone tool allows objects dragged and dropped onto the tool to be
        exported to other tools.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Drop Zone' )

    # The most recently dropped items:
    items = Any

    # The item available for other to tools to connect to:
    item = Any( connect = 'from' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HGroup(
            UItem( 'items',
                   editor = DNDEditor( image = '@icons2:ArrowLargeDown' )
            ),
            spring
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _items_set ( self ):
        items = self.items
        if not isinstance( items, ( list, tuple ) ):
            items = [ items ]

        for item in items:
            if (isinstance( item, basestring ) and
                (item[:3] == '///')            and
                exists( item[3:])):
                item = item[3:]

            self.item = item

#-- EOF ------------------------------------------------------------------------
