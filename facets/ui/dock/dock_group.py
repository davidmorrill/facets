"""
Base container class for any region of a DockWindow that can contain multiple
items.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.core_api \
    import List, Property, Constant

from dock_item \
    import DockItem

from dock_control \
    import DockControl

#-------------------------------------------------------------------------------
#  'DockGroup' class:
#-------------------------------------------------------------------------------

class DockGroup ( DockItem ):
    """ Base container class for any region of a DockWindow that can contain
        multiple items.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The contents of the group:
    contents = List

    # The UI name of this group:
    name = Property

    # Style of drag bar/tab:
    style = Property

    # Are the contents of the group resizable?
    resizable = Property

    # Category of control when it is dragged out of the DockWindow:
    export = Constant( '' )

    # Is the group visible?
    visible = Property

    # Content items which are visible:
    visible_contents = Property

    # Can the control be closed?
    closeable = Property

    # The control associated with this group:
    control = Property

    # Is the group locked?
    locked = Property

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        controls = self.get_controls()

        return (', '.join( sorted( [ c.name for c in controls ] ) ))


    def _get_visible ( self ):
        for item in self.contents:
            if item.visible:
                return True

        return False


    def _get_visible_contents ( self ):
        return [ item for item in self.contents if item.visible ]


    def _get_closeable ( self ):
        for item in self.contents:
            if not item.closeable:
                return False

        return True


    def _get_style ( self ):
        # Make sure there is at least one item in the group:
        if len( self.contents ) > 0:
            # Return the first item's style:
            return self.contents[0].style

        # Otherwise, return a default style for an empty group:
        return 'horizontal'


    def _get_resizable ( self ):
        if self._resizable is None:
            self._resizable = False
            for control in self.get_controls():
                if control.resizable:
                    self._resizable = True
                    break

        return self._resizable


    def _get_control ( self ):
        if len( self.contents ) == 0:
            return None

        return self.contents[0].control


    def _get_locked ( self ):
        return self.contents[0].locked

    #-- Method Implementations -------------------------------------------------

    def show ( self, visible = True, layout = True ):
        """ Hides or shows the contents of the group.
        """
        for item in self.contents:
            item.show( visible, False )

        if layout:
            self.control.parent.update()


    def replace_control ( self, old, new ):
        """ Replaces a specified DockControl by another.
        """
        for i, item in enumerate( self.contents ):
            if isinstance( item, DockControl ):
                if item is old:
                    self.contents[i] = new
                    new.parent = self

                    return True

            elif item.replace_control( old, new ):
                return True

        return False


    def get_controls ( self, visible_only = True ):
        """ Returns all DockControl objects contained in the group.
        """
        contents = self.visible_contents if visible_only else self.contents
        result   = []
        for item in contents:
            result.extend( item.get_controls( visible_only ) )

        return result


    def get_image ( self ):
        """ Gets the image (if any) associated with the group.
        """
        if len( self.contents ) == 0:
            return None

        return self.contents[0].get_image()


    def get_cursor ( self, event ):
        """ Gets the cursor to use when the mouse is over the item.
        """
        return 'arrow'


    def toggle_lock ( self ):
        """ Toggles the 'lock' status of every control in the group.
        """
        for item in self.contents:
            item.toggle_lock()


    def close ( self, layout = True, force = False ):
        """ Closes the control.
        """
        window = self.control.parent

        for item in self.contents[:]:
            item.close( False, force = force )

        if layout:
            window.update()


    def reset ( self ):
        """ Resets any cached property values that may depend upon the group's
            children.
        """
        self._resizable = None

        if self.parent is not None:
            self.parent.reset()

#-- EOF ------------------------------------------------------------------------