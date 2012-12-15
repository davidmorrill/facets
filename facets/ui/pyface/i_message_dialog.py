"""
The interface for a dialog that displays a message.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Enum, Unicode

from i_dialog \
    import IDialog

#-------------------------------------------------------------------------------
#  'IMessageDialog' class:
#-------------------------------------------------------------------------------

class IMessageDialog ( IDialog ):
    """ The interface for a dialog that displays a message.
    """

    #-- 'IMessageDialog' interface ---------------------------------------------

    # The message to display in the dialog.
    message = Unicode

    # The severity of the message.
    severity = Enum( 'information', 'warning', 'error' )

#-------------------------------------------------------------------------------
#  'MMessageDialog' class:
#-------------------------------------------------------------------------------

class MMessageDialog ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IMessageDialog interface.
    """

#-- EOF ------------------------------------------------------------------------