"""
Defines the 'themes' dictionary used to define the various themes supported by
the VIP Shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Enum

#-------------------------------------------------------------------------------
#  The VIP Shell Theme Definitions:
#-------------------------------------------------------------------------------

themes = dict(

# The 'default' theme:
default_shell_selected         = '@facets:shell_item?H9l44S|l',
default_labeled_selected       = '@facets:shell_item_x',
default_labeled_for_0_selected = '@facets:shell_item?H9l44S|l',
default_command                = '@facets:shell_item?H58l15S53|l',
default_persistedcommand       = '@facets:shell_item?H14l10S|l',
default_result                 = '@facets:shell_item?H58l5S53|l',
default_log                    = '@facets:shell_item?H58l12S53|l',
default_locals                 = '@facets:shell_item?H58l12S53|l',
default_output                 = '@facets:shell_item',
default_error                  = '@facets:shell_item?l4S0|l',
default_labeled                = '@facets:shell_item_x?H3L10s60|s3',
default_labeled_for_0          = '@facets:shell_item?H13l29S34|l',
default_calledfrom             = '@facets:shell_item_x?H49L16s44~H58l1S|h6',
default_calledfrom_for_0       = '@facets:shell_item?H58l20S53|l',
default_path                   = '@facets:shell_item_x?H99L15s62|s3',
default_path_for_0             = '@facets:shell_item?H10l3S40|l',
default_directory              = '@facets:shell_item_x?H6l15S|s3',
default_directory_for_0        = '@facets:shell_item?H16l12S|l',
default_exception              = '@facets:shell_item_x?H89L26s6|s3',
default_exception_for_0        = '@facets:shell_item?l10S0|l',

# The 'pad' theme:
pad_shell_selected             = '@facets:shell_item_yp?H93l33S|h13H53',
pad_labeled_selected           = '@facets:shell_item_ypx?H93l35|h16H51l86L92',
pad_labeled_for_0_selected     = '@facets:shell_item_yp?H93l33S|h13H53',
pad_command                    = '@facets:shell_item_yp?H82|h35H36',
pad_persistedcommand           = '@facets:shell_item_yp?Ls|h35H36',
pad_result                     = '@facets:shell_item_yp?H26|h35H36',
pad_log                        = '@facets:shell_item_yp?H26l12|h35H36',
pad_locals                     = '@facets:shell_item_yp?H26l12|h35H36',
pad_output                     = '@facets:shell_item_yp',
pad_error                      = '@facets:shell_item_yp?H59|h35H36',
pad_labeled                    = '@facets:shell_item_ypx?H75l11s56|h35H36',
pad_labeled_for_0              = '@facets:shell_item_yp?H75l11s56|h35H36',
pad_calledfrom                 = '@facets:shell_item_ypx?H26l12|h35H36',
pad_calledfrom_for_0           = '@facets:shell_item_yp?H26l12|h35H36',
pad_path                       = '@facets:shell_item_ypx?H80l44S|h35H36',
pad_path_for_0                 = '@facets:shell_item_yp?H80l44S|h35H36',
pad_pythonfile                 = '@facets:shell_item_ypx?H21l33S24|h35H36',
pad_pythonfile_for_0           = '@facets:shell_item_yp?H21l33S24|h35H36',
pad_directory                  = '@facets:shell_item_ypx?l49S24|h35H36',
pad_directory_for_0            = '@facets:shell_item_yp?l49S24|h35H36',
pad_exception                  = '@facets:shell_item_ypx?H65l45S|h35H36',
pad_exception_for_0            = '@facets:shell_item_yp?H65l45S|h35H36',

# The 'legal' theme:
legal_shell_selected           = '@facets:shell_item_lpc?H93l33S|h13H53',
legal_labeled_selected         = '@facets:shell_item_lpx?H93l35|h16H51l86L92',
legal_labeled_for_0_selected   = '@facets:shell_item_lpo?H93l33S|h13H53',
legal_command                  = '@facets:shell_item_lpc',
legal_result                   = '@facets:shell_item_lpo?H26L7|h35H36',
legal_log                      = '@facets:shell_item_lpo?H26|h35H36',
legal_locals                   = '@facets:shell_item_lpo?H26|h35H36',
legal_output                   = '@facets:shell_item_lpo?L6|h35H36',
legal_error                    = '@facets:shell_item_lpo?H59L6|h35H36',
legal_labeled                  = '@facets:shell_item_lpx?H75l11s56|h35H36',
legal_labeled_for_0            = '@facets:shell_item_lpo?H75l11s56|h35H36',
legal_calledfrom               = '@facets:shell_item_lpx?H26|h35H36',
legal_calledfrom_for_0         = '@facets:shell_item_lpo?H26|h35H36',
legal_path                     = '@facets:shell_item_lpx?H80l20s14|h35H36',
legal_path_for_0               = '@facets:shell_item_lpo?H80l20s14|h35H36',
legal_pythonfile               = '@facets:shell_item_lpx?H19l9s53|h35H36',
legal_pythonfile_for_0         = '@facets:shell_item_lpo?H19l9s53|h35H36',
legal_directory                = '@facets:shell_item_lpx?l11s48|h35H36',
legal_directory_for_0          = '@facets:shell_item_lpo?l11s48|h35H36',
legal_exception                = '@facets:shell_item_lpx?H65l45S|h35H36',
legal_exception_for_0          = '@facets:shell_item_lpo?H65l45S|h35H36',

# The 'grey' theme:
grey_shell_selected            = '@facets:shell_item_lpo?H93l33S|h13H53',
grey_command_selected          = '@facets:shell_item_lpc?H93l33S|h13H53',
grey_labeled_selected          = '@facets:shell_item_lpx?H93l35|h16H51l86L92',
grey_labeled_for_0_selected    = '@facets:shell_item_lpo?H93l33S|h13H53',
grey_command                   = '@facets:shell_item_lpc?s',
grey_generated                 = '@facets:shell_item_lpo?s',
grey_labeled                   = '@facets:shell_item_lpx?s',
grey_labeled_for_0             = '@facets:shell_item_lpo?s',

# The 'light' theme:
light_shell_selected           = '@facets:shell_item?H9l44S|l',
light_labeled_selected         = '@facets:shell_item_x?l14S|s3',
light_labeled_for_0_selected   = '@facets:shell_item?H9l44S|l',
light_command                  = '@facets:shell_item?H61l12S70|l',
light_generated                = '@facets:shell_item?l8s|l',
light_labeled                  = '@facets:shell_item_x?L11s|s3',
light_labeled_for_0            = '@facets:shell_item?l8s|l',

# The 'dark' theme:
dark_shell_selected            = '@facets:shell_item?H9l65S|l',
dark_labeled_selected          = '@facets:shell_item_x?l29|l57',
dark_labeled_for_0_selected    = '@facets:shell_item?H9l65S|l',
dark_command                   = '@facets:shell_item?H10l90S26|l',
dark_generated                 = '@facets:shell_item?H59l95s55|l',
dark_labeled                   = '@facets:shell_item_xd?H22l50s62|h8',
dark_labeled_for_0             = '@facets:shell_item?H35l86S39|l',

# The 'white' theme:
white_shell_selected           = '@facets:shell_item_lpo?H93l33S|h13H53',
white_command_selected         = '@facets:shell_item_lpc?H93l33S|h13H53',
white_labeled_selected         = '@facets:shell_item_lpx?H93l35|h16H51l86L92',
white_labeled_for_0_selected   = '@facets:shell_item_lpo?H93l33S|h13H53',
white_command                  = '@facets:shell_item_lpc?Ls|h16H17',
white_generated                = '@facets:shell_item_lpo?Ls|h6H55',
white_labeled                  = '@facets:shell_item_lpx?Ls|h6H55',
white_labeled_for_0            = '@facets:shell_item_lpo?Ls|h6H55',

# The 'black' theme:
black_shell_selected           = '@facets:shell_item_lpo?H53l53S|h13H53',
black_command_selected         = '@facets:shell_item_lpc?H53l53S|h13H53',
black_labeled_selected         = '@facets:shell_item_lpx?H53l53S|h16H51l86L92',
black_labeled_for_0_selected   = '@facets:shell_item_lpo?H53l53S|h13H53',
black_command                  = '@facets:shell_item_lpc?ls|h16H17',
black_generated                = '@facets:shell_item_lpo?ls|h6H55',
black_labeled                  = '@facets:shell_item_lpx?ls|h6H55',
black_labeled_for_0            = '@facets:shell_item_lpo?ls|h6H55',

# The 'simple_white' theme:
simple_white_shell_selected    = '@facets:shell_item?H9l44S|l',
simple_white_command           = '@facets:shell_item?l14',
simple_white_generated         = '@facets:shell_item',

# The 'simple_black' theme:
simple_black_shell_selected    = '@facets:shell_item?H9l44S|l',
simple_black_command           = '@facets:shell_item?l90|l',
simple_black_generated         = '@facets:shell_item?l|l',

# The 'stark_white' theme:
stark_white_shell_selected     = '@facets:shell_item?H9l44S|l',
stark_white_shell              = '@facets:shell_item?L',

# The 'stark_black' theme:
stark_black_shell_selected     = '@facets:shell_item?H9l44S|l',
stark_black_shell              = '@facets:shell_item?l',

# The 'grey3d' theme:
grey3d_shell_selected          = '@facets:shell_item_bo?H45l6S|l26L33',
grey3d_command_selected        = '@facets:shell_item_bc?H45l3S|h55H65l27L45',
grey3d_labeled_selected        = '@facets:shell_item_box?H45l6S|l26L33',
grey3d_labeled_for_0_selected  = '@facets:shell_item_bo?H45l6S|l26L33',
grey3d_command                 = '@facets:shell_item_bc',
grey3d_generated               = '@facets:shell_item_bo',
grey3d_labeled                 = '@facets:shell_item_box',
grey3d_labeled_for_0           = '@facets:shell_item_bo',

# The 'shadow' theme:
shadow_shell_selected          = '@facets:shell_item?H9l44S|l',
shadow_shell                   = '@facets:shell_item_s',
shadow_command                 = '@facets:shell_item_s?L18s|h17',
shadow_error                   = '@facets:shell_item_s?H65l11|h17',
shadow_result                  = '@facets:shell_item_s?H28|h17',
shadow_path                    = '@facets:shell_item_s?H71L2s12|h17',

# The 'rounded' theme:
rounded_shell_selected         = '@facets:shell_item?H9l44S|l',
rounded_shell                  = '@facets:shell_item_r?L18|h31H33',
rounded_command                = '@facets:shell_item_r?L24s43|h31H33',
rounded_output                 = '@facets:shell_item_r?H79L15|h31H33',
rounded_error                  = '@facets:shell_item_r?H67L12S25|h31H33',
rounded_result                 = '@facets:shell_item_r?H27L15|h31H33',
rounded_log                    = '@facets:shell_item_r?H27L6|h31H33',
rounded_labeled                = '@facets:shell_item_rx?L18|h31H33',
rounded_labeled_for_0          = '@facets:shell_item_r?L18|h31H33',
rounded_calledfrom             = '@facets:shell_item_rx?H26L6|h31H33',
rounded_calledfrom_for_0       = '@facets:shell_item_r?H27L6|h31H33',
rounded_directory              = '@facets:shell_item_rx?H81L21S66|h31H33',
rounded_directory_for_0        = '@facets:shell_item_r?H81L21S66|h31H33',
rounded_pythonfile             = '@facets:shell_item_rx?L4|h31H33',
rounded_pythonfile_for_0       = '@facets:shell_item_r?L4|h31H33',
rounded_imagefile              = '@facets:shell_item_rx?H43L16|h31H33',
rounded_imagefile_for_0        = '@facets:shell_item_r?H43L16|h31H33',
rounded_exception              = '@facets:shell_item_rx?H66l4S14|h31H33',
rounded_exception_for_0        = '@facets:shell_item_r?H66l4S14|h31H33',

# The 'thor' theme:
thor_shell_selected            = '@facets:shell_item_thor?H6L14S59|l27L32',
thor_shell                     = '@facets:shell_item_thor',

# The 'smooth' theme:
smooth_shell_selected          = '@facets:shell_item_zon?H6L14S59|l27L32',
smooth_shell                   = '@facets:shell_item_zon',
smooth_command                 = '@facets:shell_item_zcn',
smooth_output                  = '@facets:shell_item_zon?H20S14|h13',
smooth_error                   = '@facets:shell_item_zon?H67L9|h13',
smooth_result                  = '@facets:shell_item_zon?S6|h13',
smooth_log                     = '@facets:shell_item_zon?H49L16S32|h13',
smooth_locals                  = '@facets:shell_item_zon?H49L16S32|h13',
smooth_labeled                 = '@facets:shell_item_zox',
smooth_labeled_for_0           = '@facets:shell_item_zon',
smooth_calledfrom              = '@facets:shell_item_zox?H49L16S32|h13',
smooth_calledfrom_for_0        = '@facets:shell_item_zon?H49L16S32|h13',
smooth_pythonfile              = '@facets:shell_item_zox?H74S24|h13',
smooth_pythonfile_for_0        = '@facets:shell_item_zon?H74S24|h13',
smooth_imagefile               = '@facets:shell_item_zox?H48L6S8|h13',
smooth_imagefile_for_0         = '@facets:shell_item_zon?H48L6S8|h13',
smooth_file                    = '@facets:shell_item_zox?H81L4S12|h13',
smooth_file_for_0              = '@facets:shell_item_zon?H81L4S12|h13',
smooth_view                    = '@facets:shell_item_zox?H25l2S34|h13',
smooth_view_for_0              = '@facets:shell_item_zon?H25l2S34|h13',
smooth_exception               = '@facets:shell_item_zox?H67S43|h13',
smooth_exception_for_0         = '@facets:shell_item_zon?H67S43|h13',

# The 'Bee' theme:
bee_shell_selected             = '@xform:b?H10S90',
bee_shell                      = '@xform:b?L45',
bee_output                     = '@xform:b?H10L37S13',
bee_result                     = '@xform:b?H62L39S20',
bee_log                        = '@xform:b?H62L33S20',
bee_locals                     = '@xform:b?H62L33S20',
bee_exception_for_0            = '@xform:b?HL32S',
)

# The facet defining the possible 'theme' values:
ShellTheme = Enum( 'default', dict(
    default      = 'Default',
    pad          = 'Pad: Yellow',
    legal        = 'Pad: Legal',
    grey         = 'Pad: Grey',
    grey3d       = 'Grey 3D',
    white        = 'Pad: White',
    black        = 'Pad: Black',
    light        = 'Light',
    dark         = 'Dark',
    simple_white = 'Simple white',
    simple_black = 'Simple black',
    stark_white  = 'All white',
    stark_black  = 'All black',
    shadow       = 'Shadow',
    rounded      = 'Rounded',
    thor         = 'Core: Thor',
    smooth       = 'Smooth',
    bee          = 'Bee',
) )

# The mapping from the current theme to the next theme:
CycleTheme = dict(
    default      = 'pad',
    pad          = 'legal',
    legal        = 'grey',
    grey         = 'grey3d',
    grey3d       = 'white',
    white        = 'black',
    black        = 'light',
    light        = 'dark',
    dark         = 'simple_white',
    simple_white = 'simple_black',
    simple_black = 'stark_white',
    stark_white  =  'stark_black',
    stark_black  =  'shadow',
    shadow       =  'rounded',
    rounded      =  'thor',
    thor         =  'smooth',
    smooth       =  'bee',
    bee          =  'default',
)

#-- EOF ------------------------------------------------------------------------
