"""
Defines the AnIDockUIProvider class, which is a concrete base class
implementation of the IDockUIProvider interface which objects that support being
dragged and dropped into a DockWindow must implement.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasFacets, implements

from idock_ui_provider \
    import IDockUIProvider

#-------------------------------------------------------------------------------
#  'AnIDockUIProvider' class:
#-------------------------------------------------------------------------------

class AnIDockUIProvider ( HasFacets ):

    implements( IDockUIProvider )

    #-- Public Methods ---------------------------------------------------------

    def get_dockable_ui ( self, parent ):
        """ Returns a Facets UI which a DockWindow can imbed.
        """
        return self.edit_facets( parent     = parent,
                                 kind       = 'subpanel',
                                 scrollable = True )

#-- EOF ------------------------------------------------------------------------