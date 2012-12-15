"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

# Standard library imports:
import sys

# Major package imports:
from PyQt4 \
    import QtCore, QtGui

# Facets library imports:
from facets.core_api \
    import implements, Instance, List, Unicode

# Local imports:
from facets.ui.pyface.i_about_dialog \
    import IAboutDialog, MAboutDialog

from facets.ui.pyface.image_resource \
    import ImageResource

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.ui.ui_facets \
    import Image

from dialog \
    import Dialog


# The HTML displayed in the QLabel.
_DIALOG_TEXT = '''
<html>
  <body>
    <center>
      <table width="100%%" cellspacing="4" cellpadding="0" border="0">
        <tr>
          <td align="center">
          <p>
            <img src="%s" alt="">
          </td>
        </tr>
      </table>

      <p>
      %s<br>
      <br>
      Python %s<br>
      PyQt %s<br>
      Qt %s<br>
      </p>
  </center>
  </body>
</html>
'''


class AboutDialog ( MAboutDialog, Dialog ):
    """ The toolkit specific implementation of an AboutDialog.  See the
    IAboutDialog interface for the API documentation.
    """

    implements( IAboutDialog )

    #-- 'IAboutDialog' interface -----------------------------------------------

    additions = List( Unicode )

    image = Image

    #---------------------------------------------------------------------------
    # Protected 'IDialog' interface.
    #---------------------------------------------------------------------------

    def _create_contents ( self, parent ):
        label = QtGui.QLabel()

        if self.title == 'Dialog':
            title = ''
            if parent.parent() is not None:
                title = parent.parent().windowTitle()

            # Set the title.
            self.title = "About %s" % title

        # Load the image to be displayed in the about box.
        image = self.image.create_image()
        path  = self.image.absolute_path

        # The additional strings.
        additions = '<br />'.join( self.additions )

        # Get the version numbers.
        py_version   = sys.version[ 0: sys.version.find( "(" ) ]
        pyqt_version = QtCore.PYQT_VERSION_STR
        qt_version   = QtCore.QT_VERSION_STR

        # Set the page contents.
        label.setText( _DIALOG_TEXT % (
                       path, additions, py_version, pyqt_version, qt_version ) )

        # Create the button.
        buttons = QtGui.QDialogButtonBox()

        if self.ok_label:
            buttons.addButton( self.ok_label,
                               QtGui.QDialogButtonBox.AcceptRole )
        else:
            buttons.addButton( QtGui.QDialogButtonBox.Ok )

        buttons.connect( buttons, QtCore.SIGNAL( 'accepted()' ), parent,
                         QtCore.SLOT( 'accept()' ) )

        lay = QtGui.QVBoxLayout()
        lay.addWidget( label )
        lay.addWidget( buttons )

        parent.setLayout( lay )

#-- EOF ------------------------------------------------------------------------