"""
Demonstrates one possible approach to writing Model/View/Controller
(i.e. MVC) based applications using Facets.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

# Imports:
from facets.core_api \
    import HasFacets, Str, Bool, FacetError

from facets.api \
    import View, VGroup, HGroup, Item, Controller

class MyModel ( HasFacets ):
    """ Define a simple model containing a single 'name' string.
    """

    # A name:
    name = Str

class MyViewController ( Controller ):
    """ Define a combined controller/view class that validates that
        MyModel.name is consistent with the 'allow_empty_string' flag.
    """

    # When False, the model.name facet is not allowed to be empty:
    allow_empty_string = Bool

    # Last attempted value of model.name to be set by user:
    last_name = Str

    # Define the view associated with this controller:
    view = View(
        VGroup(
            HGroup(
                Item( 'name', springy = True ), '10',
                Item( 'controller.allow_empty_string', label = 'Allow Empty' )
            ),

            # Add an empty vertical group so the above items don't end up
            # centered vertically:
            VGroup()
        ),
        resizable = True
    )

    #-- Handler Interface ------------------------------------------------------

    def name_setattr ( self, info, object, name, value ):
        """ Validate the request to change the named facet on object to the
            specified value.  Vaildation errors raise FacetError.
        """
        self.last_name = value
        if (not self.allow_empty_string) and (value.strip() == ''):
            raise FacetError( 'Empty string not allowed.' )

        return super( MyViewController, self ).setattr( info, object, name,
                                                         value )

    #-- Event handlers ---------------------------------------------------------

    def controller_allow_empty_string_changed ( self, info ):
        """ 'allow_empty_string' has changed, check the name facet to ensure
            that it is consistent with the current setting.
        """
        if (not self.allow_empty_string) and (self.model.name == ''):
            self.model.name = '?'
        else:
            self.model.name = self.last_name

#-- Create the model and (demo) view/controller --------------------------------

demo = MyViewController( MyModel() )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------