"""
A status bar manager realizes itself in a status bar control.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.core_api \
    import Any, HasFacets, List, Property, Str, Unicode

#-------------------------------------------------------------------------------
#  'StatusBarManager' class:
#-------------------------------------------------------------------------------

class StatusBarManager ( HasFacets ):
    """ A status bar manager realizes itself in a status bar control.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The manager's unique identifier (if it has one):
    id = Str

    # The message displayed in the first field of the status bar:
    message = Property

    # The messages to be displayed in the status bar fields:
    messages = List( Unicode )

    # The toolkit-specific control that represents the status bar:
    status_bar = Any

    #-- 'StatusBarManager' Interface -------------------------------------------

    def create_status_bar ( self, parent ):
        """ Creates a status bar.
        """
        if self.status_bar is None:
            self.status_bar = wx.StatusBar( parent )
            self.status_bar._pyface_control = self
            if len( self.messages ) > 1:
                self.status_bar.SetFieldsCount( len( self.messages ) )
                for i in range( len( self.messages ) ):
                    self.status_bar.SetStatusText( self.messages[ i ], i )
            else:
                self.status_bar.SetStatusText( self.message )

        return self.status_bar

    #-- Property Implementations -----------------------------------------------

    def _get_message ( self ):
        """ Property getter.
        """
        if len( self.messages ) > 0:
            message = self.messages[ 0 ]

        else:
            message = ''

        return message

    def _set_message ( self, value ):
        """ Property setter.
        """
        if len( self.messages ) > 0:
            old = self.messages[ 0 ]
            self.messages[ 0 ] = value

        else:
            old = ''
            self.messages.append( value )

        self.facet_property_set( 'message', old, value )

    #-- Facet Event Handlers ---------------------------------------------------

    def _messages_set ( self ):
        """ Sets the text displayed on the status bar.
        """
        if self.status_bar is not None:
            for i in range( len( self.messages ) ):
                self.status_bar.SetStatusText( self.messages[ i ], i )


    def _messages_items_set ( self ):
        """ Sets the text displayed on the status bar.
        """
        self._messages_set()

#-- EOF ------------------------------------------------------------------------