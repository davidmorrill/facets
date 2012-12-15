"""
The interface for a dialog that prompts the user for confirmation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Bool, Enum, Unicode, Image

from constant \
    import CANCEL, NO, YES

from i_dialog \
    import IDialog

#-------------------------------------------------------------------------------
#  'IConfirmationDialog' class:
#-------------------------------------------------------------------------------

class IConfirmationDialog ( IDialog ):
    """ The interface for a dialog that prompts the user for confirmation.
    """

    #-- 'IConfirmationDialog' Interface ----------------------------------------

    # Should the cancel button be displayed?
    cancel = Bool( False )

    # The default button:
    default = Enum( NO, YES, CANCEL )

    # The image displayed with the message. The default is toolkit specific.
    image = Image

    # The message displayed in the body of the dialog (use the inherited
    # 'title' facet to set the title of the dialog itself):
    message = Unicode

    # The label for the 'no' button. The default is toolkit specific:
    no_label = Unicode

    # The label for the 'yes' button. The default is toolkit specific:
    yes_label = Unicode

#-------------------------------------------------------------------------------
#  'MConfirmationDialog' class:
#-------------------------------------------------------------------------------

class MConfirmationDialog ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IConfirmationDialog interface.
    """

#-- EOF ------------------------------------------------------------------------