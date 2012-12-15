"""
The implementation of a dialog that prompts the user for confirmation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from constant \
    import NO

from toolkit \
    import toolkit_object

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def confirm ( parent, message, title = None, cancel = False, default = NO ):
    """ Convenience function to show a confirmation dialog.
    """
    if title is None:
        title = "Confirmation"

    dialog = ConfirmationDialog(
        parent  = parent,
        message = message,
        cancel  = cancel,
        default = default,
        title   = title
    )

    return dialog.open()

#-------------------------------------------------------------------------------
#  Define the GUI toolkit specific implementation:
#-------------------------------------------------------------------------------

ConfirmationDialog = toolkit_object( 'confirmation_dialog:ConfirmationDialog' )

#-- EOF ------------------------------------------------------------------------