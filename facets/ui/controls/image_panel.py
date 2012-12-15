"""
Defines a themed panel that wraps itself around a single child control.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasPrivateFacets, Str, Property, Instance, Bool, Any, implements, \
           cached_property, property_depends_on, toolkit

from facets.ui.adapters.layout \
    import Layout

from facets.ui.i_abstract_layout \
    import IAbstractLayout

from themed_window \
    import ThemedWindow

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Size of an empty text string:
ZeroTextSize = ( 0, 0 )

#-------------------------------------------------------------------------------
#  'ImagePanel' class:
#-------------------------------------------------------------------------------

class ImagePanel ( ThemedWindow ):
    """ Defines a themed panel that wraps itself around a single child control.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The optional text to display in the top or bottom of the image slice:
    text = Str( event = 'updated' )

    # Can the application change the theme contents?
    mutable_theme = Bool( False )

    # Is the image panel capable of displaying text?
    can_show_text = Property

    # The adjusted size of the panel, taking into account the size of its
    # current children and the image border:
    adjusted_size = Property

    # The best size of the panel, taking into account the best size of its
    # children and the image border:
    best_size = Property

    #-- Private Facets ---------------------------------------------------------

    # The size of the current text:
    text_size = Property( depends_on = 'text, control' )

    #-- Property Implementations -----------------------------------------------

    def _get_adjusted_size ( self ):
        """ Returns the adjusted size of the panel taking into account the
            size of its current children and the image border.
        """
        control = self.control
        dx, dy  = 0, 0
        for child in control.children:
            # There should only be at most one child, so the loop should only
            # execute 0 or 1 times:
            dx, dy = child.size

        control.size = size = self._adjusted_size_of( dx, dy )

        return size


    def _get_best_size ( self ):
        """ Returns the best size of the panel taking into account the
            best size of its current children and the image border.
        """
        control = self.control
        dx, dy  = 0, 0
        for child in control.children:
            # There should only be at most one child, so the loop should only
            # execute 0 or 1 times:
            dx, dy = child.best_size

        control.min_size = size = self._adjusted_size_of( dx, dy )

        return size


    @cached_property
    def _get_can_show_text ( self ):
        """ Returns whether or not the image panel is capable of displaying
            text.
        """
        tdx, tdy = self.control.text_size( 'Myj' )
        slice    = self.theme.image_slice
        tdy     += 4

        return ((tdy <= slice.xtop) or (tdy <= slice.xbottom) or
                (slice.xleft >= 40) or (slice.xright >= 40))


    @property_depends_on( 'text, control' )
    def _get_text_size ( self ):
        """ Returns the text size information for the window.
        """
        if (self.text == '') or (self.control is None):
            return ZeroTextSize

        return self.control.text_size( self.text )

    #-- Facet Event Handlers ---------------------------------------------------

    def _control_set ( self ):
        """ Handles the underlying 'control' being changed.
        """
        control = self.control
        if control is not None:
            # Set up the sizer for the control:
            self.layout = ImageLayout( image_panel = self )

            # Attach the image slice to the control:
            control.image_slice = self.theme.image_slice

            # Set the panel's background colour to the image slice bg_color:
            control.background_color = control.image_slice.bg_color


    def _updated_set ( self ):
        """ Handles a change that requires the control to be updated.
        """
        if self.control is not None:
            self.control.refresh()


    def _mutable_theme_set ( self, state ):
        """ Handles a change to the 'mutable_theme' facet.
        """
        self.on_facet_set(
            self._theme_modified,
            'theme.[border.-,content.-,label.-,alignment,content_color,'
            'label_color]',
            remove = not state
        )


    def _theme_modified ( self ):
        self.update()


    def _theme_set ( self ):
        """ Handles the 'theme' facet being changed.
        """
        super( ImagePanel, self )._theme_set()

        control = self.control
        theme   = self.theme
        if (control is not None) and (theme is not None):
            # Attach the image slice to the control:
            control.image_slice = theme.image_slice

            # Set the panel's background colour to the image slice bg_color:
            control.background_color = control.image_slice.bg_color

    #-- Control Event Handlers -------------------------------------------------

    def paint ( self, g ):
        """ Paints the foreground into the specified graphics object.
        """
        # If we have text and have room to draw it, then do so:
        text = self.text
        if (text != '') and self.can_show_text:
            theme                   = self.theme
            g.text_background_color = None
            g.text_color            = theme.label_color
            g.font                  = self.control.font
            alignment               = theme.alignment
            label                   = theme.label
            wdx, wdy                = self.control.client_size
            tdx, tdy                = self.text_size
            tx                      = None
            slice                   = theme.image_slice
            xleft                   = slice.xleft
            xright                  = slice.xright
            xtop                    = slice.xtop
            xbottom                 = slice.xbottom
            ltop                    = label.top
            lbottom                 = label.bottom
            tdyp                    = tdy + ltop + lbottom
            cl                      = xleft + label.left
            cr                      = wdx - xright - label.right
            if (tdyp <= xtop) and (xtop >= xbottom):
                ty = (ltop + xtop - lbottom - tdy) / 2
            elif tdy <= xbottom:
                ty = wdy + ((ltop - xbottom - lbottom - tdy) / 2)
            else:
                ty = (wdy + xtop + label.top - xbottom - label.bottom - tdy) / 2
                if xleft >= xright:
                    cl = label.left
                    cr = xleft - label.right
                else:
                    cl = wdx - xright + label.left
                    cr = wdx - label.right

            # Calculate the x coordinate for the specified alignment type:
            if alignment == 'left':
                tx = cl
            elif alignment == 'right':
                tx = cr - tdx
            else:
                tx = (cl + cr - tdx) / 2

            # Draw the (clipped) text string (note that we increase the clipping
            # bounds height a small amount because too tight a bounds can cause
            # clipping of text descenders:
            g.clipping_bounds = ( cl, ty, cr - cl, tdy + 2 )
            g.draw_text( text, tx, ty )
            g.clipping_bounds = None

    #-- Private Methods --------------------------------------------------------

    def _adjusted_size_of ( self, dx, dy ):
        """ Returns the adjusted size of its children, taking into account the
            image slice border.
        """
        slice   = self.theme.image_slice
        content = self.theme.content
        adx     = (min( slice.left,   slice.xleft )   +
                   min( slice.right,  slice.xright )  + content.right)
        ady     = (min( slice.top,    slice.xtop )    +
                   min( slice.bottom, slice.xbottom ) + content.bottom)

        if dx > 0:
            adx += (dx + content.left)

        if dy > 0:
            ady += (dy + content.top)

        return ( adx, ady )

