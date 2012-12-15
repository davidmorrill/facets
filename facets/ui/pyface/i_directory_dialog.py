"""
The interface for a dialog that allows the user to browse for a directory.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Bool, Unicode

from i_dialog \
    import IDialog

#-------------------------------------------------------------------------------
#  'IDirectoryDialog' class:
#-------------------------------------------------------------------------------

class IDirectoryDialog ( IDialog ):
    """ The interface for a dialog that allows the user to browse for a
        directory.
    """

    #-- 'IDirectoryDialog' interface -------------------------------------------

    # The default path.  The default (ie. the default default path) is toolkit
    # specific.
    # FIXME v3: The default should be the current directory.  (It seems wx is
    # the problem, although the file dialog does the right thing.)
    default_path = Unicode

    # The message to display in the dialog.  The default is toolkit specific.
    message = Unicode

    # True iff the dialog should include a button that allows the user to
    # create a new directory.
    new_directory = Bool( True )

    # The path of the chosen directory.
    path = Unicode

#-------------------------------------------------------------------------------
#  'MDirectoryDialog' class:
#-------------------------------------------------------------------------------

class MDirectoryDialog ( object ):
    """ The mixin class that contains common code for toolkit specific
        implementations of the IDirectoryDialog interface.
    """

#-- EOF ------------------------------------------------------------------------