"""
Defines the ShellTag base class used to define the objects associated with tags
in a ShellItem's content.

Custom tags should subclass ShellTag, add any necessary facets to hold related
data, and define methods with names of the form: [modifier_]*[click|right_click]
where 'modifier' can be 'alt', 'control' or 'shift'. If multiple modifiers are
present, they will be in the order just given (e.g. 'control_shift_click'). The
methods are called whenever the user mouses over the tag in a ShellItem and
clicks on it.

Access to the parent item and shell are available through the 'shell_item' and
'shell' facets respectively.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Any, Property, Str

#-------------------------------------------------------------------------------
#  'ShellTag' class:
#-------------------------------------------------------------------------------

class ShellTag ( HasPrivateFacets ):
    """ Defines the ShellTag base class used to define the objects associated
        with tags in a ShellItem's content.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The shell item the tag is associated with:
    shell_item = Any # Instance( ShellItem )

    # The shell associated with the tag:
    shell = Property

    # The tooltip associated with the tag:
    tooltip = Str

    #-- Public Methods ---------------------------------------------------------

    def on_click ( self, event ):
        """ Handles the user left-clicking on the tag.
        """
        self._method_for( 'click', event )


    def on_right_click ( self, event ):
        """ Handles the user right-clicking on the tag.
        """
        self._method_for( 'right_click', event )

    #-- Property Implementations -----------------------------------------------

    def _get_shell ( self ):
        return self.shell_item.shell

    #-- Private Methods --------------------------------------------------------

    def _method_for ( self, name, event ):
        """ Invokes the method corresponding to the specified base *name* and
            *event*.
        """
        modifier = ''
        if event.alt_down:
            modifier = 'alt_'

        if event.control_down:
            modifier += 'control_'

        if event.shift_down:
            modifier += 'shift_'

        method = getattr( self, modifier + name, None )
        if method is not None:
            method()

#-- EOF ------------------------------------------------------------------------
