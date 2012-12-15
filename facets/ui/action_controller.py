"""
Defines the ActionController class which a user interface object can use to
delegate the implementation of the Action 'controller' interface to.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from traceback \
    import print_exc

from facets.api \
    import HasPrivateFacets, Any, Dict, Instance, UI

#-------------------------------------------------------------------------------
#  'ActionController' class:
#-------------------------------------------------------------------------------

class ActionController ( HasPrivateFacets ):
    """ Defines the ActionController class which a user interface object can use
        to delegate the implementation of the Action 'controller' interface to.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The context dictionary to use when executing or evaluating an Action:
    context = Dict

    # The user interface object associated with the set of actions:
    ui = Instance( UI )

    # The object that should be passed to an Action's 'on_perform' method:
    object = Any

    #-- pyface.action 'controller' Interface Implementation --------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        action = menu_item.item.action
        self._eval_when( action.enabled_when, menu_item, 'enabled' )
        self._eval_when( action.checked_when, menu_item, 'checked' )


    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a toolbar item to the toolbar being constructed.
        """
        self.add_to_menu( toolbar_item )


    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        for condition in ( action.defined_when, action.visible_when ):
            if condition != '':
                try:
                    if not eval( condition, globals(), self.context ):
                        return False
                except:
                    print_exc()

        return True


    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return self.can_add_to_menu( action )


    def perform ( self, action ):
        """ Performs the action described by a specified Action object.
        """
        method_name = action.action
        if method_name.find( '.' ) >= 0:
            if method_name.find( '(' ) < 0:
                method_name += '()'

            try:
                eval( method_name, globals(), self.context )
            except:
                print_exc()

            return

        method = getattr( self.ui.handler, method_name, None )
        if method is not None:
            method( self.ui.info, self.object )

            return

        if action.on_perform is not None:
            action.on_perform( self.object )

    #-- Private Methods --------------------------------------------------------

    def _eval_when ( self, condition, object, facet ):
        """ Evaluates a condition within a defined context, and sets a
            specified object facet based on the result, which is assumed to be a
            boolean value.
        """
        if condition != '':
            value = True
            try:
                if not eval( condition, globals(), self.context ):
                    value = False
            except:
                print_exc()

            setattr( object, facet, value )

#-- EOF ------------------------------------------------------------------------
