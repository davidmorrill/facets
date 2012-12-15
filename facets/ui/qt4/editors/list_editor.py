"""
Defines the various list editors and the list editor factory for the
PyQt user interface toolkit..
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
    import QPoint

from PyQt4.QtGui \
    import QWidget, QGridLayout, QFrame, QScrollArea, QPushButton, QLayout, \
           QLabel

from facets.api \
    import HasFacets, BaseFacetHandler, Range, Str, Any, Int, Instance, \
           Property, Bool, PrototypedFrom, EditorFactory

from facets.ui.ui_facets \
    import EditorStyle

from editor \
    import Editor

from facets.ui.qt4.helper \
    import IconButton

from menu \
    import MakeMenu

#-------------------------------------------------------------------------------
#  'ListEditor' class:
#-------------------------------------------------------------------------------

class ListEditor ( EditorFactory ):
    """ PyQt editor factory for list editors.
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
    columns = Range( 1, 10, 5, desc = 'the number of list columns to display' )

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
        with only one item visible at a time. A icon next to the list box
        displays a menu of operations on the list.
    """

    #-- Class Constants --------------------------------------------------------

    # Whether the list is displayed in a single row:
    single_row = True

    # Menu for modifying the list
    list_menu = """
       Add &Before     [_menu_before]: self.add_before()
       Add &After      [_menu_after]:  self.add_after()
       ---
       &Delete         [_menu_delete]: self.delete_item()
       ---
       Move &Up        [_menu_up]:     self.move_up()
       Move &Down      [_menu_down]:   self.move_down()
       Move to &Top    [_menu_top]:    self.move_top()
       Move to &Bottom [_menu_bottom]: self.move_bottom()
    """

    empty_list_menu = """
       Add: self.add_empty()
    """

    #-- Facet Definitions ------------------------------------------------------

    # The kind of editor to create for each list item:
    kind = Str

    # Is the list of items being edited mutable?
    mutable = Bool( True )

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
        self.control = QScrollArea( parent )
        self.control.setFrameShape( QFrame.NoFrame )

        # Create a widget with a grid layout as the container.
        self._list_pane = QWidget()
        layout = QGridLayout( self._list_pane )
        layout.setMargin( 0 )

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

        super( SimpleEditor, self ).dispose()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        # Disconnect the editor from any control about to be destroyed:
        self._dispose_items()

        list_pane = self._list_pane
        layout    = list_pane.layout()

        # Create all of the list item facet editors:
        facet_handler = self._facet_handler
        resizable     = ((facet_handler.minlen != facet_handler.maxlen) and
                         self.mutable)
        item_facet    = facet_handler.item_facet
        values        = self.value
        index         = 0

        is_fake       = (resizable and (len( values ) == 0))
        if is_fake:
            values = [ item_facet.default_value()[1] ]

        editor = self._editor
        # FIXME: Add support for more than one column.
        for value in values:
            if resizable:
                control = IconButton( '@facets:list_editor',  self.popup_menu )
                layout.addWidget( control, index, 0 )

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

                pcontrol = QPushButton( 'sample', list_pane )

            if isinstance( pcontrol, QWidget ):
                layout.addWidget( pcontrol, index, 1 )
            else:
                layout.addLayout( pcontrol, index, 1 )

            index += 1

        if is_fake:
           self._cur_control = control
           self.empty_list()
           control.setParent( None )

        if self.single_row:
            rows = 1
        else:
            rows = self.factory.rows

        #list_pane.SetSize( wx.Size(
        #     width + ((facet_handler.maxlen > rows) * scrollbar_dx),
        #     height * rows ) )

        # QScrollArea can have problems if the widget being scrolled is set too
        # early (ie. before it contains something).
        if self.control.widget() is None:
            self.control.setWidget( list_pane )


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
        for control in self.control.widget().children():
            if isinstance( control, QLayout ):
                continue

            proxy = control.proxy
            if proxy.index == event.index:
                proxy.value = event.added[0]
                break


    def empty_list ( self ):
        """ Creates an empty list entry (so the user can add a new item).
        """
        control          = IconButton( '@facets:list_editor', self.popup_menu )
        control.is_empty = True
        proxy          = ListItemProxy( self.object, self.name, -1, None, None )
        pcontrol       = QLabel( '   (Empty List)' )
        pcontrol.proxy = control.proxy = proxy
        self.reload_sizer( [ ( control, pcontrol ) ] )


    def reload_sizer ( self, controls, extra = 0 ):
        """ Reloads the layout from the specified list of ( button, proxy )
            pairs.
        """
        layout = self._list_pane.layout()

        child = layout.takeAt( 0 )
        while child is not None:
            child = layout.takeAt( 0 )

        del child

        index = 0
        for control, pcontrol in controls:
            layout.addWidget( control )
            layout.addWidget( pcontrol )

            control.proxy.index = index
            index += 1


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
                                       control ).menu, 0, 0 )


    def popup_menu ( self ):
        """ Displays the list editor popup menu.
        """
        self._cur_control = control = self.control.sender()
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
        menu.exec_( control.mapToGlobal( QPoint( 0, 0 ) ) )


    def add_item ( self, offset ):
        """ Adds a new value at the specified list index.
        """
        list, index = self.get_info()
        index      += offset
        item_facet  = self._facet_handler.item_facet
        dv          = item_facet.default_value()
        if dv[0] == 7:
            func, args, kw = dv[1]
            if kw is None:
                kw = {}
            value = func( *args, **kw )
        else:
            value = dv[1]
        self.value = list[ : index ] + [ value ] + list[ index: ]
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
        self.value  = (list[ :index - 1 ] + [ list[ index ],
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
        list_pane = self._list_pane
        layout = list_pane.layout()

        for control in list_pane.children():
            editor = getattr( control, '_editor', None )
            if editor is not None:
                editor.dispose()
                editor.control = None
            elif control is not layout:
                control.setParent( None )

        del control

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
    # default:
    single_row = False

    #-- Facet Definitions ------------------------------------------------------

    # Is the list editor is scrollable? This values overrides the default:
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

        self._zzz_inited = ( self.index < len( self.list ) )

    #-- Property Implementations -----------------------------------------------

    def _get_list ( self ):
        return getattr( self._zzz_object, self._zzz_name )

    #-- Facet Event Handlers ---------------------------------------------------

    def _value_set ( self, value ):
        if self._zzz_inited:
            self.list[ self.index ] = value

#-- EOF ------------------------------------------------------------------------