"""
Adds a 'popup_menu' feature to DockWindow which will display a popup menu
defined by an object when the user clicks on the feature image. The associated
object must have a 'popup_menu' attribute, which can either be a menu or a
function which returns a menu.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.ui.menu \
    import Menu, Action

from facets.ui.dock.api \
    import DockWindowFeature

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Menu to display when there is no valid menu defined:
no_menu = Menu(
    Action( name    = 'No menu available',
            enabled = False ),
    name = 'popup'
 )

#-------------------------------------------------------------------------------
#  'PopupMenuFeature' class:
#-------------------------------------------------------------------------------

class PopupMenuFeature ( DockWindowFeature ):

    #-- Class Constants --------------------------------------------------------

    # The user interface name of the feature:
    feature_name = 'Popup Menu'

    #-- Facet Definitions ------------------------------------------------------

    # The current image to display on the feature bar:
    image = '@facets:popup_menu_feature'

    # The tooltip to display when the mouse is hovering over the image:
    tooltip = 'Click to display the menu.'

    #-- Event Handlers ---------------------------------------------------------

    def click ( self ):
        """ Handles the user left clicking on the feature image.
        """
        object = self.dock_control.object
        menu   = object.popup_menu
        if not isinstance( menu, Menu ):
            try:
                # It might be a method which returns a menu:
                menu = menu()
            except:
                pass

        if not isinstance( menu, Menu ):
            menu = no_menu

        self.popup_menu( menu )

    #-- Overidable Class Methods -----------------------------------------------

    @classmethod
    def is_feature_for ( self, dock_control ):
        """ Returns whether or not the DockWindowFeature is a valid feature for
            a specified DockControl.
        """
        object = dock_control.object

        return ((object is not None) and hasattr( object, 'popup_menu' ))

#-- EOF ------------------------------------------------------------------------