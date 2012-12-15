"""
Implements the DockWindowFeature base class.

A DockWindowFeature is an optional feature of a DockControl that can be
dynamically contributed to the package. Whenever a DockControl is added to
a DockWindow, each feature will be given the opportunity to add itself to
the DockControl.

Each feature is manifested as an image that appears on the DockControl tab
(or drag bar). The user interacts with the feature using mouse clicks and
drag and drop operations (depending upon how the feature is implemented).
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from weakref \
    import ref

from facets.core_api \
    import HasPrivateFacets, Instance, Int, Str, Bool, Property

from facets.ui.menu \
    import Menu, Action

from facets.ui.ui_facets \
    import Image

from facets.ui.pyface.timer.api \
    import do_later

from dock_constants \
    import features

from dock_window \
    import DockWindow

from dock_control \
    import DockControl

from ifeature_tool \
    import IFeatureTool

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def add_feature ( feature_class ):
    """ Adds a new DockWindowFeature class to the list of available features.
    """
    global features

    result = (feature_class not in features)
    if result:
        features.append( feature_class )

        # Mark the feature class as having been installed:
        if feature_class.state == 0:
            feature_class.state = 1

    return result

#-------------------------------------------------------------------------------
#  'DockWindowFeature' class:
#-------------------------------------------------------------------------------

class DockWindowFeature ( HasPrivateFacets ):
    """ Implements "features" on DockWindows.

        See "The DockWindowFeature Feature of DockWindows" document (.doc or
        .pdf) in facets.ui.pyface.doc for details on using this class.

        Facets are defined on each feature instance. One or more feature
        instances are created for each application component that a feature
        class applies to. A given feature class might or might not apply to a
        specific application component. The feature class determines whether it
        applies to an application component when the feature is activated, or
        when a new application component is added to the DockWindow (and the
        feature is already active).
    """

    #-- Class Variables --------------------------------------------------------

    # A string value that is the user interface name of the feature as it
    # should appear in the DockWindow Features sub-menu (e.g., 'Connect'). An
    # empty string (the default) means that the feature does not appear in the
    # Features sub-menu and cannot be enabled or disabled by the user. Avoid
    # feature names that conflict with other, known features.
    feature_name = ''

    # An integer that specifies th current state of the feature
    # (0 = uninstalled, 1 = active, 2 = disabled). Usually you do not need to
    # change this value explicitly; DockWindows normally manages the value
    # automatically, setting it when the user enables or disables the feature.
    state = 0

    # List of weak references to all current instances.
    instances = []

    #-- Public Facet Definitions -----------------------------------------------

    # The DockControl instance associated with this feature. Note that features
    # are not directly associated with application components, but are instead
    # associated with the DockControl object that manages an application
    # component. The DockControl object provides the feature with access to
    # information about the parent DockWindow object, other DockControl objects
    # contained within the same DockWindow, as well as the application
    # component. This facet is automatically set by the DockWindow when the
    # feature instance is created and associated with an application component.
    dock_control = Instance( DockControl )

    #-- Public Facets (new defaults can be defined by subclasses) --------------

    # The image (icon) to display on the feature bar. If **None**, no image
    # is displayed. For images that never change, the value can be declared
    # statically in the class definition. However, the feature is free to
    # change the value at any time. Changing the value to a new
    # **ImageResource** object causes the associated image to be updated on the
    # feature bar. Setting the value to **None** removes the image from the
    # feature bar.
    image = Image

    # The tooltip to display when the pointer hovers over the image. The value
    # can be changed dynamically to reflect changes in the feature's state.
    tooltip = Str

    # The x-coordinate of a pointer event that occurred over the feature's
    # image. This can be used in cases where the event-handling for a feature is
    # sensitive to the position of the pointer relative to the feature image.
    # This is not normally the case, but the information is available if it is
    # needed.
    x = Int

    # The y-coordinate of a pointer event that occurred over the feature's
    # image.
    y = Int

    # A boolean value that specifies whether the shift key was being held down
    # when a mouse event occurred.
    shift_down = Bool( False )

    # A boolean value that specifies whether the control key was being held down
    # when a mouse event occurred.
    control_down = Bool( False )

    # A boolean value that specifies whether the alt key was being held down
    # when a mouse event occurred.
    alt_down = Bool( False )

    #-- Private Facets Definitions ---------------------------------------------

    # The current bitmap to display on the feature bar:
    bitmap = Property

    #-- Overridable Public Methods ---------------------------------------------

    def click ( self ):
        """ Handles the user left-clicking on a feature image.

            This method is designed to be overridden by subclasses. The default
            implementation attempts to perform a 'quick drag' operation (see the
            'quick_drag' method). Returns nothing.
        """
        self.quick_drag()


    def right_click ( self ):
        """ Handles the user right-clicking on a feature image.

            This method is designed to be overridden by subclasses. The default
            implementation attempts to perform a 'quick drag' operation (see the
            'quick_right_drag' method). Returns nothing. Typically, you override
            this method to display the feature's shortcut menu.
        """
        self.quick_right_drag()


    def drag ( self ):
        """ Returns the object to be dragged when the user drags a feature
            image.

            This method can be overridden by subclasses. If dragging is
            supported by the feature, then the method returns the object to be
            dragged; otherwise it returns **None**. The default implementation
            returns **None**.
        """
        return None


    def control_drag ( self ):
        """ Returns the object to be dragged when the user drags a feature
            image while pressing the 'Ctrl' key.

            This method is designed to be overridden by subclasses. If
            control-dragging is supported by the feature, then the method
            returns the object to be dragged; otherwise it returns **None**.
            The default implementation returns **None**.
        """
        return None


    def shift_drag ( self ):
        """ Returns the object to be dragged when the user drags a feature
            image while pressing the 'Shift' key.

            This method is designed to be overridden by subclasses. If
            shift-dragging is supported by the feature, then the method returns
            the object to be dragged; otherwise it returns **None**. The default
            implementation returns **None**.
        """
        return None


    def alt_drag ( self ):
        """ Returns the object to be dragged when the user drags a feature
            image while pressing the 'Alt' key.

            This method is designed to be overridden by subclasses. If
            Alt-dragging is supported by the feature, then the method returns
            the object to be dragged; otherwise it returns **None**. The default
            implementation returns **None**.
        """
        return None


    def right_drag ( self ):
        """ Returns the object to be dragged when the user right mouse button
            drags a feature image.

            This method can be overridden by subclasses. If right dragging is
            supported by the feature, then the method returns the object to be
            dragged; otherwise it returns **None**. The default implementation
            returns **None**.
        """
        return None


    def control_right_drag ( self ):
        """ Returns the object to be dragged when the user right mouse button
            drags a feature image while pressing the 'Ctrl' key.

            This method is designed to be overridden by subclasses. If
            right control-dragging is supported by the feature, then the method
            returns the object to be dragged; otherwise it returns **None**.
            The default implementation returns **None**.
        """
        return None


    def shift_control_drag ( self ):
        """ Returns the object to be dragged when the user right mouse button
            drags a feature image while pressing the 'Shift' key.

            This method is designed to be overridden by subclasses. If right
            shift-dragging is supported by the feature, then the method returns
            the object to be dragged; otherwise it returns **None**. The default
            implementation returns **None**.
        """
        return None


    def alt_right_drag ( self ):
        """ Returns the object to be dragged when the user right mouse button
            drags a feature image while pressing the 'Alt' key.

            This method is designed to be overridden by subclasses. If right
            Alt-dragging is supported by the feature, then the method returns
            the object to be dragged; otherwise it returns **None**. The
            default implementation returns **None**.
        """
        return None


    def drop ( self, object ):
        """ Handles the user dropping a specified object on a feature image.

            Parameters
            ----------
            object : any object
                The object being dropped onto the feature image

            Returns
            -------
            Nothing.

            Description
            -----------
            This method is designed to be overridden by subclasses. It is called
            whenever the user drops an object on the feature's tab or drag bar
            image. This method can be called only if a previous call to
            **can_drop()** for the same object returned **True**. The default
            implementation does nothing.
        """
        return


    def can_drop ( self, object ):
        """ Returns whether a specified object can be dropped on a feature
            image.

            Parameters
            ----------
            object : any object
                The object being dragged onto the feature image

            Returns
            -------
            **True** if *object* is a valid object for the feature to process;
            **False** otherwise.

            Description
            -----------
            This method is designed to be overridden by subclasses. It is called
            whenever the user drags an icon over the feature's tab or drag bar
            image. The method does not perform any processing on *object*; it
            only examines it. Processing of the object occurs in the **drop()**
            method, which is called when the user release the object over the
            feature's image, which typically occurs after the **can_drop()**
            method has indicated that the feature can process the object, by
            returning **True**. The default implementation returns **False**,
            indicating that the feature does not accept any objects for
            dropping.
        """
        return False


    def dispose ( self ):
        """ Performs any clean-up needed when the feature is removed from its
            associated application component (for example, when the user
            disables the feature).

            This method is designed to be overridden by subclasses. The method
            performs any clean-up actions needed by the feature, such as closing
            files, removing facet listeners, and so on. The method does not
            return a result. The default implementation does nothing.
        """
        pass

    #-- Public Methods ---------------------------------------------------------

    def popup_menu ( self, menu ):
        """ Displays a shortcut menu.

            Parameters
            ----------
            menu : facets.ui.menu.Menu object
                The menu to be displayed

            Returns
            -------
            Nothing.

            Description
            -----------
            This helper method displays the shortcut menu specified by *menu* at
            a point near the feature object's current (x,y) value, as specified
            by the **x** and **y** facets. Normally, the (x,y) value contains
            the screen location where the user clicked on the feature's tab or
            drag bar image. The effect is that the menu is displayed near the
            feature's icon, with the pointer directly over the top menu option.
        """
        window = self.dock_control.control.parent
        wx, wy = window.screen_position
        window.popup_menu( menu.create_menu( window(), self ),
                           self.x - wx - 10, self.y - wy - 10 )


    def refresh ( self ):
        """ Refreshes the display of the feature image.

            Returns
            -------
            Nothing.

            Description
            -----------
            This helper method requests the containing DockWindow to refresh the
            feature bar.
        """
        self.dock_control.feature_changed = True


    def disable ( self, disable = True ):
        """ Disables the feature.

            Returns
            -------
            Nothing.

            Description
            -----------
            This helper method temporarily disables the feature for the
            associated application component. The feature can be re-enabled by
            calling the **enable()** method. Disabling the feature removes the
            feature's icon from the feature bar, without actually deleting the
            feature (i.e., the **dispose()** method is not called).
        """
        if not disable:
            self.enable()
        else:
            self._image = self.image
            self.image  = None
            if self._image is not None:
                self.dock_control.feature_changed = True


    def enable ( self, enable = True ):
        """ Enables the feature.

            Returns
            -------
            Nothing.

            Description
            -----------
            This helper method re-enables a previously disabled feature for its
            associated application component. Enabling a feature restores the
            feature bar icon that the feature displayed at the time it was
            disabled.
        """
        if not enable:
            self.disable()
        else:
            self.image  = self._image
            self._image = None
            if self.image is not None:
                self.dock_control.feature_changed = True


    def is_enabled ( self ):
        """ Returns whether or not the feature is currently enabled.
        """
        return (self.image is not None)


    def quick_drag ( self ):
        """ Performs a quick drag and drop operation by displaying a pop-up menu
            containing all targets that the feature's xxx_drag() method can be
            dropped on. Selecting an item drops the item on the selected target.
        """
        # Get the object that would have been dragged:
        if self.control_down:
            object = self.control_drag()
        elif self.alt_down:
            object = self.alt_drag()
        elif self.shift_down:
            object = self.shift_drag()
        else:
            object = self.drag()

        # If there is an object, pop up the menu:
        if object is not None:
            self._quick_drag_menu( object )


    def quick_right_drag ( self ):
        """ Performs a quick drag and drop operation with the right mouse button
            by displaying a pop-up menu containing all targets that the
            feature's xxx_right_drag() method can be dropped on. Selecting an
            item drops the item on the selected target.
        """
        # Get the object that would have been dragged:
        if self.control_down:
            object = self.control_right_drag()
        elif self.alt_down:
            object = self.alt_right_drag()
        elif self.shift_down:
            object = self.shift_right_drag()
        else:
            object = self.right_drag()

        # If there is an object, pop up the menu:
        if object is not None:
            self._quick_drag_menu( object )

    #-- Overridable Class Methods ----------------------------------------------

    @classmethod
    def feature_for ( cls, dock_control ):
        """ Returns a single new feature object or list of new feature objects
            for a specified DockControl.

            Parameters
            ----------
            dock_control : facets.ui.dock.api.DockControl
                The DockControl object that corresponds to the application
                component being added, or for which the feature is being
                enabled.

            Returns
            -------
            An instance or list of instances of this class that will be
            associated with the application component; **None** if the feature
            does not apply to the application component.

            Description
            -----------
            This class method is designed to be overridden by subclasses.
            Normally, a feature class determines whether it applies to an
            application component by examining the component to see if it is an
            instance of a certain class, supports a specified interface, or has
            facet attributes with certain types of metadata. The application
            component is available through the *dock_control.object* facet
            attribute. Note that it is possible for *dock_control.object* to be
            **None**.

            The default implementation for this method calls the
            **is_feature_for()** class method to determine whether the feature
            applies to the specified DockControl. If it does, it calls the
            **new_feature()** class method to create the feature instances to be
            returned. If it does not, it simply returns **None**.
        """
        if cls.is_feature_for( dock_control ):
            return cls.new_feature( dock_control )

        return None


    @classmethod
    def new_feature ( cls, dock_control ):
        """ Returns a new feature instance for a specified DockControl.

            Parameters
            ----------
            dock_control : facets.ui.dock.api.DockControl
                The DockControl object that corresponds to the application
                component being added, or for which the feature is being
                enabled.

            Returns
            -------
            An instance or list of instances of this class to be associated
            with the application component; it can also return **None**.

            Description
            -----------
            This method is designed to be overridden by subclasses. This method
            is called by the default implementation of the **feature_for()**
            class method to create the feature instances to be associated with
            the application component specified by *dock_control*. The default
            implementation returns the result of calling the class constructor
            as follows::

                cls( dock_control=dock_control )

        """
        return cls( dock_control = dock_control )


    @classmethod
    def is_feature_for ( self, dock_control ):
        """ Returns whether this class is a valid feature for the application
            object corresponding to a specified DockControl.

            Parameters
            ----------
            dock_control : facets.ui.dock.api.DockControl
                The DockControl object that corresponds to the application
                component being added, or for which the feature is being
                enabled.

            Returns
            -------
            **True** if the feature applies to the application object associated
            with the *dock_control*; **False** otherwise.

            Description
            -----------
            This class method is designed to be overridden by subclasses. It is
            called by the default implementation of the **feature_for()** class
            method to determine whether the feature applies to the application
            object specified by *dock_control*. The default implementation
            always returns **True**.
        """
        return True

    #-- Private Methods --------------------------------------------------------

    def _set_event ( self, event ):
        """ Sets the feature's 'event' facets for a specified mouse 'event'.
        """
        self.set( x            = event.screen_x,
                  y            = event.screen_y,
                  shift_down   = event.shift_down,
                  control_down = event.control_down,
                  alt_down     = event.alt_down )


    def _quick_drag_menu ( self, object ):
        """ Displays the quick drag menu for a specified drag object.
        """

        # Get all the features it could be dropped on:
        feature_lists = []
        if isinstance( object, IFeatureTool ):
            msg = 'Apply to'
            for dc in self.dock_control.dock_controls:
                if (dc.visible and
                    (object.feature_can_drop_on( dc.object ) or
                     object.feature_can_drop_on_dock_control( dc ))):
                    from feature_tool import FeatureTool

                    feature_lists.append( [ FeatureTool( dock_control = dc ) ] )
        else:
            msg = 'Send to'
            for dc in self.dock_control.dock_controls:
                if dc.visible:
                    allowed = [ f for f in dc.features
                                if (f.feature_name != '') and
                                    f.can_drop( object ) ]
                    if len( allowed ) > 0:
                        feature_lists.append( allowed )

        # If there are any compatible features:
        if len( feature_lists ) > 0:
            # Create the pop-up menu:
            features = []
            actions  = []
            for list in feature_lists:
                if len( list ) > 1:
                    sub_actions = []
                    for feature in list:
                        sub_actions.append( Action(
                            name   = '%s Feature' % feature.feature_name,
                            action = "self._drop_on(%d)" % len( features ) )
                        )
                        features.append( feature )

                    actions.append( Menu(
                        name = '%s the %s' % ( msg, feature.dock_control.name ),
                        *sub_actions )
                    )
                else:
                    actions.append( Action(
                        name   = '%s %s' % ( msg, list[ 0 ].dock_control.name ),
                        action = "self._drop_on(%d)" % len( features ) )
                    )
                    features.append( list[0] )

            # Display the pop-up menu:
            self._object   = object
            self._features = features
            self.popup_menu( Menu( name = 'popup', *actions ) )
            self._object = self._features = None


    def _drop_on ( self, index ):
        """ Drops the current object on the feature selected by the user.
        """
        object = self._object
        if isinstance( object, IFeatureTool ):
            dc = self._features[ index ].dock_control
            object.feature_dropped_on( dc.object )
            object.feature_dropped_on_dock_control( dc )
        else:
            self._features[ index ].drop( object )

    #-- Public Class Methods ---------------------------------------------------

    def new_feature_for ( cls, dock_control ):
        """ Returns a feature object for use with the specified DockControl (or
            **None** if the feature does not apply to the DockControl object).
        """
        result = cls.feature_for( dock_control )
        if result is not None:
            cls.instances = [ aref for aref in cls.instances
                                   if aref() is not None ]
            if isinstance( result, DockWindowFeature ):
                result = [ result ]

            cls.instances.extend( [ ref( feature ) for feature in result ] )

        return result

    new_feature_for = classmethod( new_feature_for )


    def toggle_feature ( cls, action ):
        """ Toggles the feature on or off.
        """
        if cls.state == 0:
            cls.state = 1
            add_feature( cls )
            for control in action.window.control.children:
                # fixme: Is this correct?...
                window = getattr( control(), 'owner', None )
                if isinstance( window, DockWindow ):
                    do_later( window.update_layout )
        else:
            method    = 'disable'
            cls.state = 3 - cls.state
            if cls.state == 1:
                method = 'enable'
            cls.instances = [ aref for aref in cls.instances
                                   if aref() is not None ]
            for aref in cls.instances:
                feature = aref()
                if feature is not None:
                    getattr( feature, method )()

    toggle_feature = classmethod( toggle_feature )

    #-- Property Implementations -----------------------------------------------

    def _get_bitmap ( self ):
        if self.image is None:
            return None

        return self.image.bitmap

    #-- Pyface Menu Iinterface -------------------------------------------------

    def add_to_menu ( self, menu_item ):
        """ Adds a menu item to the menu bar being constructed.
        """
        pass


    def add_to_toolbar ( self, toolbar_item ):
        """ Adds a tool bar item to the tool bar being constructed.
        """
        pass


    def can_add_to_menu ( self, action ):
        """ Returns whether the action should be defined in the user interface.
        """
        return True


    def can_add_to_toolbar ( self, action ):
        """ Returns whether the toolbar action should be defined in the user
            interface.
        """
        return True


    def perform ( self, action ):
        """ Performs the action described by a specified Action object.
        """
        action = action.action
        if action[:5] == 'self.':
            eval( action, globals(), { 'self': self } )
        else:
            getattr( self, action )()

#-- EOF ------------------------------------------------------------------------