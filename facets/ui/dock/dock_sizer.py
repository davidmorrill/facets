"""
Defines the top-level layout manager class used to manage the contents of a
DockWindow.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import HasPrivateFacets, Instance, Any, Bool, implements

from facets.ui.adapters.layout \
    import Layout

from facets.ui.i_abstract_layout \
    import IAbstractLayout

from dock_constants \
    import SequenceType, no_dock_info

from dock_item \
    import DockItem

from dock_group \
    import DockGroup

from dock_region \
    import DockRegion

from dock_section \
    import DockSection

#-------------------------------------------------------------------------------
#  'DockSizer' class:
#-------------------------------------------------------------------------------

class DockSizer ( HasPrivateFacets ):
    """ Defines the top-level layout manager class used to manage the contents
        of a DockWindow.
    """

    implements ( IAbstractLayout )

    #-- Facet Definitions ------------------------------------------------------

    # The DockWindow this sizer is associated with:
    dock_window = Instance( 'facets.ui.dock.dock_window.DockWindow' )

    # The current contents of the DockSizer layout manager:
    contents = Instance( DockItem )

    # The current structure of the DockSizer layout manager:
    structure = Instance( DockItem )

    # The current maximized structure (if any) of the DockSizer layout manager:
    max_structure = Instance( DockItem )

    # The GUI toolkit specific layout manager associated with the DockSizer
    # (part of the IAbstractLayout interface):
    layout = Any

    # Is the layout in need up update?
    needs_layout = Bool( False )

    # The GUI toolkit neutral layout manager associated with the DockSizer:
    adapter = Instance( Layout )

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, contents = None, **facets ):
        """ Initializes the object.
        """
        super( DockSizer, self ).__init__( **facets )

        # Finish initializing the sizer itself:
        if contents is not None:
            self.set_contents( contents )

    #-- IAbstractLayout Interface Implementation -------------------------------

    def calculate_minimum ( self ):
        """ Calculates the minimum size needed by the sizer.
        """
        if self.contents is None:
            return ( 20, 20 )

        return self.contents.calc_min()


    def perform_layout ( self, x, y, dx, dy ):
        """ Layout the contents of the sizer based on the sizer's current size
            and position.
        """
        self.needs_layout = False

        # Ignore any recursive calls:
        if (not self._ignore_update) and (self.contents is not None):
            self._ignore_update = True
            self.contents.recalc_sizes( x, y, dx, dy )
            self._ignore_update = False

    #-- Public Methods ---------------------------------------------------------

    def set_contents ( self, contents ):
        """ Initializes the layout of a DockWindow from a content list.
        """
        from dock_control import DockControl

        if isinstance( contents, DockGroup ):
            self.contents = contents
        elif isinstance( contents, tuple ):
            self.contents = self._set_region( contents )
        elif isinstance( contents, list ):
            self.contents = self._set_section( contents, True )
        elif isinstance( contents, DockControl ):
            self.contents = self._set_section( [ contents ], True )
        else:
            raise TypeError

        # Set the owner DockWindow for the top-level group so that it can notify
        # the owner when the DockWindow becomes empty:
        self.contents.dock_window = self.dock_window

        # If no saved structure exists yet, save the current one:
        if self.structure is None:
            self.structure = self.get_structure()


    def _set_region ( self, contents ):
        items = []
        for i, item in enumerate( contents ):
            if isinstance( item, tuple ):
                items.append( self._set_region( item ) )
            elif isinstance( item, list ):
                items.append( self._set_section( item, True ) )
            elif isinstance( item, DockItem ):
                items.append( item )
            else:
                raise TypeError

        return DockRegion( contents = items )


    def _set_section ( self, contents, is_row ):
        from dock_control import DockControl

        items = []
        for item in contents:
            if isinstance( item, tuple ):
                items.append( self._set_region( item ) )
            elif isinstance( item, list ):
                items.append( self._set_section( item, not is_row ) )
            elif isinstance( item, DockControl ):
                items.append( DockRegion( contents = [ item ] ) )
            else:
                raise TypeError

        return DockSection( is_row = is_row ).set( contents = items )


    def get_structure ( self ):
        """ Returns a copy of the layout 'structure', minus the actual content
            (i.e. controls, splitters, bounds). This method is intended for use
            in persisting the current user layout, so that it can be restored in
            a future session.
        """
        if self.contents is not None:
            return self.contents.get_structure()

        return DockSection()


    def set_structure ( self, window, structure, handler = None ):
        """ Takes a previously saved 'get_structure' result and applies it to
            the contents of the sizer in order to restore a previous layout
            using a new set of controls.
        """
        section = self.contents
        if isinstance( structure, SequenceType ):
            structure = self.map_structure( structure )
        else:
            structure = structure.get_structure()

        if (section is None) or (not isinstance( structure, DockGroup )):
            return

        # Save the current structure in case a 'reset_structure' call is made
        # later:
        self.structure = self.get_structure()

        extras = []

        # Create a mapping for all the DockControls in the new structure:
        map = {}
        for control in structure.get_controls( False ):
            if control.id in map:
                control.parent.remove( control )
            else:
                map[ control.id ] = control

        # Try to map each current item into an equivalent item in the saved
        # preferences:
        for control in section.get_controls( False ):
            mapped_control = map.get( control.id )
            if mapped_control is not None:
                control.set( **mapped_control.get( 'visible', 'locked',
                    'closeable', 'resizable', 'width', 'height' ) )

                if mapped_control.user_name:
                    control.name = mapped_control.name

                if mapped_control.user_style:
                    control.style = mapped_control.style

                structure.replace_control( mapped_control, control )
                del map[ control.id ]
            else:
                extras.append( control )

        # Try to resolve all unused saved items:
        for id, item in map.items():
            # If there is a handler, see if it can resolve it:
            if handler is not None:
                control = handler.resolve_id( id )
                if control is not None:
                    item.control = control
                    continue

            # If nobody knows what it is, just remove it:
            item.parent.remove( item )

        # Check if there are any new items that we have never seen before:
        if len( extras ) > 0:
            if handler is not None:
                # Allow the handler to decide their fate:
                handler.resolve_extras( structure, extras )
            else:
                # Otherwise, add them to the top level as a new region (let the
                # user re-arrange them):
                structure.contents.append( DockRegion( contents = extras ) )

        # Finally, replace the original structure with the updated structure:
        self.set_contents( structure )


    def reset_structure ( self, window ):
        """ Restores the previously saved structure (if any).
        """
        if self.structure is not None:
            self.set_structure( window, self.structure )


    def map_structure ( self, structure ):
        """ Converts an abstract layout structure consisting of nested row and
            column weighting factors into a concrete layout structure based upon
            the current contents of the sizer.

            The format of *structure* is as follows:
            - structure = ( row [, row, ..., row] )
            - row       = row_height_weight or
                          ( row_height_weight, column [, column, ..., column] )
            - column    = column_width_weight or
                          ( column_width_weight, row [, row, ..., row] )

            Returns a concrete layout structure based on the current contents of
            the sizer and *structure*. If the number of items in *structure*
            does not match the number of items in the sizer, then None is
            returned. The 'row_height_weight' and 'column_width_weight' values
            can be positive int or float values. If non-positive or non-numeric
            values are found, None is returned.

            An example of an abstract layout is: ( 2, ( 1, 2, 1, 1 ) ), which
            describes a layout like this:

                           +----------------------------------+
                           |                                  |
                           |                                  |
                           |            ( 2, ... )            |
                           |                                  |
                           |                                  |
                           |                                  |
                           |----------------+--------+--------|
                           |                |        |        |
                           |   ( ..., 2,    |   1,   |  1 )   |
                           |                |        |        |
                           +----------------------------------+
        """
        try:
            section = self.contents
            if ((section is None)                           or
                (not isinstance( structure, SequenceType )) or
                (len( structure ) == 0)):
                return None

            width    = section.width
            height   = section.height
            controls = section.get_controls( False )
            if len( structure ) == 1:
                result = self._column_structure(
                             structure[0], controls, width, height )
            else:
                result = self._row_structure(
                             structure, controls, width, height )

            if len( controls ) != 0:
                return None

            return result
        except ValueError:
            return None


    def toggle_lock ( self ):
        """ Toggles the current 'lock' setting of the contents.
        """
        if self.contents is not None:
            self.contents.toggle_lock()


    def draw ( self, g ):
        """ Draws the contents of the sizer.
        """
        drawable = (not self.needs_layout)
        if drawable and (self.contents is not None):
            self.contents.draw( g )

        return drawable


    def object_at ( self, x, y, force = False ):
        """ Returns the object at a specified window position.
        """
        if self.contents is not None:
            return self.contents.object_at( x, y, force )

        return None


    def dock_info_at ( self, x, y, size, is_control ):
        """ Gets a DockInfo object at a specified x, y position.
        """
        if self.contents is not None:
            return self.contents.dock_info_at( x, y, size, is_control, True )

        return no_dock_info()


    def min_max ( self, window, dock_control ):
        """ Minimizes/Maximizes a specified DockControl.
        """
        if self.max_structure is None:
            self.max_structure = self.get_structure()
            for control in self.get_controls():
                control.visible = (control is dock_control)
        else:
            self.reset( window )


    def reset ( self, window ):
        """ Resets the DockSizer to a known state.
        """
        if self.max_structure is not None:
            self.set_structure( window, self.max_structure )
            self.max_structure = None


    def reset_appearance ( self ):
        """ Reset any cached values that may affect the appearance.
        """
        for control in self.get_controls():
            control.reset_appearance()


    def is_maximizable ( self ):
        """ Returns whether the sizer can be maximized now.
        """
        return (self.max_structure is None)


    def get_controls ( self, visible_only = True ):
        """ Returns all (visible) DockControls contained within the layout.
        """
        return self.contents.get_controls( visible_only )


    def close ( self ):
        """ Disposes of the contents of the sizer.
        """
        for control in self.get_controls( False ):
            control.close( layout = False, force = True )

        self.layout.layout = None

        del self.dock_window
        del self.contents
        del self.structure
        del self.max_structure
        del self.layout
        del self.adapter

    #-- Facet Event Handlers ---------------------------------------------------

    def _dock_window_set ( self, dock_window ):
        """ Handles the 'dock_window' facet being changed.
        """
        if self.contents is not None:
            self.contents.dock_window = dock_window

    #-- Private Methods --------------------------------------------------------

    def _row_structure ( self, structure, controls, width, height ):
        """ Returns a DockSection describing a series of rows for an abstract
            layout structure.
        """
        contents     = []
        total_height = self._total_size( structure )
        for item in structure:
            row_height = int( round(
                (self._item_size( item ) / total_height) * height
            ) )
            if isinstance( item, SequenceType ):
                contents.append( self._column_structure(
                                     item[1:], controls, width, row_height ) )
            else:
                contents.append( self._item_structure(
                                     controls, width, row_height ) )

        return DockSection(
            is_row   = False,
            width    = width,
            height   = height,
            contents = contents
        )


    def _column_structure ( self, structure, controls, width, height ):
        """ Returns a DockSection describing a series of columns for an abstract
            layout structure.
        """
        contents    = []
        total_width = self._total_size( structure )
        for item in structure:
            column_width = int( round(
                (self._item_size( item ) / total_width) * width
            ) )
            if isinstance( item, SequenceType ):
                contents.append( self._row_structure(
                                     item[1:], controls, column_width, height )
                )
            else:
                contents.append( self._item_structure(
                                     controls, column_width, height ) )

        return DockSection(
            is_row   = True,
            width    = width,
            height   = height,
            contents = contents
        )


    def _item_structure ( self, controls, width, height ):
        """ Returns the DockRegion/DockControl for the next available control
            when applying an abstract layout structure to a sizer.
        """
        from dock_control import DockControl

        # If there are no controls left, then abort:
        if len( controls ) == 0:
            raise ValueError

        # Pop the next available control from the list of current DockControls:
        control = controls[0]
        del controls[0]

        # Return a DockRegion/DockControl for the control using the specified
        # width and height:
        return DockRegion(
            active   = 0,
            width    = width,
            height   = height,
            contents = [ DockControl(
                id         = control.id,
                name       = control.name,
                user_name  = control.user_name,
                style      = control.style,
                user_style = control.user_style,
                visible    = control.visible,
                locked     = control.locked,
                closeable  = control.closeable,
                resizable  = control.resizable,
                width      = width,
                height     = height
            ) ]
        )


    def _total_size ( self, structure ):
        """ Returns the total size of a specified abstract layout structure.
        """
        return reduce( lambda x, y: x + self._item_size( y ), structure, 0.0 )


    def _item_size ( self, size ):
        """ Returns the size of a specified abstract layout item.
        """
        if isinstance( size, SequenceType ):
            if len( size ) == 0:
                raise ValueError

            size = size[0]

        size = float( size )
        if size <= 0.0:
            raise ValueError

        return size

#-- EOF ------------------------------------------------------------------------