#-------------------------------------------------------------------------------
#  'ImageLayout' class:
#-------------------------------------------------------------------------------

class ImageLayout ( HasPrivateFacets ):
    """ Defines a sizer that correctly sizes a window's children to fit within
        the borders implicitly defined by a background ImageSlice object.
    """

    implements( IAbstractLayout )

    #-- Facet Definitions ------------------------------------------------------

    # The underlying GUI toolkit specific layout manager (part of the
    # IAbstractLayout interface):
    layout = Any

    # The ImagePanel using this layout manager:
    image_panel = Instance( ImagePanel )

    # The theme associated with layout manager:
    theme = Property

    # The image slice associated with the layout manager:
    image_slice = Property

    # The content of the theme associated with the layout manager:
    content = Property

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'image_panel.theme' )
    def _get_theme ( self ):
        return self.image_panel.theme


    @property_depends_on( 'theme' )
    def _get_image_slice ( self ):
        return self.theme.image_slice


    @property_depends_on( 'theme' )
    def _get_content ( self ):
        return self.theme.content

    #-- IAbstractLayout Interface Implementation -------------------------------

    def calculate_minimum ( self ):
        """ Calculates the minimum size of the control by adding its contents
            minimum size to the ImageSlice object's border size.
        """
        dx, dy = 0, 0
        for child in self.image_panel.control.children:
            # There should be at most one child control, so the loop will
            # execute 0 or 1 times:
            dx, dy = child.best_size
            if dx < 0:
                dx, dy = child.min_size

        slice   = self.image_slice
        content = self.content

        return ( max( slice.left + slice.right,
                      slice.xleft + slice.xright +
                      content.left + content.right + dx ),
                 max( slice.top + slice.bottom,
                      slice.xtop + slice.xbottom +
                      content.top + content.bottom + dy ) )


    def perform_layout ( self, x, y, dx, dy ):
        """ Layout the contents of the layout manager based on the specified
            size and position.
        """
        slice   = self.image_slice
        content = self.content
        left    = slice.xleft + content.left
        top     = slice.xtop  + content.top
        ix, iy, idx, idy = ( x + left,
                             y + top,
                             dx - left - slice.xright  - content.right,
                             dy - top  - slice.xbottom - content.bottom )

        for child in self.image_panel.control.children:
            child.bounds  = ( ix, iy, idx, idy )
            child.visible = ((idx > 0) and (idy > 0))


    def add ( self, item ):
        """ Adds an adapted item to the layout.
        """
        # We only need to do something here if the item being added is another
        # layout, since we only expect to have concrete controls as children.
        # So we create a panel and set its layout to the one we were given, and
        # so we will have the new panel as our child to layout:
        if isinstance( item, Layout ):
            toolkit().create_panel( self.image_panel.control ).layout = item

#-- EOF ------------------------------------------------------------------------