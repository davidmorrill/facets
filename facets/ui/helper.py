"""
Defines various helper functions that are useful for creating Facets-based
user interfaces.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from string \
    import uppercase, lowercase

from facets.core_api \
    import CFacet, BaseFacetHandler, FacetError

from ui_facets \
    import SequenceTypes

from facets.ui.adapters.control \
    import Control

from constants \
    import screen_dx, screen_dy, screen_info

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Types of popup views:
Popups = set( ( 'popup', 'popout', 'popover', 'info' ) )

# The types of popups that appear adjacent to the parent control:
AdjacentPopups = ( 'popup', 'popout' )

# The default font used by controls:
_default_font = None

#----------------------------------------------------------------------------
#  Helper Functions:
#----------------------------------------------------------------------------

def default_font ( ):
    """ Returns the default font used by controls.
    """
    global _default_font

    if _default_font is None:
        from facets.ui.editor_factory import EditorFactory

        _default_font = EditorFactory().font

    return _default_font


def user_name_for ( name ):
    """ Returns a "user-friendly" name for a specified facet.
    """
    name       = name.replace( '_', ' ' )
    name       = name[ : 1 ].upper() + name[ 1: ]
    result     = ''
    last_lower = 0
    for c in name:
        if (c in uppercase) and last_lower:
            result += ' '

        last_lower = ( c in lowercase )
        result    += c

    return result


def commatize ( value ):
    """ Formats a specified value as an integer string with embedded commas.
        For example: commatize( 12345 ) returns "12,345".
    """
    s = str( abs( value ) )
    s = s.rjust( ((len( s ) + 2) / 3) * 3 )
    result = ','.join( [ s[ i: i + 3 ]
                         for i in range( 0, len( s ), 3 ) ] ).lstrip()
    if value >= 0:
        return result

    return '-' + result


def enum_values_changed ( values ):
    """ Recomputes the mappings for a new set of enumeration values.
    """

    if isinstance( values, dict ):
        data = [ ( str( v ), n ) for n, v in values.iteritems() ]
        if len( data ) > 0:
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
            col = data[0][0].find( ':' ) + 1
            if col > 0:
                data = [ ( n[ col: ], v ) for n, v in data ]

    elif not isinstance( values, SequenceTypes ):
        handler = values
        if isinstance( handler, CFacet ):
            handler = handler.handler

        if not isinstance( handler, BaseFacetHandler ):
            raise FacetError( "Invalid value for 'values' specified" )

        if handler.is_mapped:
            data = [ ( str( n ), n ) for n in handler.map.keys() ]
            data.sort( lambda x, y: cmp( x[0], y[0] ) )
        else:
            values = handler.values
            if isinstance( values, dict ):
                data = [ ( str( v ), n ) for n, v in values.iteritems() ]
                if len( data ) > 0:
                    data.sort( lambda x, y: cmp( x[0], y[0] ) )
            else:
                data = [ ( str( v ), v ) for v in values ]

    else:
        data = [ ( str( v ), v ) for v in values ]

    names           = [ x[0] for x in data ]
    mapping         = {}
    inverse_mapping = {}
    for name, value in data:
        mapping[ name ] = value
        inverse_mapping[ value ] = name

    return ( names, mapping, inverse_mapping )


def save_window ( ui, path = '' ):
    """ Saves the user preference items for a specified UI.
    """
    control = ui.control
    ui.save_prefs(
        control.frame_bounds + control.bounds + ( control.maximized, ), path
    )


def restore_window ( ui, is_popup = False ):
    """ Restores the user preference items for a specified UI.
    """
    prefs = ui.restore_prefs()
    if prefs is not None:
        if len( prefs ) == 4:
            # fixme: This is to temporarily handle preferences saved before the
            # window maximized state was included (on 11/29/2012):
            x, y, dx, dy     = prefs
            fx, fy, fdx, fdy = x - 8, y - 30, dx + 16, dy + 38
            maximized        = False
        elif len( prefs ) == 5:
            x, y, dx, dy, maximized = prefs
            fx, fy, fdx, fdy        = x - 8, y - 30, dx + 16, dy + 38
        else:
            fx, fy, fdx, fdy, x, y, dx, dy, maximized = prefs

        if is_popup:
            if ui.view.resizable:
                position_window( ui.control, dx, dy, ui.view.popup_bounds )
        else:
            # Verify that most of the view will appear on the user's display.
            # If may not if the user has reconfigured the displays since the
            # view was last used:
            nx, ny, ndx, ndy = check_screen_bounds(
                x, y, dx, dy, x - fx, y - fy, fdx - dx, fdy - dy
            )

            if maximized:
                # If the window was previously maximized, adjust its bounds to
                # create a 'restore' value that is smaller than the entire
                # display:
                nx  += (dx / 10)
                ny  += (dy / 10)
                ndx -= dx / 5
                ndy -= dy / 5

            # Set the window's adjusted bounds and maximized state:
            ui.control.bounds = ( nx, ny, ndx, ndy )
            if maximized:
                ui.control.maximized = True


def check_screen_bounds ( x, y, dx, dy, ax = 0, ay = 0, adx = 0, ady = 0 ):
    """ Verify that the proposed window bounds of (*x*,*y*,*dx*,*dy*) will
        mostly fit on the user's display, and adjust them accordingly if they
        do not fit. The optional (ax, ay, adx, ady) tuple specifies adjustments
        to the proposed bounds that account for the window's frame size. Returns
        a new tuple: (xp, yp, dxp, dyp).
    """
    chunks = [ ( x, y, dx, dy ) ]
    for sx, sy, sdx, sdy in screen_info:
        new_chunks = []
        for cx, cy, cdx, cdy in chunks:
            if (cx >= (sx + sdx)) or (cy >= (sy + sdy)):
                new_chunks.append( ( cx, cy, cdx, cdy ) )

                continue

            if cx < sx:
                tdx = min( sx - cx, cdx )
                new_chunks.append( ( cx, cy, tdx, cdy ) )
                cdx -= tdx
                cx   = sx

            tdx = cx + cdx - (sx + sdx)
            if tdx > 0:
                new_chunks.append( ( sx + sdx, cy, tdx, cdy ) )
                cdx -= tdx

            if cdx > 0:
                if cy < sy:
                    tdy = min( sy - cy, cdy )
                    new_chunks.append( ( cx, cy, cdx, tdy ) )
                    cdy -= tdy
                    cy   = sy

                tdy = cy + cdy - (sy + sdy)
                if tdy > 0:
                    new_chunks.append( ( cx, sy + sdy, cdx, tdy ) )
                    cdy -= tdy

        chunks = new_chunks
        if len( chunks ) == 0:
            break

    # Calculate the total number of pixels that will not appear on the
    # display:
    hidden = 0
    for _, _, cdx, cdy in chunks:
        hidden += (cdx * cdy)

    if hidden > ((dx * dy) / 2):
        # If more than half of the view will be off the user's display,
        # reposition (and possibly resize) the view to fit on the user's
        # primary display:
        sx, sy, sdx, sdy = screen_info[0]

        # Adjust the screen boundary to take the window's title bar
        # and window borders into account:
        sx, sy, sdx, sdy = sx + ax, sy + ay, sdx - adx, sdy - ady

        dx, dy = min( dx, sdx ), min( dy, sdy )
        x      = min( max( x, sx ), sx + sdx - dx )
        y      = min( max( y, sy ), sy + sdy - dy )

    return ( x, y, dx, dy )


def position ( ui ):
    """ Positions the associated UI window on the display.
    """
    view   = ui.view
    window = ui.control

    # Set up the default position of the window:
    parent = window.parent
    if parent is None:
        px,  py  = 0, 0
        pdx, pdy = screen_dx, screen_dy
    else:
        px, py, pdx, pdy = parent.bounds

    # Calculate the correct width and height for the window:
    cur_width, cur_height = window.best_size
    width, height         = view.width, view.height

    if width < 0.0:
        width = cur_width
    elif width <= 1.0:
        width = int( width * screen_dx )
    else:
        width = int( width )

    if height < 0.0:
        height = cur_height
    elif height <= 1.0:
        height = int( height * screen_dy )
    else:
        height = int( height )

    if ui.kind in Popups:
        bounds = view.popup_bounds
        if bounds[-1] <= 0:
            bounds = None
            # fixme: This code is deprecated, only 'popup_bounds' should be
            # used now...
            if view.x >= -99999.0:
                print ('Use of view.(x,y,width,height) to position popup views '
                       'is deprecated. Use view.popup_bounds instead.')
                from facets.core.debug import called_from; called_from( 25 )
                bounds        = ( view.x, view.y, view.width, view.height )
                width, height = cur_width, cur_height

        position_window( window, width, height, bounds )

        return

    # Calculate the correct position for the window:
    x = view.x
    y = view.y

    if x < -99999.0:
        x = px + ((pdx - width) / 2)
    elif x <= -1.0:
        x = px + pdx - width + int( x ) + 1
    elif x < 0.0:
        x = px + pdx - width + int( x * pdx )
    elif x <= 1.0:
        x = px + int( x * pdx )
    else:
        x = int( x )

    if y < -99999.0:
        y = py + ((pdy - height) / 2)
    elif y <= -1.0:
        y = py + pdy - height + int( y ) + 1
    elif x < 0.0:
        y = py + pdy - height + int( y * pdy )
    elif y <= 1.0:
        y = py + int( y * pdy )
    else:
        y = int( y )

    # Position and size the window as requested:
    window.bounds = ( max( 0, x ), max( 0, y ), width, height )


def position_window ( window, width = None, height = None, parent = None ):
    """ Positions a window on the screen with a specified width and height so
        that the window completely fits on the screen if possible.
    """
    dx, dy = window.size
    width  = width  or dx
    height = height or dy

    if parent is None:
        # See if the logical window parent was set (e.g. in ui_live.py):
        parent = window._parent

    if parent is None:
        # Center the popup on the screen:
        window.bounds = ( (screen_dx - width)  / 2, (screen_dy - height) / 2,
                          width, height )

        return

    # Calculate the desired size of the popup control:
    if isinstance( parent, Control ):
        x, y     = parent.screen_position
        cdx, cdy = parent.size
    else:
        # Special case of parent being a screen position and size tuple (used
        # to pop-up a dialog for a table cell):
        x, y, cdx, cdy = parent

    adjacent = (window.kind in AdjacentPopups)
    width    = min( max( cdx, width ), screen_dx )
    height   = min( height, screen_dy )

    # Calculate the best position and size for the pop-up:

    # Note: This code tries to deal with the fact that the user may have
    # multiple monitors. wx does not report this information, so the screen_dx,
    # screen_dy values usually just provide the size of the primary monitor. To
    # get around this, the code assumes that the original (x,y) values are
    # valid, and that all monitors are the same size. If this assumption is not
    # true, popups may appear in wierd positions on the secondary monitors.
    nx     = x % screen_dx
    xdelta = x - nx
    rx     = nx + cdx
    if (nx + width) > screen_dx:
        if (rx - width) < 0:
            nx = screen_dx - width
        else:
            nx = rx - width

    ny     = y % screen_dy
    ydelta = y - ny
    by     = ny
    if ny > (screen_dy / 2):
        by -= height
        if not adjacent:
            by += cdy

        if by < 0:
            by = ny
            if adjacent:
                by += cdy

            if (by + height) > screen_dy:
                by = 0
    else:
        if adjacent:
            by += cdy

        if (by + height) > screen_dy:
            if not adjacent:
                ny += cdy

            if (ny - height) >= 0:
                by = ny - height
            else:
                by = screen_dy - height

    # Position and size the window as requested:
    window.bounds = ( nx + xdelta, by + ydelta, width, height )

#-- EOF ------------------------------------------------------------------------