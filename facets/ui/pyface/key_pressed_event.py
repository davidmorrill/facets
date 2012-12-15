"""
The event that is generated when a key is pressed.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import Bool, HasFacets, Int, Any

#-------------------------------------------------------------------------------
#  'KeyPressedEvent' class:
#-------------------------------------------------------------------------------

class KeyPressedEvent ( HasFacets ):
    """ The event that is generated when a key is pressed.
    """

    #-- 'KeyPressedEvent' Interface --------------------------------------------

    # Is the alt key down?
    alt_down = Bool

    # Is the control key down?
    control_down = Bool

    # Is the shift key down?
    shift_down = Bool

    # The keycode.
    key_code = Int

    # The original toolkit specific event.
    event = Any

#-- EOF ------------------------------------------------------------------------