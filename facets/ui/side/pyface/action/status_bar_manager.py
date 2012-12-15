"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PySide \
    import QtGui

from facets.core_api \
    import Any, HasFacets, List, Property, Str, Unicode

#-------------------------------------------------------------------------------
#  'StatusBarManager' class:
#-------------------------------------------------------------------------------

class StatusBarManager ( HasFacets ):
    """ A status bar manager realizes itself in a status bar control. """

    # FIXME v3: Is this used anywhere?
    # The manager's unique identifier (if it has one).
    id = Str

    # The message displayed in the first field of the status bar.
    message = Property

    # The messages to be displayed in the status bar fields.
    messages = List( Unicode )

    # The toolkit-specific control that represents the status bar.
    status_bar = Any

    #-- StatusBarManager Interface ---------------------------------------------

    def create_status_bar ( self, parent ):
        """ Creates a status bar. """

        if self.status_bar is None:
            self.status_bar = QtGui.QStatusBar( parent )
            self.status_bar.setSizeGripEnabled( False )

            if len( self.messages ) > 1:
                self._show_messages()
            else:
                self.status_bar.showMessage( self.message )

        return self.status_bar

    #-- Property Implementations -----------------------------------------------

    def _get_message ( self ):

        if len( self.messages ) > 0:
            message = self.messages[ 0 ]
        else:
            message = ''

        return message

    def _set_message ( self, value ):

        if len( self.messages ) > 0:
            old = self.messages[ 0 ]
            self.messages[ 0 ] = value
        else:
            old = ''
            self.messages.append( old )

        self.facet_property_set( 'message', old, value )

    #-- Facet Event Handlers ---------------------------------------------------

    def _messages_set ( self ):
        """ Sets the text displayed on the status bar. """

        if self.status_bar is not None:
            self._show_messages()

    def _messages_items_set ( self ):
        """ Sets the text displayed on the status bar. """

        if self.status_bar is not None:
            self._show_messages()

    #-- Private Methods --------------------------------------------------------

    def _show_messages ( self ):
        """ Display the list of messages. """

        # FIXME v3: At the moment we just string them together but we may
        # decide to put all but the first message into separate widgets.  We
        # probably also need to extend the API to allow a "message" to be a
        # widget - depends on what wx is capable of.
        self.status_bar.showMessage( "  ".join( self.messages ) )

#-- EOF ------------------------------------------------------------------------