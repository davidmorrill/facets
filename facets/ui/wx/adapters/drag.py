"""
Defines the wxPython specific WxDrag class that provides a concrete
implementation of the Drag base class.

The WxDrag class adapts a GUI toolkit drag and drop related event to provide a
set of toolkit neutral properties and methods.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from cPickle \
    import dumps, loads, HIGHEST_PROTOCOL

from facets.core_api \
    import Any, Int

from facets.ui.adapters.drag \
    import Drag

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from wxPython drop actions to a GUI toolkit neutral version:
RequestAction = {
    wx.DragError:  'ignore',
    wx.DragNone:   'ignore',
    wx.DragCopy:   'copy',
    wx.DragMove:   'move',
    wx.DragLink:   'link',
    wx.DragCancel: 'ignore'
}

# Mapping from GUI toolkit neutral drop actions to the Qt version:
ResultAction = {
    'copy': wx.Drag_CopyOnly,
    'move': wx.Drag_DefaultMove,
    'link': wx.Drag_AllowMove
}

# Mapping from GUI toolkit neutral drag result to wxPython drag result:
DragResult = {
    'copy':   wx.DragCopy,
    'move':   wx.DragMove,
    'link':   wx.DragLink,
    'ignore': wx.DragNone
}

#-------------------------------------------------------------------------------
#  Global Data:
#-------------------------------------------------------------------------------

# The current Python object being dragged:
drag_object = None

# The data formats used for pickled and unpickled Python objects:
PickledPythonObject   = wx.CustomDataFormat( 'PickledPythonObject' )
UnpickledPythonObject = wx.CustomDataFormat( 'UnpickledPythonObject' )

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def python_data_object ( object ):
    """ Returns a wxPython custom data object used to represent a Python object.
        If *data* can be pickled, a pickled Python object is returned; otherwise
        an unpickled Python object is returned
    """
    global drag_object

    try:
        pickle = dumps( object, HIGHEST_PROTOCOL )
        result = wx.CustomDataObject( PickledPythonObject )
        result.SetData( pickle )
    except:
        drag_object = object
        result      = wx.CustomDataObject( UnpickledPythonObject )
        result.SetData( 'dummy' )

    return result

#-------------------------------------------------------------------------------
#  'WxDrag' class:
#-------------------------------------------------------------------------------

class WxDrag ( Drag ):

    #-- Public Facet Definitions -----------------------------------------------

    # The result of the adapted drag event:
    drag_result = Int( wx.DragNone )

    # The wx DropTarget object this adapter is accoiated with:
    drop_target = Any

    #-- Property Implementations -----------------------------------------------

    def _get_x ( self ):
        return self.event[0]


    def _get_y ( self ):
        return self.event[1]


    def _get_request ( self ):
        return RequestAction.get( self.drag_result, wx.DragCopy )


    def _get_result ( self ):
        return RequestAction[ self.drag_result ]

    def _set_result ( self, result ):
        self.drag_result = DragResult.get( result, wx.DragNone )


    def _get_has_color ( self ):
        return False


    def _get_has_image ( self ):
        try:
            return (self.drop_target.image_object.GetBitmap() is not None)
        except:
            import traceback       ### TEMPORARY ###
            traceback.print_exc()  ### TEMPORARY ###

            return False


    def _get_has_text ( self ):
        try:
            return (self.drop_target.text_object.GetTextLength() > 0)
        except:
            import traceback       ### TEMPORARY ###
            traceback.print_exc()  ### TEMPORARY ###

            return False


    def _get_has_html ( self ):
        return False


    def _get_has_files ( self ):
        try:
            return (len( self.drop_target.file_object.GetFileNames() ) > 0)
        except:
            import traceback       ### TEMPORARY ###
            traceback.print_exc()  ### TEMPORARY ###

            return False


    def _get_has_urls ( self ):
        return False


    def _get_has_object ( self ):
        global drag_object

        return (drag_object is not None)


    def _get_color ( self ):
        return wx.WHITE


    def _get_image ( self ):
        try:
            return self.drop_target.image_object.GetBitmap()
        except:
            import traceback       ### TEMPORARY ###
            traceback.print_exc()  ### TEMPORARY ###

            return None


    def _get_text ( self ):
        try:
            return self.drop_target.text_object.GetText
        except:
            import traceback       ### TEMPORARY ###
            traceback.print_exc()  ### TEMPORARY ###

            return ''


    def _get_html ( self ):
        return ''


    def _get_files ( self ):
        try:
            return [ file
                     for file in self.drop_target.file_object.GetFileNames() ]
        except:
            import traceback       ### TEMPORARY ###
            traceback.print_exc()  ### TEMPORARY ###

            return []


    def _get_urls ( self ):
        return []


    def _get_object ( self ):
        # Try to return a Python object from a pickled representation:
        try:
            data = self.drop_target.pickled_object.GetData()
            if len( data ) > 0:
                return loads( data )
        except:
            import traceback       ### TEMPORARY ###
            traceback.print_exc()  ### TEMPORARY ###

        # Try to return an unpickled object using the global python object:
        try:
            data = self.drop_target.unpickled_object.GetData()
            if len( data ) > 0:
                global drag_object

                return drag_object
        except:
            import traceback       ### TEMPORARY ###
            traceback.print_exc()  ### TEMPORARY ###

        # Try to get an object from an of the other supported formats:
        result = self._get_image()
        if result is None:
            result = self._get_files()
            if len( result ) == 0:
                result = self._get_text()

        # Return the final result we arrived at:
        return result

#-------------------------------------------------------------------------------
#  'WxDropTarget' class:
#-------------------------------------------------------------------------------

class WxDropTarget ( wx.DropTarget ):
    """ Custom DropTarget class for use with WxDrag.
    """

    #-- DropTarget Method Overrides --------------------------------------------

    def __init__ ( self ):
        self.pickled_object   = wx.CustomDataObject( PickledPythonObject )
        self.unpickled_object = wx.CustomDataObject( UnpickledPythonObject )
        self.text_object      = wx.TextDataObject()
        self.file_object      = wx.FileDataObject()
        self.bitmap_object    = wx.BitmapDataObject()

        self.data_object      = data_object = wx.DataObjectComposite()
        data_object.Add( self.pickled_object, preferred = True )
        data_object.Add( self.unpickled_object )
        data_object.Add( self.text_object )
        data_object.Add( self.file_object )
        data_object.Add( self.bitmap_object )

        super( WxDropTarget, self ).__init__( data_object )


    def OnEnter ( self, x, y, drag_result ):
        adapter = self._adapter_for( 'enter', x, y, drag_result )
        if adapter is not None:
            return adapter.drag_result

        return super( WxDropTarget, self ).OnEnter( x, y, drag_result )


    def OnLeave ( self ):
        adapter = self._adapter_for( 'leave' )
        if adapter is None:
            super( WxDropTarget, self ).OnLeave()


    def OnDragOver ( self, x, y, drag_result ):
        adapter = self._adapter_for( 'move', x, y, drag_result )
        if adapter is not None:
            return adapter.drag_result

        return super( WxDropTarget, self ).OnDragOver( x, y, drag_result )


    def OnData ( self, x, y, drag_result ):
        self.GetData()
        adapter = self._adapter_for( 'drop', x, y, drag_result )
        if adapter is not None:
            return adapter.drag_result

        return super( WxDropTarget, self ).OnData( x, y, drag_result )


    def OnDrop ( self, x, y ):
        return True

    #-- Private Methods --------------------------------------------------------

    def _adapter_for ( self, name, x = 0, y = 0, drag_result = wx.DragNone ):
        """ Attempts to find and call the handler for a specified drag event
            name, using a WxDrag created using the specified x, y and
            drag_result values. Returns the WxDrag passed to the handler if a
            handler exists and was called, and None otherwise.
        """
        handler = getattr( self, '_drag_' + name, None )
        if handler is None:
            return None

        adapter = WxDrag( ( x, y ), drag_result = drag_result,
                                    drop_target = self )
        handler( adapter )

        return adapter

#-- EOF ------------------------------------------------------------------------
