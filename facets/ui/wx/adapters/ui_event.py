"""
Defines the concrete wxPython specific implementation of the UIEvent class for
providing GUI toolkit neutral support.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import cached_property

from facets.ui.adapters.ui_event \
    import UIEvent

from facets.ui.wx.key_event_to_name \
    import key_event_to_name

#-------------------------------------------------------------------------------
#  'WxUIEvent' class:
#-------------------------------------------------------------------------------

class WxUIEvent ( UIEvent ):

    #-- Property Implementations -----------------------------------------------

    def _get_value ( self ):
        return self.event.GetString()


    def _get_x ( self ):
        return self.event.GetX()

    def _get_y ( self ):
        return self.event.GetY()


    @cached_property
    def _get_screen_x ( self ):
        x, y = self.event.GetEventObject().GetScreenPosition()

        return self.event.GetX() + x

    @cached_property
    def _get_screen_y ( self ):
        x, y = self.event.GetEventObject().GetScreenPosition()

        return self.event.GetY() + y


    def _get_left_down ( self ):
        return self.event.LeftIsDown()


    def _get_right_down ( self ):
        return self.event.RightIsDown()


    def _get_shift_down ( self ):
        return self.event.ShiftDown()


    def _get_control_down ( self ):
        return self.event.ControlDown()


    def _get_alt_down ( self ):
        return self.event.AltDown()


    @cached_property
    def _get_key_code ( self ):
        return key_event_to_name( self.event )


    def _get_wheel_change ( self ):
        event = self.event

        return (event.GetWheelRotation() / event.GetWheelDelta())


    def _get_activated ( self ):
        return self.event.GetActive()


    def _get_control ( self ):
        from control import control_adapter

        return control_adapter( self.event.GetEventObject() )


    def _set_handled ( self, handled ):
        if not handled:
            self.event.Skip()

#-- EOF ------------------------------------------------------------------------