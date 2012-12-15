"""
Defines the *information*, *warning*, *error* and *question* functions for
displaying various types of messages in a non-modal, stand-alone dialog.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Any, Str, Either, Enum, Event, Button, Float, List, Instance,  \
           Theme, Handler, UIInfo, View, HGroup, UItem, ThemedTextEditor, \
           ProgressBarEditor, spring, on_facet_set

from facets.ui.view \
    import Unspecified

#-------------------------------------------------------------------------------
#  'MessageDialog' class:
#-------------------------------------------------------------------------------

class MessageDialog ( Handler ):
    """ Defines a Facets-based message dialog for information, warning and
        error messages.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The message to display:
    message = Str

    # The title of the message dialog:
    title = Str

    # The kind of message being displayed:
    kind = Enum( 'info', 'warning', 'error', 'question', 'progress' )

    # The button labels to display in the message dialog (either a single string
    # or a list of up to four strings):
    buttons = Either( Str, List, default = 'OK' )

    # The parent control for the message dialog:
    parent = Any

    # The result returned by the dialog (i.e. 'Close' or the label of the button
    # that was clicked):
    result = Event

    # The persistence id to associate with the message dialog:
    id = Str

    # The lowest value for a progress bar:
    low = Float( 0.0 )

    # The highest value for a progress bar:
    high = Float( 100.0 )

    # The current value of a progress bar:
    value = Float( 0.0 )

    #-- Private Facets Definitions ---------------------------------------------

    # The UIInfo object associated with an open message dialog:
    ui_info = Instance( UIInfo )

    # The most recent position of the message dialog on the screen:
    xy = Any( ( Unspecified, Unspecified ) )

    # The list of button labels:
    button_labels = Any # List( Str )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        x, y  = self.xy
        items = [ spring ] + [ UItem( 'b%d' % i )
                               for i in xrange( len( self.button_labels ) ) ]

        if self.kind == 'progress':
            width     = 0.33
            main_item = UItem( 'value',
                editor = ProgressBarEditor( low = self.low, high = self.high )
            )
        else:
            width     = Unspecified
            main_item = UItem( 'message',
                style  = 'readonly',
                editor = ThemedTextEditor(
                    theme = Theme( '@xform:b?L50', content = ( 6, 12, 8, 8 ) ),
                    image = '@facets:' + self.kind
                )
            )

        return View(
            main_item,
            HGroup(
                group_theme = '@xform:b?L30',
                *items
            ),
            title = self.title,
            id    = self.id,
            x     = x,
            y     = y,
            width = width
        )

    #-- Facet Default Values ---------------------------------------------------

    def _button_labels_default ( self ):
        buttons = self.buttons
        if isinstance( buttons, basestring ):
            buttons = [ buttons ]

        return buttons

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        """ Initializes the object.
        """
        for i, button in enumerate( self.button_labels ):
            facet = 'b%d' % i
            self.add_facet( facet, Button( button, button_label = button ) )
            self.on_facet_set( self._button_clicked, facet )

    #-- Handler Method Overrides -----------------------------------------------

    def init_info ( self, ui_info ):
        self.ui_info = ui_info


    def close ( self, info, is_ok ):
        self.ui_info = None
        if info.ui is not None:
            self.xy     = info.ui.control.screen_position
            self.result = 'Close'

        return True


    def dispose ( self ):
        """ Explicitly closes the dialog.
        """
        self.xy = self.ui_info.ui.control.screen_position
        self.ui_info.ui.dispose()

    #-- Facet Event Handlers ---------------------------------------------------

    def _button_clicked ( self, facet ):
        """ Handles any of the dialog buttons being clicked.
        """
        label  = self.facet( facet ).button_label
        result = label.strip()
        if result == label:
            self.dispose()

        self.result = result


    @on_facet_set( 'message, value' )
    def show ( self ):
        if ((self.ui_info is None) and
            ((self.kind == 'progress') or (self.message != ''))):
            self.edit_facets( parent = self.parent )

        return self

#-------------------------------------------------------------------------------
#  Function definitions:
#-------------------------------------------------------------------------------

def information ( parent, message = '', title = 'Information', buttons = 'OK',
                          id      = '' ):
    """ Displays an information message.
    """
    return message_dialog( parent, message, title, 'info', buttons, id )


def warning ( parent, message = '', title = 'Warning', buttons = 'OK',
                      id      = '' ):
    """ Displays a warning message.
    """
    return message_dialog( parent, message, title, 'warning', buttons, id )


def error ( parent, message = '', title = 'Error', buttons = 'OK',
                    id      = '' ):
    """ Displays an error message.
    """
    return message_dialog(
        parent, message, title, 'error', buttons, id
    )


def question ( parent, message = '', title = 'Question',
               buttons = [ 'Yes', 'No' ], id = '' ):
    """ Displays a question.
    """
    return message_dialog( parent, message, title, 'question', buttons, id )


def progress ( parent, message = '', title = 'Progress', buttons = 'Stop',
               id = '', low = 0.0, high = 100.0 ):
    """ Displays a progress bar.
    """
    return message_dialog(
        parent, message, title, 'progress', buttons, id, low, high
    )

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def message_dialog ( parent = None,   message = '', title = 'Information',
                     kind   = 'info', buttons = 'OK', id = '', low = 0.0,
                     high = 100.0 ):
    """ Displays a generic informational message.
    """
    return MessageDialog(
        parent  = parent,
        message = message,
        title   = title,
        kind    = kind,
        buttons = buttons,
        id      = id,
        low     = low,
        high    = high
    ).show()

#-- EOF ------------------------------------------------------------------------
