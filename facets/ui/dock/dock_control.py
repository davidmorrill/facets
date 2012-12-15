"""
Represents a region of a DockWindow used to display a single developer supplied
control.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Instance, Int, Event, Str, Bool, Property, Callable

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.ui.pyface.timer.api \
    import do_later

from dock_constants \
    import FEATURE_NONE, FEATURE_PRE_NORMAL, NORMAL_FEATURES, DockStyle, \
           SequenceType, features

from dock_item \
    import DockItem

from idockable \
    import IDockable

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Reference to the DockSizer class:
DockSizer = None

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def dock_control_for ( control ):
    """ Returns the DockControl object associated with the Control object
        specified by *control*, or None if the control is not being managed by a
        DockWindow. The control may be a (grand-)child control of the actual
        control object associated with the DockControl object returned.
    """
    while True:
        if control is None:
            return None

        dc = getattr( control, '_dock_control', None )
        if isinstance( dc, DockControl ):
            return dc

        control = control.parent

#-------------------------------------------------------------------------------
#  'DockControl' class:
#-------------------------------------------------------------------------------

class DockControl ( DockItem ):
    """ Represents a region of a DockWindow used to display a single developer
        supplied control.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The number of global DockWindowFeature's that were available the last
    # the time the feature set was checked:
    num_global_features = Int

    # The number of window DockWindowFeature's that were available the last
    # the time the feature set was checked:
    num_window_features = Int

    # A feature associated with the DockControl has been changed:
    feature_changed = Event

    # The image to display for this control:
    image = Instance( AnImageResource )

    # Has the user set the name of the control?
    user_name = Bool( False )

    # The object (if any) associated with this control:
    object = Property

    # The id of this control:
    id = Str

    # Style of drag bar/tab:
    style = DockStyle

    # Has the user set the style for this control:
    user_style = Bool( False )

    # Category of control when it is dragged out of the DockWindow:
    export = Str

    # Is the control visible?
    visible = Bool( True )

    # Is the control's drag bar locked?
    locked = Bool( False )

    # Can the control be resized?
    resizable = Bool( True )

    # Function to call when a DockControl is requesting to be closed:
    on_close = Callable

    # (Optional) object that allows the control to be docked with a different
    # DockWindow:
    dockable = Instance( IDockable )

    # List of all other DockControl's in the same DockWindow:
    dock_controls = Property

    # Event fired when the control's notebook tab is activated by the user:
    activated = Event

    #-- Method Implementations -------------------------------------------------

    def calc_min ( self, use_size = False ):
        """ Calculates the minimum size of the control.
        """
        self.check_features()
        dx, dy = self.width, self.height
        if self.control is not None:
            dx, dy = self.control.best_size
            if self.width < 0:
                self.width, self.height = dx, dy

        if use_size and (self.width >= 0):
            return ( self.width, self.height )

        return ( dx, dy )


    def recalc_sizes ( self, x, y, dx, dy ):
        """ Layout the contents of the region based on the specified bounds.
        """
        self.width  = dx = max( 0, dx )
        self.height = dy = max( 0, dy )
        self.control.bounds = self.bounds = ( x, y, dx, dy )


    def check_features ( self ):
        """ Checks to make sure that all applicable DockWindowFeatures have been
            applied.
        """
        global features

        window_features = []
        window          = self.owner
        if window is not None:
            window_features = window.features

        nw  = len( window_features )
        nwf = self.num_window_features
        ng  = len( features )
        ngf = self.num_global_features
        if (self.control is None) or ((ngf >= ng) and  (nwf >= nw)):
            return

        if self.control.parent.owner.dock_sizer is not None:
            applied_features = set( features[ : ngf ] )
            applied_features.union( window_features[ : nwf ] )
            for feature_class in (features[ ngf: ] + window_features[ nwf: ]):
                self.check_feature( feature_class, applied_features )

            self.num_global_features = ng
            self.num_window_features = nw


    def check_feature ( self, feature_class, applied_features ):
        """ Adds the DockWindowFeature specifed by *feature_class* to the
            DockControl if it is valid for the control. The feature can only be
            added if it is not in the set of features that have already been
            applied to the control, as specified by *applied_features*.
        """
        if feature_class not in applied_features:
            applied_features.add( feature_class )
            feature = feature_class.new_feature_for( self )
            if feature is not None:
                if not isinstance( feature, SequenceType ):
                    feature = [ feature ]

                self.features.extend( list( feature ) )
                mode = self.feature_mode
                if mode == FEATURE_NONE:
                    self.feature_mode = FEATURE_PRE_NORMAL

                if feature_class.state != 1:
                    for item in feature:
                        item.disable()
                else:
                    self._tab_width = None
                    if mode in NORMAL_FEATURES:
                        self.set_feature_mode()


    def set_visibility ( self, visible ):
        """ Sets the visibility of the control.
        """
        if self.control is not None:
            self.control.visible = visible


    def get_controls ( self, visible_only = True ):
        """ Returns all DockControl objects contained in the control.
        """
        if visible_only and (not self.visible):
            return []

        return [ self ]


    def get_image ( self ):
        """ Gets the image (if any) associated with the control.
        """
        if self._image is None:
            if self.image is not None:
                self._image = self.image.bitmap

        return self._image


    def show ( self, visible = True, layout = True ):
        """ Hides or shows the control.
        """
        if visible != self.visible:
            self.visible = visible
            self._layout( layout )


    def select ( self ):
        """ Select the item.
        """
        self.control.parent.owner.selected = self


    def activate ( self, layout = True ):
        """ Activates a control (i.e. makes it the active page within its
            containing notebook).
        """
        if self.parent is not None:
            self.parent.activate( self, layout )


    def close ( self, layout = True, force = False ):
        """ Closes the control.
        """
        control = self.control
        if control is not None:
            window = control.parent

            if self.on_close is not None:
                # Ask the handler if it is OK to close the control:
                if self.on_close( self, force ) is False:
                    # If not OK to close it, we're done:
                    return

            elif self.dockable is not None:
                if self.dockable.dockable_close( self, force ) is False:
                    # If not OK to close it, we're done:
                    return

            else:
                # No close handler, just destroy the widget ourselves:
                control.destroy()

            # Reset all features:
            self.reset_features()

            # Remove the DockControl from the sizer:
            self.parent.remove( self )

            # Mark the DockControl as closed (i.e. has no associated widget or
            # parent):
            self.control = self.parent = self.dockable = \
            control._dock_control = None

            # Make sure we are not the currently selected DockControl for the
            # DockWindow we are contained in:
            owner = window.owner
            if owner.selected is self:
                owner.selected = None

            # If a screen update is requested, lay everything out again now:
            if layout:
                window.update()


    def object_at ( self, x, y ):
        """ Returns the object at a specified window position.
        """
        return None


    def get_structure ( self ):
        """ Returns a copy of the control 'structure', minus the actual content.
        """
        return self.clone_facets( [
            'id', 'name', 'user_name', 'style', 'user_style', 'visible',
            'locked', 'closeable', 'resizable', 'width', 'height'
        ] )


    def toggle_lock ( self ):
        """ Toggles the 'lock' status of the control.
        """
        self.locked = not self.locked


    def dump ( self, indent ):
        """ Prints the contents of the control.
        """
        print ('%sControl( %08X, name = %s, id = %s,\n%s'
                          'style = %s, locked = %s,\n%s'
                          'closeable = %s, resizable = %s, visible = %s\n%s'
                          'width = %d, height = %d )' % (
              ' ' * indent, id( self ), self.name, self.id,
              ' ' * (indent + 9), self.style, self.locked,
              ' ' * (indent + 9), self.closeable, self.resizable, self.visible,
              ' ' * (indent + 9), self.width, self.height ))


    def draw ( self, g ):
        """ Draws the contents of the control.
        """
        pass


    def set_name ( self, name, layout = True ):
        """ Sets a new name for the control.
        """
        if name != self.name:
            self.name = name
            self._layout( layout )


    def reset_tab ( self ):
        """ Resets the state of the tab.
        """
        self.reset_features()
        self._layout()


    def reset_features ( self ):
        """ Resets all currently defined features.
        """
        for feature in self.features:
            feature.dispose()

        self.features            = []
        self.num_global_features = self.num_window_features = 0


    def reset_appearance ( self ):
        """ Reset any cached values that may affect the appearance of the item.
        """
        parent = self.parent
        if parent is not None:
            parent._is_notebook = parent._is_full_width_tab = None

            # fixme: We need to fire a fake property change to force the
            # 'tab_width' property to get recalculated...
            self.facet_property_set( 'tab_state', self.tab_state )


    def _layout ( self, layout = True ):
        """ Forces the containing DockWindow to be laid out.
        """
        if layout and (self.control is not None):
            do_later( self.control.parent.update )

    #-- Facet Event Handlers ---------------------------------------------------

    def _feature_changed_set ( self ):
        """ Handles the 'feature_changed' facet being changed.
        """
        self.set_feature_mode()


    def _control_set ( self, old, new ):
        """ Handles the 'control' facet being changed.
        """
        self._tab_width = None

        if old is not None:
            old._dock_control = None

        if new is not None:
            new._dock_control = self
            self.reset_tab()


    def _name_set ( self ):
        """ Handles the 'name' facet being changed.
        """
        self._tab_width = self._tab_name = None


    def _style_set ( self ):
        """ Handles the 'style' facet being changed.
        """
        self.reset_appearance()


    def _image_set ( self ):
        """ Handles the 'image' facet being changed.
        """
        self._image = None


    def _visible_set ( self ):
        """ Handles the 'visible' facet being changed.
        """
        if self.parent is not None:
            self.parent.show_hide( self )


    def _dockable_set ( self, dockable ):
        """ Handles the 'dockable' facet being changed.
        """
        if dockable is not None:
            dockable.dockable_bind( self )


    def _resizable_set ( self ):
        """ Handles the 'resizable' facet being changed.
        """
        if self.parent is not None:
            self.parent.reset()

    #-- Property Implementations -----------------------------------------------

    def _get_object ( self ):
        return getattr( self.control, '_object', None )


    def _get_dock_controls ( self ):
        # Get all of the DockControls in the parent DockSizer:
        controls = self.control.parent.owner.dock_sizer.contents.get_controls(
            False
        )

        # Remove ourself from the list:
        try:
            controls.remove( self )
        except:
            pass

        return controls

#-- EOF ------------------------------------------------------------------------