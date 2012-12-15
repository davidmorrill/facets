"""
Defines a HyperlinkEditor which displays a string which can contain hyperlinks
to web pages which when clicked will open in an external browser window.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide.QtCore \
    import QObject, QUrl, SIGNAL

from PySide.QtGui \
    import QLabel, QDesktopServices

from facets.api \
    import Str, Editor, BasicEditorFactory

#-------------------------------------------------------------------------------
#  '_HyperlinkEditor' class:
#-------------------------------------------------------------------------------

class _HyperlinkEditor ( Editor ):
    """ Displays a string which can contain hyperlinks to web pages which when
        clicked will open in an external browser window.
    """

    #-- Editor Method Overrides ------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = control = QLabel( parent() )
        QObject.connect( control, SIGNAL( 'linkActivated(QString)' ),
                         self._link_activated )

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        label = self.factory.label
        if label == '':
            label = self.value_text

        self.control.setText( label )

    #-- Private Methods --------------------------------------------------------

    def _link_activated ( self, url ):
        """ Handles the user clicking on a hyperlink.
        """
        QDesktopServices.openUrl( QUrl( url ) )
        if self.factory.label != '':
            self.value = unicode( url )

#-------------------------------------------------------------------------------
#  'HyperlinkEditor' class:
#-------------------------------------------------------------------------------

class HyperlinkEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _HyperlinkEditor

    # The optional label for the hyperlink (if not the empty string, then the
    # 'value' of the editor is ignored):
    label = Str

#-- EOF ------------------------------------------------------------------------