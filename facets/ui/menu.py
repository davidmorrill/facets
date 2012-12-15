"""
Defines the standard menu bar for use with Facets UI windows and panels,
    and standard actions and buttons.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

# Import and rename the needed PyFace elements:
from facets.ui.pyface.action.api \
    import ToolBarManager as ToolBar

from facets.ui.pyface.action.api \
    import MenuBarManager as MenuBar

from facets.ui.pyface.action.api \
    import MenuManager as Menu

from facets.ui.pyface.action.api \
    import Group as ActionGroup

from facets.ui.pyface.action.api \
    import Action

#-------------------------------------------------------------------------------
#  Standard actions and menu bar definitions:
#-------------------------------------------------------------------------------

# Menu separator:
Separator = ActionGroup

# The standard "close window" action:
CloseAction = Action(
    name   = 'Close',
    action = '_on_close'
)


# The standard "undo last change" action:
UndoAction = Action(
    name         = 'Undo',
    action       = '_on_undo',
    defined_when = 'ui.history is not None',
    enabled_when = 'ui.history.can_undo'
)


# The standard "redo last undo" action:
RedoAction = Action(
    name         = 'Redo',
    action       = '_on_redo',
    defined_when = 'ui.history is not None',
    enabled_when = 'ui.history.can_redo'
)


# The standard "revert all changes" action:
RevertAction = Action(
    name         = 'Revert',
    action       = '_on_revert',
    defined_when = 'ui.history is not None',
    enabled_when = 'ui.history.can_undo'
)


# The standard "show help" action:
HelpAction = Action(
    name   = 'Help',
    action = 'show_help'
)


# Manages the current window layouts:
ManageLayoutsAction = Action(
    name         = 'Manage layouts...',
    action       = '_on_manage_layouts',
    enabled_when = "(ui.id != '') and (ui.dock_window is not None)"
)


# Select the DockWindow theme to use:
SelectThemeAction = Action(
    name         = 'Select theme...',
    action       = '_on_select_theme',
    enabled_when = "ui.dock_window is not None"
)


# The standard Facets UI menu bar:
StandardMenuBar = MenuBar(
    Menu( CloseAction,
          name = 'File' ),
    Menu( UndoAction,
          RedoAction,
          RevertAction,
          name = 'Edit' ),
    Menu( ManageLayoutsAction,
          SelectThemeAction,
          name = 'View'
    ),
    Menu( HelpAction,
          name = 'Help' )
)

# The standard "save user preferences" action:
SavePreferencesAction = Action(
    name         = 'Save user preferences',
    action       = '_on_save_preferences',
    defined_when = "ui.id != ''"
)

#-------------------------------------------------------------------------------
#  Standard buttons (i.e. actions):
#-------------------------------------------------------------------------------

NoButton = Action( name = '' )


# Appears as two buttons: **Undo** and **Redo**. When **Undo** is clicked, the
# most recent change to the data is cancelled, restoring the previous value.
# **Redo** cancels the most recent "undo" operation.
UndoButton = Action( name = 'Undo' )


# When the user clicks the **Revert** button, all changes made in the window are
# cancelled and the original values are restored. If the changes have been
# applied to the model (because the user clicked **Apply** or because the window
# is live), the model data is restored as well. The window remains open.
RevertButton = Action( name = 'Revert' )


# When theuser clicks the **Apply** button, all changes made in the window are
# applied to the model. This option is meaningful only for modal windows.
ApplyButton = Action( name = 'Apply' )


# When the user clicks the **OK** button, all changes made in the window are
# applied to the model, and the window is closed.
OKButton = Action( name = 'OK' )


# When the user clicks the **Cancel** button, all changes made in the window
# are discarded; if the window is live, the model is restored to the values it
# held before the window was opened. The window is then closed.
CancelButton = Action( name = 'Cancel' )


# When the user clicks the **Help** button, the current help handler is
# invoked. If the default help handler is used, a pop-up window is displayed,
# which contains the **help** text for the top-level Group (if any), and for
# the items in the view. If the default help handler has been overridden,
# the action is determined by the custom help handler. See
# **facets.ui.help**.
HelpButton = Action( name = 'Help' )


OKCancelButtons = [ OKButton, CancelButton ]
ModalButtons = [ ApplyButton, RevertButton, OKButton, CancelButton, HelpButton ]
LiveButtons  = [ UndoButton,  RevertButton, OKButton, CancelButton, HelpButton ]


# The window has no command buttons:
NoButtons = [ NoButton ]

#-- EOF ------------------------------------------------------------------------