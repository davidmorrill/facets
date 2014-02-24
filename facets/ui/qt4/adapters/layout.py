"""
Defines a Qt4 specific concrete implementation of the Layout base class that
adapts a Qt4 layout manager to provide a set of toolkit neutral properties and
methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
    import Qt, QSize, QRect

from PyQt4.QtGui \
    import QLayout, QSpacerItem, QWidget, QWidgetItem, QFrame

from facets.core_api \
    import Int

from facets.ui.adapters.layout \
    import Layout

from layout_item \
    import layout_item_adapter

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from alignment values to corresponding  flags:
align_map = {
    'top':     int( Qt.AlignTop ),
    'bottom':  int( Qt.AlignBottom ),
    'left':    int( Qt.AlignLeft ),
    'right':   int( Qt.AlignRight ),
    'hcenter': int( Qt.AlignHCenter ),
### 'vcenter': Qt.AlignVCenter
}

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def adapted_layout ( layout ):
    """ Returns a correctly adapted version of the specified layout mananger.
    """
    if layout is None:
        return None

    return layout_adapter( layout )


def layout_adapter ( layout, is_vertical = False, columns = 0 ):
    """ Returns the layout adapter associated with the specified layout manager.
    """
    adapter = getattr( layout, 'adapter', None )
    if adapter is not None:
        return adapter

    return QtLayout(
        layout, is_vertical = is_vertical, columns = columns
    )

#-------------------------------------------------------------------------------
#  'QtLayout' class:
#-------------------------------------------------------------------------------

class QtLayout ( Layout ):
    """ Defines an Qt4 specific concrete implementation of the Layout base class
        that adapts a Qt4 layout manager to provide a set of toolkit neutral
        properties and methods.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The numbers of columns in a grid layout:
    columns = Int

    #-- Private Facet Definitions ----------------------------------------------

    # The current row in a grid layout:
    _row = Int

    # The current column in a grid layout:
    _column = Int

    #-- Concrete Methods -------------------------------------------------------

    def do_layout ( self ):
        """ Lays out the controls belonging to the layout manager.
        """
        # fixme: The Qt4 docs say that you should never have to explicitly
        # ask for a layout. we'll see...
        # self.layout.update()
        pass


    def clear ( self ):
        """ Clears the contents of the layout.
        """
        layout = self.layout
        while layout.takeAt( 0 ) is not None: pass


    def add ( self, item, left = 0, right = 0, top = 0, bottom = 0,
                          stretch = 0, fill = True, align = '' ):
        """ Adds a specified item to the layout manager with margins determined
            by the specified values for **left**, **right**, **top** and
            **bottom**.

            If **stretch** is 0, the item only receives as much space in the
            layout direction as it requires. If > 0, it receives an amount of
            space proportional to **stretch** when compared to the other items
            having a non-zero **stretch** value.

            If **fill** is False, the item only is the width or height it
            requests. If True, the item is expanded to fill the full width or
            height assigned to the layout manager.

            If **align** is one of the values: 'top', 'bottom', 'left',
            'right', 'hcenter' or 'vcenter', the item will be aligned
            accordingly; otherwise no special alignment is made. Note that a
            list of such values can also be specified.
        """
        layout         = self.layout
        lm, tm, rm, bm = layout.getContentsMargins()

        # Update the layout's margins and get any pre/post spacing that needs
        # to be added along with the item:
        if self.is_vertical:
            pre, post = top, bottom
            nlm       = max( lm, left )
            nrm       = max( rm, right )
            if (nlm != lm) or (nrm != rm):
                layout.setContentsMargins( nlm, tm, nrm, bm )
        else:
            pre, post = left, right
            ntm       = max( tm, top )
            nbm       = max( bm, bottom )
            if (ntm != tm) or (nbm != bm):
                layout.setContentsMargins( lm, ntm, rm, nbm )

        # Determine the correct alignment flags to use:
        if not isinstance( align, list ):
            alignment = align_map.get( align, 0 )
        else:
            alignment = 0
            for align_item in align:
                alignment |= align_map.get( align_item, 0 )

        if stretch > 0:
            ### if self.is_vertical:
            ###     alignment &= (~Qt.AlignVCenter)
            ### else:
            alignment &= (~Qt.AlignHCenter)

        # fixme: Do we need this?...
        ### if not fill:
        ###     alignment = Qt.AlignCenter

        if self.columns > 0:
            # Handle adding an item to a grid layout:
            if not isinstance( item, tuple ):
                item = item()
                if isinstance( item, QWidget ):
                    layout.addWidget( item, self._row, self._column )
                else:
                    layout.addLayout( item, self._row, self._column )

            # Advance to the next grid cell:
            self._column += 1
            if self._column >= self.columns:
                self._column = 0
                self._row   += 1
        else:
            # Check if item is a spacer (and convert it if it is):
            if isinstance( item, tuple ):
                item = QSpacerItem( *item )
            else:
                if item is None:
                    from facets.extra.helper.debug import called_from; called_from(10)
                item = item()

            if isinstance( item, QWidget ):
                # Item is a widget, add any padding as spacing:
                if pre > 0:
                    layout.addSpacing( pre )

                # Add the item itself to the layout:
                if alignment == 0:
                    layout.addWidget( item, stretch )
                else:
                    layout.addWidget( item, stretch, alignment )

                # Add any trailing spacing as needed:
                if post > 0:
                    layout.addSpacing( post )
            elif isinstance( item, QSpacerItem ):
                layout.addSpacerItem( item )
            else:
                # Add the item layout or spacer to the layout:
                layout.addLayout( item, stretch )

                # Get the item's current margins and add any pre/post spacing
                # as increases to the item's margins:
                lm, tm, rm, bm = item.getContentsMargins()

                if pre > 0:
                    if self.is_vertical:
                        tm += pre
                    else:
                        lm += pre

                if post > 0:
                    if self.is_vertical:
                        bm += post
                    else:
                        rm += post

                if (pre > 0) or (post > 0):
                    item.setContentsMargins( lm, tm, rm, bm )


    def add_separator ( self, parent ):
        """ Adds a separator to the layout.
        """
        control = QFrame()
        control.setFrameShadow( QFrame.Sunken )

        if self.is_vertical or (self.columns > 0):
            control.setFrameShape( QFrame.HLine )
            control.setMinimumHeight( 5 )
        else:
            control.setFrameShape( QFrame.VLine )
            control.setMinimumWidth( 5 )

        if self.columns > 0:
            self.layout.addWidget( control, self._row, 0, 1, self.columns )
            self._row += 1
        else:
            self.layout.addWidget( control )


    def remove ( self, item ):
        """ Removes the specified adapted item from the layout manager.
        """
        self.layout.removeWidget( item() )


    def set_stretchable_column ( self, column ):
        """ Marks the 'column'th column of a grid layout as 'stretchable'.
        """
        self.layout.setColumnStretch( column, 1 )


    def set_stretchable_row ( self, row ):
        """ Marks the 'row'th row of a grid layout as 'stretchable'.
        """
        self.layout.setRowStretch( row, 1 )


    def create_generic_layout ( self, layout ):
        """ Returns a generic GUI toolkit specific layout manager that will
            delegate all of its toolkit specific layout methods to the
            corresponding methods in the IAbstractLayout interface implemented
            by the specified **layout** object.
        """
        return GenericLayout( layout )

    #-- Layout Property Implementations ----------------------------------------

    def _get_children ( self ):
        layout = self.layout
        print 'layout.count():', layout.count()
        return [ layout_item_adapter( layout.itemAt( i ) )
                 for i in xrange( layout.count() ) ]


    def _get_size ( self ):
        rect = self.layout.geometry()

        return ( rect.width(), rect.height() )

    def _set_size ( self, dx_dy ):
        # fixme: For now we won't do anything, wait until we see what breaks...
        pass


    def _get_bounds ( self ):
        rect = self.layout.geometry()

        return ( rect.x(), rect.y(), rect.width(), rect.height() )

    #-- Private Methods --------------------------------------------------------

    def update ( self, x, y, dx, dy ):
        """ Handles a control adapter request to perform a layout update. Since
            Qt claims that you shoud not normallly need to update layouts
            manually, we only request a layout if the actual layout manager is
            one of our GenericLayout instances.
        """
        layout = self.layout
        if isinstance( layout, GenericLayout ):
            layout.setGeometry( QRect( x, y, dx, dy ) )
            return True

        return False

