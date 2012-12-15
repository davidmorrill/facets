"""
Defines the concrete Qt4 specific implementation of the UIEvent class for
providing GUI toolkit neutral support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
    import Qt, QString

from facets.core_api \
    import Instance, Any, cached_property

from facets.ui.adapters.control \
    import Control

from facets.ui.adapters.ui_event \
    import UIEvent

from facets.ui.qt4.key_event_to_name \
    import key_event_to_name

#-------------------------------------------------------------------------------
#  'QtUIEvent' class:
#-------------------------------------------------------------------------------

class QtUIEvent ( UIEvent ):

    #-- Facet Definitions ------------------------------------------------------

    # The control associated with the event:
    control_adapter = Instance( Control )

    # The data set by Qt for a SIGNAL/SLOT connection:
    data = Any

    #-- Property Implementations -----------------------------------------------

    def _get_value ( self ):
        result = self.data
        if not isinstance( result, QString ):
            return result

        return str( result )


    def _get_x ( self ):
        return self.event.x()

    def _get_y ( self ):
        return self.event.y()


    def _get_screen_x ( self ):
        return self.event.globalX()

    def _get_screen_y ( self ):
        return self.event.globalY()


    def _get_left_down ( self ):
        return ((int( self.event.buttons() ) & Qt.LeftButton) != 0)


    def _get_right_down ( self ):
        return ((int( self.event.buttons() ) & Qt.RightButton) != 0)


    def _get_shift_down ( self ):
        return ((int( self.event.modifiers() ) & Qt.ShiftModifier) != 0)


    def _get_control_down ( self ):
        return ((int( self.event.modifiers() ) & Qt.ControlModifier) != 0)


    def _get_alt_down ( self ):
        return ((int( self.event.modifiers() ) & Qt.AltModifier) != 0)


    @cached_property
    def _get_key_code ( self ):
        return key_event_to_name( self.event )


    def _get_wheel_change ( self ):
        try:
            return (self.event.delta() / 120)
        except:
            # Just in case this is used for normal mouse events, which won't
            # have the 'delta' method:
            return 0


    def _get_activated ( self ):
        # fixme: This does not appear to be used by Qt...
        print 'event.activated!'
        return False


    def _get_control ( self ):
        return self.control_adapter


    def _get_handled ( self ):
        return self.event.isAccepted()

    def _set_handled ( self, handled ):
        self.event.setAccepted( handled )

#-- EOF ------------------------------------------------------------------------