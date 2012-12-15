"""
The implementation of a dialog that displays a message.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def information ( parent, message, title = 'Information' ):
    """ Convenience function to show an information message dialog.
    """
    MessageDialog(
        parent   = parent and parent(),
        message  = message,
        title    = title,
        severity = 'information'
    ).open()


def warning ( parent, message, title = 'Warning' ):
    """ Convenience function to show a warning message dialog.
    """
    MessageDialog(
        parent   = parent and parent(),
        message  = message,
        title    = title,
        severity = 'warning'
    ).open()


def error ( parent, message, title = 'Error' ):
    """ Convenience function to show an error message dialog.
    """
    MessageDialog(
        parent   = parent and parent(),
        message  = message,
        title    = title,
        severity = 'error'
    ).open()

#-------------------------------------------------------------------------------
#  Define the GUI toolkit specific implementation:
#-------------------------------------------------------------------------------

from toolkit \
    import toolkit_object

MessageDialog = toolkit_object( 'message_dialog:MessageDialog' )

#-- EOF ------------------------------------------------------------------------