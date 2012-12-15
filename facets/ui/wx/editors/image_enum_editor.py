"""
Defines the various image enumeration editors and the image enumeration
    editor factory for the wxPython user interface toolkit.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys
import wx

from os \
    import getcwd

from os.path \
    import join, dirname, exists

from facets.api \
    import Str, Type, List, Module, Any, Instance, on_facet_set, Editor

from enum_editor \
    import EnumEditor

from facets.ui.wx.helper \
    import position_window, FacetsUIPanel

from facets.ui.wx.constants \
    import WindowColor

from facets.ui.controls.image_control \
    import ImageControl

from editor \
    import Editor as WxEditor

#-------------------------------------------------------------------------------
#  'ImageEnumEditor' class:
#-------------------------------------------------------------------------------

class ImageEnumEditor ( EnumEditor ):
    """ wxPython editor factory for image enumeration editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Prefix to add to values to form image names:
    prefix = Str

    # Suffix to add to values to form image names:
    suffix = Str

    # Path to use to locate image files:
    path = Str

    # Class used to derive the path to the image files:
    klass = Type

    # Module used to derive the path to the image files:
    module = Module

    #-- Public Methods ---------------------------------------------------------

    def init ( self ):
        """ Performs any initialization needed after all constructor facets
            have been set.
        """
        super( ImageEnumEditor, self ).init()

        self._update_path()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'path, klass, module' )
    def _update_path ( self ):
        """ Handles one of the items defining the path being updated.
        """
        if self.path != '':
            self._image_path = self.path
        elif self.klass is not None:
            module = self.klass.__module__
            if module == '___main___':
                module = '__main__'
            try:
                self._image_path = join( dirname( sys.modules[ module
                                                        ].__file__ ), 'images' )
            except:
                self._image_path = self.path
                dirs = [ join( dirname( sys.argv[ 0 ] ), 'images' ),
                         join( getcwd(), 'images' ) ]
                for d in dirs:
                    if exists( d ):
                        self._image_path = d
                        break
        elif self.module is not None:
            self._image_path = join( dirname( self.module.__file__ ), 'images' )

    #-- 'Editor' Factory Methods -----------------------------------------------

    def simple_editor ( self, ui, object, name, description ):
        return SimpleEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

    def custom_editor ( self, ui, object, name, description ):
        return CustomEditor( factory     = self,
                             ui          = ui,
                             object      = object,
                             name        = name,
                             description = description )

    def readonly_editor ( self, ui, object, name, description ):
        return ReadonlyEditor( factory     = self,
                               ui          = ui,
                               object      = object,
                               name        = name,
                               description = description )

#-------------------------------------------------------------------------------
#  'ReadonlyEditor' class:
#-------------------------------------------------------------------------------

class ReadonlyEditor ( Editor ):
    """ Read-only style of image enumeration editor, which displays a single
        ImageControl, representing the object facet's value.
    """

    #-- Facet Definitions ------------------------------------------------------

    image_control = Instance( ImageControl )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.image_control = ic = ImageControl()
        self.update_editor()
        self.adapter = ic.create_control( parent )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        self.image_control.image = '%s%s%s' % ( self.factory.prefix,
                                   self.str_value, self.factory.suffix )

#-------------------------------------------------------------------------------
#  'SimpleEditor' class:
#-------------------------------------------------------------------------------

class SimpleEditor ( ReadonlyEditor ):
    """ Simple style of image enumeration editor, which displays an
        ImageControl, representing the object facet's value. Clicking an image
        displays a dialog box for selecting an image corresponding to a
        different value.
    """

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        super( SimpleEditor, self ).init( parent )

        self.image_control.set(
            selectable = True,
            selected   = True
        )
        self.set_tooltip()


    @on_facet_set( 'image_control:clicked' )
    def popup_editor ( self ):
        """ Handles the user clicking the ImageControl to display the pop-up
            dialog.
        """
        ImageEnumDialog( self )

#-------------------------------------------------------------------------------
#  'CustomEditor' class:
#-------------------------------------------------------------------------------

class CustomEditor ( WxEditor ):
    """ Custom style of image enumeration editor, which displays a grid of
        ImageControls. The user can click an image to select the corresponding
        value.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Callback to call when any button clicked:
    update_handler = Any

    # The list of ImageControl used to populate the grid:
    image_controls = List( ImageControl )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self._create_image_grid( parent )


    def update_object ( self, image_control, old, new ):
        """ Handles the user clicking on an ImageControl to set an object value.
        """
        self.value = image_control._value
        if self.update_handler is not None:
            self.update_handler()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        value = self.value
        for image_control in self.image_controls:
            image_control.selected = (value == image_control._value)


    def dispose ( self ):
        """ Disposes of the editor.
        """
        del self.image_controls[:]

    #-- Private Methods --------------------------------------------------------

    def _create_image_grid ( self, parent ):
        """ Populates a specified window with a grid of image buttons.
        """
        # Create the panel to hold the ImageControl buttons:
        self.control = panel = FacetsUIPanel( parent, -1 )

        # Create the main sizer:
        if self.factory.cols > 1:
           sizer = wx.GridSizer( 0, self.factory.cols, 0, 0 )
        else:
           sizer = wx.BoxSizer( wx.VERTICAL )

        # Add the set of all possible choices:
        factory   = self.factory
        mapping   = factory._mapping
        ics       = self.image_controls
        cur_value = self.value
        for name in self.factory._names:
            value   = mapping[ name ]
            ic      = ImageControl( image = '%s%s%s' % ( factory.prefix, name,
                                                         factory.suffix ),
                                    selectable = True,
                                    selected   = (value == cur_value) )
            ic.on_facet_set( self.update_object, 'clicked', dispatch = 'ui' )
            ic._value = value
            control   = ic.create_control( panel )()
            sizer.Add( control, 0, wx.ALL, 2 )
            self.set_tooltip( control )
            ics.append( ic )

        # Finish setting up the control layout:
        panel.SetSizerAndFit( sizer )

#-------------------------------------------------------------------------------
#  'ImageEnumDialog' class:
#-------------------------------------------------------------------------------

class ImageEnumDialog ( wx.Frame ):
    """ Dialog box for selecting an ImageControl
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, editor ):
        """ Initializes the object.
        """
        wx.Frame.__init__( self, editor.control, -1, '',
                           style = wx.SIMPLE_BORDER )
        self.SetBackgroundColour( WindowColor )
        wx.EVT_ACTIVATE( self, self._on_close_dialog )
        self._closed = False

        dlg_editor = CustomEditor( factory        = editor.factory,
                                   ui             = editor.ui,
                                   object         = editor.object,
                                   name           = editor.name,
                                   description    = editor.description,
                                   update_handler = self._close_dialog )
        dlg_editor.init( self )

        # Wrap the dialog around the image button panel:
        sizer = wx.BoxSizer( wx.VERTICAL )
        sizer.Add( dlg_editor.control )
        sizer.Fit( self )

        # Position the dialog:
        position_window( self, parent = editor.control )
        self.Show()

    #-- wxPython Event Handlers ------------------------------------------------

    def _on_close_dialog ( self, event ):
        """ Closes the dialog.
        """
        if not event.GetActive():
            self._close_dialog()

    #-- Event Handlers ---------------------------------------------------------

    def _close_dialog ( self ):
        """ Closes the dialog.
        """
        if not self._closed:
            self._closed = True
            self.Destroy()

#-- EOF ------------------------------------------------------------------------