#-------------------------------------------------------------------------------
#  'GenericLayout' class:
#-------------------------------------------------------------------------------

class GenericLayout ( QLayout ):
    """ An instance of GenericLayout is automatically created whenever a
        layout manager that implements IAbstractLayout is used. The
        GenericLayout instance routes all Qt specific layout manager calls to
        the appropriate methods of the instance implementing IAbstractLayout.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, layout ):
        self.layout = layout
        self.items  = []
        self._cached_size_hint = None

        super( GenericLayout, self ).__init__()


    def invalidate ( self ):
        QLayout.invalidate( self )

        self._cached_size_hint = None


    def sizeHint ( self ):
        """ Calculates the preferred size requested by the layout manager.
        """
        if self._cached_size_hint is None:
            self._cached_size_hint = QSize( *self.layout.calculate_minimum() )

        return self._cached_size_hint

    minimumSize = sizeHint


    def setGeometry ( self, rect ):
        """ Layout the contents of the layout manager based upon the area
            provided by the specified rectangle.
        """
        QLayout.setGeometry( self, rect )

        self.layout.perform_layout( rect.x(), rect.y(),
                                    rect.width(), rect.height() )


    def count ( self ):
        return len( self.items )


    def addItem ( self, item ):
        self.items.append( item )
        self.layout.add( item )


    def addSpacing ( self, amount ):
        self.layout.add( amount )


    def addWidget ( self, widget, stretch = None ):
        from facets.ui.qt4.adapters.control import control_adapter

        self.items.append( QWidgetItem( widget ) )
        self.layout.add( control_adapter( widget ) )


    def itemAt ( self, index ):
        if 0 <= index < len( self.items ):
            return self.items[ index ]

        return None


    def takeAt ( self, index ):
        if 0 <= index < len( self.items ):
            result = self.items[ index ]
            del self.items[ index ]

            return result

        return None


    def removeWidget ( self, widget ):
        #QLayout.removeWidget( self, widget )
        pass


    def addLayout ( self, layout, stretch = None ):
        #QLayout.addLayout( self, layout )
        self.layout.add( layout_adapter( layout ) )

#-- EOF ------------------------------------------------------------------------