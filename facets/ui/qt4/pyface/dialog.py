"""
The Qt toolkit specific implementation of a Dialog. See the IDialog interface
for the API documentation.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4. QtCore \
    import Qt

from PyQt4.QtGui \
    import QDialog, QMessageBox, QDialogButtonBox, QVBoxLayout, QWidget, \
           QPalette, QColor

from facets.core_api \
    import Bool, Enum, implements, Int, Str, Unicode

from facets.ui.pyface.i_dialog \
    import IDialog, MDialog

from facets.ui.pyface.constant \
    import OK, CANCEL, YES, NO

from window \
    import Window

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Map PyQt dialog related constants to the pyface equivalents:
_RESULT_MAP = {
    QDialog.Accepted:   OK,
    QDialog.Rejected:   CANCEL,
    QMessageBox.Ok:     OK,
    QMessageBox.Cancel: CANCEL,
    QMessageBox.Yes:    YES,
    QMessageBox.No:     NO
}

#-------------------------------------------------------------------------------
#  'Dialog' class:
#-------------------------------------------------------------------------------

class Dialog ( MDialog, Window ):
    """ The toolkit specific implementation of a Dialog.  See the IDialog
        interface for the API documentation.
    """

    implements( IDialog )

    #-- IDialog Interface ------------------------------------------------------

    cancel_label = Unicode
    help_id      = Str
    help_label   = Unicode
    ok_label     = Unicode
    resizeable   = Bool( True )
    return_code  = Int( OK )
    style        = Enum( 'modal', 'nonmodal' )

    #-- IWindow Interface ------------------------------------------------------

    title = Unicode( "Dialog" )

    def show ( self, visible ):
        if visible and (self.style == 'modal'):
            self.control.setWindowModality( Qt.ApplicationModal )

        super( Dialog, self ).show( visible )

    #-- Protected IDialog Interface --------------------------------------------

    def _create_buttons ( self, parent ):
        buttons = QDialogButtonBox()

        # 'OK' button.
        # FIXME v3: Review how this is supposed to work for non-modal dialogs
        # (ie. how does anything act on a button click?)
        if self.ok_label:
            btn = buttons.addButton( self.ok_label,
                                     QDialogButtonBox.AcceptRole )
        else:
            btn = buttons.addButton( QDialogButtonBox.Ok )

        btn.setDefault( True )

        # 'Cancel' button.
        # FIXME v3: Review how this is supposed to work for non-modal dialogs
        # (ie. how does anything act on a button click?)
        if self.cancel_label:
            buttons.addButton( self.cancel_label, QDialogButtonBox.RejectRole )
        else:
            buttons.addButton( QDialogButtonBox.Cancel )

        # 'Help' button.
        # FIXME v3: In the original code the only possible hook into the help
        # was to reimplement self._on_help().  However this was a private
        # method.  Obviously nobody uses the Help button.  For the moment we
        # display it but can't actually use it.
        if len( self.help_id ) > 0:
            if self.help_label:
                buttons.addButton( self.help_label, QDialogButtonBox.HelpRole )
            else:
                buttons.addButton( QDialogButtonBox.Help )

        return buttons


    def _create_contents ( self, parent ):
        lay = QVBoxLayout()

        lay.addWidget( self._create_dialog_area( parent ) )
        lay.addWidget( self._create_buttons( parent ) )

        parent.setLayout( lay )


    def _create_dialog_area ( self, parent ):
        panel = QWidget( parent )

        palette = panel.palette()
        palette.setColor( QPalette.Window, QColor( 'red' ) )
        panel.setPalette( palette )
        panel.setAutoFillBackground( True )

        return panel


    def _show_modal ( self ):
        return _RESULT_MAP[ self.control.exec_() ]

    #-- Protected IWidget Interface --------------------------------------------

    def _create_control ( self, parent ):
        dlg = QDialog( parent )

        if self.size != ( -1, -1 ):
            dlg.resize( *self.size )

        # FIXME v3: Decide what to do with the resizable facet (ie. set the
        # size policy):
        dlg.setWindowTitle( self.title )

        return dlg

#-- EOF ------------------------------------------------------------------------