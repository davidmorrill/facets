"""
Defines the 'theme_color_tables' dictionary used to define the various default
theme color tables supported by the VIP Shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  The VIP Shell Color Table Definitions:
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  The usage for each index is:
#-------------------------------------------------------------------------------
#  0:  Output item (stdout)
#  1 = Error item (stderr)
#  2 = Result item
#  3 = Shell command item
#  4 = Exception item
#  5 = Directory item
#  6 = File item
#  7 = Python file item
#  8 = Line numbers
#  9 = Item Id
#  A = Omitted data
#  B = Emphasized
#  C = Example
#  D = Error
#  E = Python normal
#  F = Python literal
#  G = Python number
#  H = Python keyword
#  I = Python comment
#  J = Python special
#-------------------------------------------------------------------------------

DefaultColors = ('\x020B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B4D87E0'
                     'FF0E0C919191C00000001DF51306F20B0B0BA400817A8309FC3800'
                     '0000E9E28300.')

PadColors     = ('\x020303030303030303030303030303030303030303030303032462C9'
                     '855400919191E900002323FFDA0000030303A400817A8309FC3800'
                     '0000E9E28300.')

DarkColors    = ('\x02DFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDFDF008486'
                     'E8D0008E8E8EFF9C4679A9FFFE5B00DFDFDF00F400F2970EFFFF15'
                     '1EFFFFD830FF.')

GreyColors    = ('\x020B0B0B0B0B0B0B0B0B043C9E0B0B0B0B0B0B0B0B0B0B0B0B2244C6'
                     '7958005F5F5FC000000000D0EE002D0B0B0BA70083AE8D0CFC3800'
                     '0000DF579800.')

BlackColors   = ('\x02000000000000000000000000000000000000000000000000000000'
                     '000000000000000000000000000000000000000000000000000000'
                     '000000000000.')

WhiteColors   = ('\x02FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
                     'FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
                     'FFFFFFFFFFFF.')

Grey3DColors  = ('\x02FDFDFDFDFDFDF4F4F4FDFCB0FFD9D9FDFDFDFAFAFAFFFFFFFDFD91'
                     'FFBA8CB3B3B3FF9C46A6C8FFFF7B00F5F5F57CFF7CF6AF46FFFF14'
                     '5AFFFFEC98FF.' )

ThorColors    = ('\x02FFFFFFFDDDDDF5F5F5BBD2FDE0BFBF0B0B0BF5F5F5FFFFFBD4BB9A'
                     'FFB5A0ACACACC6FF9F96F1FF99E3E0F5F5F5FFF727FA9FDEFCB600'
                     '8CFFFFA1FF24.')

SmoothColors  = ('\x020B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B0B7C6339'
                     '1E7679777777B41313001AE31306F20B0B0B8F2477496B07D82E00'
                     '1F4CC0FAF302.')

#-------------------------------------------------------------------------------
#  Update this section when adding, renaming or deleting shell themes:
#-------------------------------------------------------------------------------

# The mapping from editor 'theme' values to 'color_table' values:
theme_color_tables = {
    'default':      DefaultColors,
    'pad':          PadColors,
    'legal':        PadColors,
    'grey':         GreyColors,
    'grey3d':       Grey3DColors,
    'white':        DefaultColors,
    'black':        DarkColors,
    'light':        DefaultColors,
    'dark':         DarkColors,
    'simple_white': BlackColors,
    'simple_black': WhiteColors,
    'stark_white':  BlackColors,
    'stark_black':  WhiteColors,
    'shadow':       DefaultColors,
    'rounded':      GreyColors,
    'thor':         ThorColors,
    'smooth':       SmoothColors,
    'bee':          SmoothColors,
}

#-- EOF ------------------------------------------------------------------------
