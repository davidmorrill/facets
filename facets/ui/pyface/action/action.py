"""
The base class for all actions.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Callable, Enum, HasFacets, Str, Unicode, Image

#-------------------------------------------------------------------------------
#  'Action' class:
#-------------------------------------------------------------------------------

class Action ( HasFacets ):
    """ The base class for all actions.

        An action is the non-UI side of a command which can be triggered by the
        end user.  Actions are typically associated with buttons, menu items and
        tool bar tools.

        When the user triggers the command via the UI, the action's 'perform'
        method is invoked to do the actual work.
    """

    #-- 'Action' interface -----------------------------------------------------

    # Keyboard accelerator (by default the action has NO accelerator):
    accelerator = Unicode

    # A longer description of the action (used for context sensitive help etc).
    # If no description is specified, the tooltip is used instead:
    description = Unicode

    # The method to call to perform the action, on the Handler for the window.
    # The method must accept a single parameter, which is a UIInfo object.
    # Because Actions are associated with Views rather than Handlers, you must
    # ensure that the Handler object for a particular window has a method with
    # the correct name, for each Action defined on the View for that window.
    action = Str

    # Is the action visible?
    visible = Bool( True )

    # Is the action enabled?
    enabled = Bool( True )

    # Is the action checked?  This is only relevant if the action style is
    # 'radio' or 'toggle'.
    checked = Bool( False )

    # Pre-condition for including the action in the menu bar or toolbar. If the
    # expression evaluates to False, the action is not defined in the display.
    # Conditions for **defined_when** are evaluated only once, when the display
    # is first constructed.
    defined_when = Str

    # Pre-condition for showing the action. If the expression evaluates to
    # False, the action is not visible (and disappears if it was previously
    # visible). If the value evaluates to True, the action becomes visible. All
    # **visible_when** conditions are checked each time that any facet value
    # is edited in the display. Therefore, you can use **visible_when**
    # conditions to hide or show actions in response to user input.
    visible_when = Str

    # Pre-condition for enabling the action. If the expression evaluates to
    # False, the action is disabled, that is, it cannot be selected. All
    # **enabled_when** conditions are checked each time that any facet value
    # is edited in the display. Therefore, you can use **enabled_when**
    # conditions to enable or disable actions in response to user input.
    enabled_when = Str

    # Boolean expression indicating when the action is displayed with a check
    # mark beside it. This attribute applies only to actions that are included
    # in menus.
    checked_when = Str

    # The action's name (displayed on menus/tool bar tools etc):
    name = Unicode

    # The action's unique identifier:
    id = Str

    # The action's image (displayed on tool bar tools, etc.):
    image = Image

    # An (optional) callable that will be invoked when the action is performed:
    on_perform = Callable

    # The action's style:
    style = Enum( 'push', 'radio', 'toggle' )

    # A short description of the action used for tooltip text, etc.:
    tooltip = Unicode

    #-- 'Action' Interface -----------------------------------------------------

    #-- Initializers -----------------------------------------------------------

    def _id_default ( self ):
        """ Initializes the 'id' facet.
        """
        return self.name

    #-- Methods ----------------------------------------------------------------

    def destroy ( self ):
        """ Called when the action is no longer required.

            By default this method does nothing, but this would be a great place to
            unhook facet listeners etc.
        """
        pass


    def perform ( self, event ):
        """ Performs the action.
        """
        if self.on_perform is not None:
            self.on_perform()

#-- EOF ------------------------------------------------------------------------