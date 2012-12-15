"""
Displays a message to the user as a modal window.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Str, Float

from view \
    import View

from group \
    import HGroup

from item \
    import Item, spring

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  'Message' class:
#-------------------------------------------------------------------------------

class Message ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The message to be displayed
    message = Str

#-------------------------------------------------------------------------------
#  Function Definitions:
#-------------------------------------------------------------------------------

def message ( message = '', title = 'Message', buttons = [ 'OK' ],
              parent  = None ):
    """ Displays a message to the user as a model window with the specified
        title and buttons.

        If *buttons* is not specified, a single **OK** button is used, which is
        appropriate for notifications, where no further action or decision on
        the user's part is required.
    """
    msg = Message( message = message )
    ui  = msg.edit_facets( parent = parent,
                           view   = View( [ 'message~', '|<>' ],
                                          title   = title,
                                          buttons = buttons,
                                          kind    = 'modal' ) )
    return ui.result


def error ( message = '', title = 'Message', buttons = [ 'OK', 'Cancel' ],
            parent  = None ):
    """ Displays a message to the user as a modal window with the specified
        title and buttons.

        If *buttons* is not specified, **OK** and **Cancel** buttons are used,
        which is appropriate for confirmations, where the user must decide
        whether to proceed. Be sure to word the message so that it is clear that
        clicking **OK** continues the operation.
    """
    msg = Message( message = message )
    ui  = msg.edit_facets( parent = parent,
                           view   = View( [ 'message~', '|<>' ],
                                          title   = title,
                                          buttons = buttons,
                                          kind    = 'modal' ) )
    return ui.result

#-------------------------------------------------------------------------------
#  'AutoCloseMessage' class:
#-------------------------------------------------------------------------------

class AutoCloseMessage ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The message to be shown:
    message = Str( 'Please wait' )

    # The time (in seconds) to show the message:
    time = Float( 2.0 )

    #-- Public Methods ---------------------------------------------------------

    def show ( self, parent = None, title = '' ):
        """ Display the wait message for a limited duration.
        """
        view = View(
            HGroup(
                spring,
                Item( 'message',
                      show_label = False,
                      style      = 'readonly'
                ),
                spring
            ),
            title = title
        )

        do_after( int( 1000.0 * self.time ),
                  self.edit_facets( parent = parent, view = view ).dispose )

#-------------------------------------------------------------------------------
#  Function Definitions:
#-------------------------------------------------------------------------------

def auto_close_message ( message = 'Please wait', time   = 2.0,
                         title   = 'Please wait', parent = None ):
    """ Displays a message to the user as a modal window with no buttons. The
        window closes automatically after a specified time interval (specified
        in seconds).
    """
    msg = AutoCloseMessage( message = message, time = time )
    msg.show( parent = parent, title = title )

#-- EOF ------------------------------------------------------------------------