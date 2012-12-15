"""
A simple progress bar intended to run in the UI thread
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import time

from PyQt4.QtGui \
    import QProgressBar, QDialog, QDialogButtonBox, QLabel, QHBoxLayout, \
           QVBoxLayout

from PyQt4.QtCore \
    import QRect, SIGNAL, SLOT, Qt

from facets.core_api \
    import Instance, Int, Bool, Unicode

from facets.ui.pyface.i_progress_dialog \
    import MProgressDialog

from window \
    import Window

#-------------------------------------------------------------------------------
#  'ProgressDialog' class:
#-------------------------------------------------------------------------------

class ProgressDialog ( MProgressDialog, Window ):
    """ A simple progress dialog window which allows itself to be updated

        FIXME: buttons are not set up correctly yet
    """

    #-- Facet Definitions ------------------------------------------------------

    progress_bar    = Instance( QProgressBar )
    title           = Unicode
    message         = Unicode
    min             = Int
    max             = Int
    margin          = Int( 5 )
    can_cancel      = Bool( False )
    show_time       = Bool( False )
    show_percent    = Bool( False )
    _user_cancelled = Bool( False )
    dialog_size     = Instance( QRect )

    # Label for the 'cancel' button
    cancel_button_label = Unicode( 'Cancel' )

    #-- Public Methods ---------------------------------------------------------

    def open ( self ):
        super( ProgressDialog, self ).open()
        self._start_time = time.time()


    def close ( self ):
        self.progress_bar.destroy()
        self.progress_bar = None

        super( ProgressDialog, self ).close()


    def update ( self, value ):
        """
        Updates the progress bar to the desired value. If the value is >=
        the maximum and the progress bar is not contained in another panel
        the parent window will be closed

        """

        if self.progress_bar is None:
            return ( None, None )

        self.progress_bar.setValue( value )

        percent = (float( value ) - self.min) / (self.max - self.min)

        if self.show_time and (percent != 0):
            current_time = time.time()
            elapsed      = current_time - self._start_time
            estimated    = elapsed / percent
            remaining    = estimated - elapsed

            self._set_time_label( elapsed,   self._elapsed_control )
            self._set_time_label( estimated, self._estimated_control )
            self._set_time_label( remaining, self._remaining_control )
            self._message_control.setText( self.message )

        if self.show_percent:
            self._percent_control = "%3f" % ((percent * 100) % 1)

        if (value >= self.max) or self._user_cancelled:
            self.close()

        return ( not self._user_cancelled, False )


    def reject ( self, event ):
        self._user_cancelled = True
        self.close()


    def _set_time_label ( self, value, control ):
        hours   = value / 3600
        minutes = (value % 3600) / 60
        seconds = value % 60
        label   = "%1u:%02u:%02u" % ( hours, minutes, seconds )

        control.setText( control.text()[:-7] + label )


    def _create_buttons ( self, dialog, layout ):
        """ Creates the buttons.
        """
        # Create the button:
        buttons = QDialogButtonBox()

        if self.can_cancel:
            buttons.addButton( self.cancel_button_label,
                               QDialogButtonBox.RejectRole )

        buttons.addButton( QDialogButtonBox.Ok )

        # TODO: hookup the buttons to our methods, this may involve subclassing
        # from QDialog

        if self.can_cancel:
            buttons.connect( buttons, SIGNAL( 'rejected()' ), dialog,
                             SLOT( 'reject() ' ) )
        buttons.connect( buttons, SIGNAL( 'accepted()' ), dialog,
                         SLOT( 'accept()' ) )

        layout.addWidget( buttons )


    def _create_label ( self, dialog, layout, text ):
        dummy = QLabel( text, dialog )
        dummy.setAlignment( Qt.AlignTop | Qt.AlignLeft )

        label = QLabel( "unknown", dialog )
        label.setAlignment( Qt.AlignTop | Qt.AlignLeft | Qt.AlignRight )

        sub_layout = QHBoxLayout()

        sub_layout.addWidget( dummy )
        sub_layout.addWidget( label )

        layout.addLayout( sub_layout )

        return label


    def _create_gauge ( self, dialog, layout ):
        self.progress_bar = QProgressBar( dialog )
        self.progress_bar.setRange( self.min, self.max )
        layout.addWidget( self.progress_bar )


    def _create_message ( self, dialog, layout ):
        label = QLabel( self.message, dialog )
        label.setAlignment( Qt.AlignTop | Qt.AlignLeft )
        layout.addWidget( label )
        self._message_control = label


    def _create_percent ( self, dialog, layout ):
        #not an option with the QT progress bar
        return


    def _create_timer ( self, dialog, layout ):
        if not self.show_time:
            return

        self._elapsed_control   = self._create_label( dialog, layout,
                                                      "Elapsed time : " )
        self._estimated_control = self._create_label( dialog, layout,
                                                      "Estimated time : " )
        self._remaining_control = self._create_label( dialog, layout,
                                                      "Remaining time : " )


    def _create_control ( self, parent ):
        control = QDialog( parent )
        control.setWindowTitle( self.title )

        return control


    def _create ( self ):
        super( ProgressDialog, self )._create()

        contents = self._create_contents( self.control )


    def _create_contents ( self, parent ):
        dialog = parent
        layout = QVBoxLayout( dialog )

        # The 'guts' of the dialog:
        self._create_message( dialog, layout )
        self._create_gauge(   dialog, layout )
        self._create_percent( dialog, layout )
        self._create_timer(   dialog, layout )
        self._create_buttons( dialog, layout )

        parent.setLayout( layout )

#-- EOF ------------------------------------------------------------------------