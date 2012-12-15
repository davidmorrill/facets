"""
An action manager item that represents an actual action.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Any, Instance, List, Property, Str

from action \
    import Action

from action_manager_item \
    import ActionManagerItem

from facets.ui.pyface.toolkit \
    import toolkit_object

#-------------------------------------------------------------------------------
#  Defines the GUI toolkit specific implementation:
#-------------------------------------------------------------------------------

_MenuItem    = toolkit_object( 'action.action_item:_MenuItem' )
_Tool        = toolkit_object( 'action.action_item:_Tool' )
_PaletteTool = toolkit_object( 'action.action_item:_PaletteTool' )

#-------------------------------------------------------------------------------
#  'ActionItem' class:
#-------------------------------------------------------------------------------

class ActionItem ( ActionManagerItem ):
    """ An action manager item that represents an actual action.
    """

    #-- 'ActionManagerItem' interface ------------------------------------------

    # The item's unique identifier ('unique' in this case means unique within
    # its group).
    id = Property( Str )

    #-- 'ActionItem' interface -------------------------------------------------

    # The action!
    action = Instance( Action )

    # The toolkit specific control created for this item:
    control = Any

    # The toolkit specific Id of the control created for this item:
    #
    # We have to keep the Id as well as the control because wx tool bar tools
    # are created as 'wxObjectPtr's which do not have Ids, and the Id is
    # required to manipulate the state of a tool via the tool bar 8^(
    # FIXME v3: Why is this part of the public interface?
    control_id = Any

    #-- Private Facets ---------------------------------------------------------

    # All of the internal instances that wrap this item:
    _wrappers = List( Any )

    #-- 'ActionManagerItem' Interface ------------------------------------------

    #-- Property Implementations -----------------------------------------------

    def _get_id ( self ):
        """ Return's the item's Id.
        """
        return self.action.id

    #-- Facet Event Handlers ---------------------------------------------------

    def _enabled_set ( self, enabled ):
        """ Handles the 'enabled' facet being modified.
        """
        self.action.enabled = enabled


    def _visible_set ( self ):
        """ Handles the 'visible' facet being changed.
        """
        self.action.visible = True  # Should this be 'self.visible'?

    #-- 'ActionItem' Interface -------------------------------------------------

    def add_to_menu ( self, parent, menu, controller ):
        """ Adds the item to a menu.
        """
        if (controller is None) or controller.can_add_to_menu( self.action ):
            wrapper = _MenuItem( parent, menu, self, controller )

            # fixme: Martin, who uses this information?
            if controller is None:
                self.control    = wrapper.control
                self.control_id = wrapper.control_id

            self._wrappers.append( wrapper )


    def add_to_toolbar ( self, parent, tool_bar, image_cache, controller,
                               show_labels = True ):
        """ Adds the item to a tool bar.
        """
        if (controller is None) or controller.can_add_to_toolbar( self.action ):
            wrapper = _Tool(
                parent, tool_bar, image_cache, self, controller, show_labels
            )

            # fixme: Martin, who uses this information?
            if controller is None:
                self.control    = wrapper.control
                self.control_id = wrapper.control_id

            self._wrappers.append( wrapper )


    def add_to_palette ( self, tool_palette, image_cache, show_labels = True ):
        """ Adds the item to a tool palette.
        """
        wrapper = _PaletteTool( tool_palette, image_cache, self, show_labels )
        self._wrappers.append( wrapper )


    def destroy ( self ):
        """ Called when the action is no longer required.

            By default this method calls 'destroy' on the action itself.
        """
        self.action.destroy()

#-- EOF ------------------------------------------------------------------------