"""
Defines the various list editors and the list editor factory for the
wxPython user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from facets.api \
    import HasFacets, BaseFacetHandler, Range, Str, Any, Int, Instance, Bool, \
           Property, PrototypedFrom, EditorFactory

from facets.ui.ui_facets \
    import Image, EditorStyle

from facets.ui.constants \
    import scrollbar_dx

from facets.ui.controls.image_control \
    import ImageControl

from facets.ui.wx.helper \
    import FacetsUIScrolledPanel

from editor \
    import Editor

from menu \
    import MakeMenu

#-------------------------------------------------------------------------------
#  'ListEditor' class:
#-------------------------------------------------------------------------------

class ListEditor ( EditorFactory ):
    """ wxPython editor factory for list editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor to use for each list item:
    editor = Instance( EditorFactory )

    # The style of editor to use for each item:
    style = EditorStyle

    # The facet handler for each list item:
    facet_handler = Instance( BaseFacetHandler )

    # The number of list rows to display:
    rows = Range( 1, 50, 5, desc = 'the number of list rows to display' )

    # The number of list columns to create:
    columns = Range( 1, 10, 1, desc = 'the number of list columns to display' )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             kind        = self.style + '_editor' )

    def custom_editor ( self, ui, object, name, description ):
        return CustomEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             kind        = self.style + '_editor' )

    def text_editor ( self, ui, object, name, description ):
        return CustomEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             kind        = 'text_editor' )

    def readonly_editor ( self, ui, object, name, description ):
        return CustomEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description,
                             kind        = self.style + '_editor',
                             mutable     = False )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( Editor ):
    """ Simple style of editor for lists, which displays a scrolling list box
        with only one item visible at a time. An icon next to the list box
        displays a menu of operations on the list.
    """

    #-- Class Constants --------------------------------------------------------

    # Whether the list is displayed in a single row
    single_row = True

    # Menu for modifying the list
    list_menu = """
       Add Before     [_menu_before]: self.add_before()
       Add After      [_menu_after]:  self.add_after()
       ---
       Delete         [_menu_delete]: self.delete_item()
       ---
       Move Up        [_menu_up]:     self.move_up()
       Move Down      [_menu_down]:   self.move_down()
       Move to Top    [_menu_top]:    self.move_top()
       Move to Bottom [_menu_bottom]: self.move_bottom()
    """

    empty_list_menu = """
       Add: self.add_empty()
    """

    #-- Facet Definitions ------------------------------------------------------

    # The kind of editor to create for each list item
    kind = Str

    # Is the list of items being edited mutable?
    mutable = Bool( True )

    # The image used by the editor:
    image = Image( '@facets:list_editor' )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        # Initialize the facet handler to use:
        facet_handler = self.factory.facet_handler
        if facet_handler is None:
            facet_handler = self.object.base_facet( self.name ).handler

        self._facet_handler = facet_handler

        # Create a scrolled window to hold all of the list item controls:
        self.control = FacetsUIScrolledPanel( parent )

        # Remember the editor to use for each individual list item:
        editor = self.factory.editor
        if editor is None:
            editor = facet_handler.item_facet.get_editor()

        self._editor = getattr( editor, self.kind )

        # Set up the additional 'list items changed' event handler needed for
        # a list based facet:
        self.context_object.on_facet_set(
            self.update_editor_item, self.extended_name + '_items?',
            dispatch = 'ui'
        )
        self.set_tooltip()


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self.context_object.on_facet_set(
            self.update_editor_item, self.extended_name + '_items?',
            remove = True
        )
        self._dispose_items()

        super( SimpleEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        # Disconnect the editor from any control about to be destroyed:
        self._dispose_items()

        # Get rid of any previous contents:
        list_pane = self.control
        list_pane.SetSizer( None )
        list_pane.DestroyChildren()

        # Create all of the list item facet editors:
        facet_handler = self._facet_handler
        resizable     = ((facet_handler.minlen != facet_handler.maxlen) and
                         self.mutable)
        item_facet    = facet_handler.item_facet
        factory       = self.factory
        list_sizer    = wx.FlexGridSizer(
                            0, (1 + resizable) * factory.columns, 0, 0 )
        j = resizable
        for i in range( factory.columns ):
            list_sizer.AddGrowableCol( j )
            j += ( 1 + resizable )

        values        = self.value
        index         = 0
        width, height = 0, 0

        is_fake = (resizable and (len( values ) == 0))
        if is_fake:
            values = [ item_facet.default_value()[1] ]

        editor = self._editor
        for value in values:
            width1 = height = 0
            if resizable:
                ic      = ImageControl( image = self.image, selectable = True )
                control = ic.create_control( list_pane ).control

                def handler ( ):
                    self.popup_menu( control )

                ic.on_facet_set( handler, 'clicked' )
                width1, height = control.GetSize()
                width1 += 4

            try:
                proxy = ListItemProxy( self.object, self.name, index,
                                       item_facet, value )
                if resizable:
                    control.proxy = proxy
                peditor = editor( self.ui, proxy, 'value',
                                  self.description ).set( object_name = '' )
                peditor.prepare( list_pane )
                pcontrol = peditor.control
                pcontrol.proxy = proxy
            except:
                if not is_fake:
                    raise

                pcontrol = wx.Button( list_pane, -1, 'sample' )

            pcontrol.Fit()
            width2, height2 = size = pcontrol.GetSize()
            pcontrol.SetMinSize( size )
            width  = max( width, width1 + width2 )
            height = max( height, height2 )

            if resizable:
                list_sizer.Add( control, 0, wx.LEFT | wx.RIGHT, 2 )

            list_sizer.Add( pcontrol, 0, wx.EXPAND )
            index += 1

        list_pane.SetSizer( list_sizer )

        if is_fake:
           self._cur_control = control
           self.empty_list()
           control.Destroy()
           pcontrol.Destroy()

        rows = 1
        if not self.single_row:
            rows = self.factory.rows

        # Make sure we have valid values set for width and height (in case there
        # was no data to base them on):
        if width == 0:
            width = 100

        if height == 0:
            height = 20

        list_pane.SetMinSize( wx.Size(
             width + ((facet_handler.maxlen > rows) * scrollbar_dx),
             height * rows ) )
        list_pane.SetupScrolling()
        list_pane.GetParent().Layout()


    def update_editor_item ( self, object, name, old, event ):
        """ Updates the editor when an item in the object facet changes
        externally to the editor.
        """
        # If this is not a simple, single item update, rebuild entire editor:
        if (len( event.removed ) != 1) or (len( event.added ) != 1):
            self.update_editor()
            return

        # Otherwise, find the proxy for this index and update it with the
        # changed value:
        for control in self.control.GetChildren():
            proxy = control.proxy
            if proxy.index == event.index:
                proxy.value = event.added[0]
                break


    def empty_list ( self ):
        """ Creates an empty list entry (so the user can add a new item).
        """
        def handler ( ):
            self.popup_empty_menu( control )

        ic      = ImageControl( image = self.image, selectable = True )
        control = ic.create_control( self.control ).control
        ic.on_facet_set( handler, 'clicked' )
        control.is_empty = True
        proxy    = ListItemProxy( self.object, self.name, -1, None, None )
        pcontrol = wx.StaticText( self.control, -1, '   (Empty List)' )
        pcontrol.proxy = control.proxy = proxy
        self.reload_sizer( [ ( control, pcontrol ) ] )


    def reload_sizer ( self, controls, extra = 0 ):
        """ Reloads the layout from the specified list of ( button, proxy )
            pairs.
        """
        sizer = self.control.GetSizer()
        for i in xrange( (2 * len( controls )) + extra ):
            sizer.Remove( 0 )

        index = 0
        for control, pcontrol in controls:
            sizer.Add( control,  0, wx.LEFT | wx.RIGHT, 2 )
            sizer.Add( pcontrol, 1, wx.EXPAND )
            control.proxy.index = index
            index += 1

        sizer.Layout()
        self.control.SetVirtualSize( sizer.GetMinSize() )


    def get_info ( self ):
        """ Returns the associated object list and current item index.
        """
        proxy = self._cur_control.proxy
        return ( proxy.list, proxy.index )


    def popup_empty_menu ( self, control ):
        """ Displays the empty list editor popup menu.
        """
        self._cur_control = control
        control.PopupMenuXY( MakeMenu( self.empty_list_menu, self, True,
                                       control ).menu )


    def popup_menu ( self, control ):
        """ Displays the list editor popup menu.
        """
        self._cur_control = control

        # Makes sure that any text that was entered get's added:
        control.SetFocus()
        proxy    = control.proxy
        index    = proxy.index
        menu     = MakeMenu( self.list_menu, self, True, control ).menu
        len_list = len( proxy.list )
        not_full = ( len_list < self._facet_handler.maxlen )
        self._menu_before.enabled( not_full )
        self._menu_after.enabled(  not_full )
        self._menu_delete.enabled( len_list > self._facet_handler.minlen )
        self._menu_up.enabled(  index > 0 )
        self._menu_top.enabled( index > 0 )
        self._menu_down.enabled(   index < (len_list - 1) )
        self._menu_bottom.enabled( index < (len_list - 1) )
        control.PopupMenuXY( menu )


    def add_item ( self, offset ):
        """ Adds a new value at the specified list index.
        """
        list, index = self.get_info()
        index      += offset
        item_facet  = self._facet_handler.item_facet
        value       = item_facet.default_value_for( self.object, self.name )
        self.value  = list[ : index ] + [ value ] + list[ index: ]
        self.update_editor()


    def add_before ( self ):
        """ Inserts a new item before the current item.
        """
        self.add_item( 0 )


    def add_after ( self ):
        """ Inserts a new item after the current item.
        """
        self.add_item( 1 )


    def add_empty ( self ):
        """ Adds a new item when the list is empty.
        """
        list, index = self.get_info()
        self.add_item( 0 )


    def delete_item ( self ):
        """ Delete the current item.
        """
        list, index = self.get_info()
        self.value  = list[ : index ] + list[ index + 1: ]
        self.update_editor()


    def move_up ( self ):
        """ Move the current item up one in the list.
        """
        list, index = self.get_info()
        self.value  = (list[ : index - 1 ] + [ list[ index ],
                       list[ index - 1 ] ] + list[ index + 1: ])


    def move_down ( self ):
        """ Moves the current item down one in the list.
        """
        list, index = self.get_info()
        self.value  = ( list[ : index ] + [ list[ index + 1 ], list[ index ] ] +
                       list[ index + 2: ] )


    def move_top ( self ):
        """ Moves the current item to the top of the list.
        """
        list, index = self.get_info()
        self.value  = [ list[ index ] ] + list[ : index ] + list[ index + 1: ]


    def move_bottom ( self ):
        """ Moves the current item to the bottom of the list.
        """
        list, index = self.get_info()
        self.value  = list[ : index ] + list[ index + 1: ] + [ list[ index ] ]

    #-- Private Methods --------------------------------------------------------

    def _dispose_items ( self ):
        """ Disposes of each current list item.
        """
        for control in self.control.GetChildren():
            editor = getattr( control, '_editor', None )
            if editor is not None:
                editor.dispose()
                editor.control = None

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( SimpleEditor ):
    """ Custom style of editor for lists, which displays the items as a series
        of text fields. If the list is editable, an icon next to each item
        displays a menu of operations on the list.
    """

    #-- Class Constants --------------------------------------------------------

    # Whether the list is displayed in a single row. This value overrides the
    # default.
    single_row = False

    #-- Facet Definitions ------------------------------------------------------

    # Is the list editor is scrollable? This values overrides the default.
    scrollable = True

#-------------------------------------------------------------------------------
#  'ListItemProxy' class:
#-------------------------------------------------------------------------------

class ListItemProxy ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The list proxy:
    list = Property

    # The item proxies index into the original list:
    index = Int

    # Delegate all other facets to the original object:
    _ = PrototypedFrom( '_zzz_object' )

    # Define all of the private internal use values (the funny names are an
    # attempt to avoid name collisions with delegated facet names):
    _zzz_inited = Any
    _zzz_object = Any
    _zzz_name   = Any

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, object, name, index, facet, value ):
        super( ListItemProxy, self ).__init__()

        self._zzz_inited = False
        self._zzz_object = object
        self._zzz_name   = name
        self.index       = index

        if facet is not None:
            self.add_facet( 'value', facet )
            self.value = value

        self._zzz_inited = (self.index < len( self.list ))


    def _get_list ( self ):
        return getattr( self._zzz_object, self._zzz_name )


    def _value_set ( self, value ):
        if self._zzz_inited:
            self.list[ self.index ] = value

#-- EOF ------------------------------------------------------------------------