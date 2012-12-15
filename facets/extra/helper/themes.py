"""
Defines some useful definitions for creating themed user interfaces.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Constant, Delegate, Instance, Item, Theme, ATheme, ButtonEditor, \
           TextEditor, ScrubberEditor, RangeSliderEditor

#-------------------------------------------------------------------------------
#  Themes:
#-------------------------------------------------------------------------------

# An item that displays the tool title or information:
class TTitle ( Item ):
    show_label = Constant( False )
    style      = Constant( 'readonly' )
    editor     = Constant( TextEditor() )
    item_theme = ATheme( Theme( '@xform:i4b.png?L46', content = ( -2, -6 ) ) )


# A standard themed button:
class TButton ( Item ):
    show_label = Constant( False )
    editor     = Instance( ButtonEditor, () )
    image      = Delegate( 'editor', modify = True )


# A standard scrubber editor item:
def Scrubber ( name, tooltip = '', increment = 1, low = 0.0, high = 0.0,
                     width   = 40, label     = None ):
    """ Returns an Item for a value using a ScrubberEditor.
    """
    result = Item( name,
        width      = -width,
        editor     = ScrubberEditor(
                         low       = low,
                         high      = high,
                         increment = increment
                     ),
        tooltip    = tooltip,
        item_theme = '#themes:ScrubberEditor'
    )
    if label is not None:
        result.label = label

    return result


# A standard range slider item:
def Slider ( name, tooltip = '', low = -1.0, high = 1.0, width = 140,
                   label   = None ):
    """ Returns an Item for a value using a RangeSliderEditor.
    """
    result = Item( name,
        width   = -width,
        editor  = RangeSliderEditor( low = low, high = high,
                                     increment = 0.01, body_style = 25 ),
        tooltip = tooltip
    )
    if label is not None:
        result.label = label

    return result


# A label theme:
LabelTheme = Theme( '@xform:b6?H61L20S9', alignment = 'center' )


# An inset label theme:
InsetTheme = Theme( '@std:inset_grey',
    content   = -6,
    label     = ( 6, 6, 9, 0 ),
    alignment = 'center'
)

#-- EOF ------------------------------------------------------------------------