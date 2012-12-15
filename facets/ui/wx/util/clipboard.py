"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx

from cStringIO \
    import StringIO

from cPickle \
    import dumps, load, loads

from facets.core_api \
    import HasStrictFacets, Property

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Data formats:
PythonObjectFormat = wx.CustomDataFormat( 'PythonObject' )
TextFormat         = wx.DataFormat( wx.DF_TEXT )
FileFormat         = wx.DataFormat( wx.DF_FILENAME )

# Shortcuts:
cb           = wx.TheClipboard
is_supported = cb.IsSupported

# Standard sequence types:
SequenceTypes = ( list, tuple )

#-------------------------------------------------------------------------------
#  'Clipboard' class:
#-------------------------------------------------------------------------------

class Clipboard ( HasStrictFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The type of data in the clipboard (string):
    data_type = Property

    # Arbitrary Python data:
    data = Property

    # Arbitrary Python data is available:
    has_data = Property

    # Name of the class of object in the clipboard:
    object_type = Property

    # Python object data:
    object_data = Property

    # Python object data is available:
    has_object_data = Property

    # Text data:
    text_data = Property

    # Text data is available:
    has_text_data = Property

    # File name data:
    file_data = Property

    # File name data is available:
    has_file_data = Property

    #-- Property Implementations -----------------------------------------------

    def _get_data ( self ):
        if self.has_text_data:
            return self.text_data

        if self.has_file_data:
            return self.file_data

        if self.has_object_data:
            return self.object_data

        return None

    def _set_data ( self, data ):
        if isinstance( data, basestring ):
            self.text_data = data
        elif type( data ) in SequenceTypes:
            self.file_data = data
        else:
            self.object_data = data


    def _get_has_data ( self ):
        result = False
        if cb.Open():
            result = (is_supported( TextFormat ) or
                      is_supported( FileFormat ) or
                      is_supported( PythonObjectFormat ))
            cb.Close()

        return result


    def _get_data_type ( self ):
        if self.has_text_data:
            return 'str'

        if self.has_file_data:
            return 'file'

        if self.has_object_data:
            return self.object_type

        return ''


    def _get_object_data ( self ):
        result = None
        if cb.Open():
            try:
                if is_supported( PythonObjectFormat ):
                    cdo = wx.CustomDataObject( PythonObjectFormat )
                    if cb.GetData( cdo ):
                        file   = StringIO( cdo.GetData() )
                        klass  = load( file )
                        result = load( file )
            finally:
                cb.Close()

        return result

    def _set_object_data ( self, data ):
        if cb.Open():
            try:
                cdo = wx.CustomDataObject( PythonObjectFormat )
                cdo.SetData( dumps( data.__class__ ) + dumps( data ) )
                # fixme: There seem to be cases where the '-1' value creates
                # pickles that can't be unpickled (e.g. some FacetDictObject's)
                # cdo.SetData( dumps( data, -1 ) )
                cb.SetData( cdo )
            finally:
                cb.Close()
                cb.Flush()


    def _get_has_object_data ( self ):
        return self._has_this_data( PythonObjectFormat )


    def _get_object_type ( self ):
        result = ''
        if cb.Open():
            try:
                if is_supported( PythonObjectFormat ):
                    cdo = wx.CustomDataObject( PythonObjectFormat )
                    if cb.GetData( cdo ):
                        try:
                            # We may not be able to load the required class:
                            result = loads( cdo.GetData() )
                        except:
                            pass
            finally:
                cb.Close()

        return result


    def _get_text_data ( self ):
        result = ''
        if cb.Open():
            if is_supported( TextFormat ):
                tdo = wx.TextDataObject()
                if cb.GetData( tdo ):
                    result = tdo.GetText()
            cb.Close()

        return result

    def _set_text_data ( self, data ):
        if cb.Open():
            cb.SetData( wx.TextDataObject( str( data ) ) )
            cb.Close()
            cb.Flush()


    def _get_has_text_data ( self ):
        return self._has_this_data( TextFormat )


    def _get_file_data ( self ):
        result = []
        if cb.Open():
            if is_supported( FileFormat ):
                tfo = wx.FileDataObject()
                if cb.GetData( tfo ):
                    result = tfo.GetFilenames()
            cb.Close()

        return result

    def _set__file_data ( self, data ):
        if cb.Open():
            tfo = wx.FileDataObject()
            if isinstance( data, basestring ):
                tfo.AddFile( data )
            else:
                for filename in data:
                    tfo.AddFile( filename )
            cb.SetData( tfo )
            cb.Close()
            cb.Flush()


    def _get_has_file_data ( self ):
        return self._has_this_data( FileFormat )

    #-- Private Methods --------------------------------------------------------

    def _has_this_data ( self, format ):
        result = False
        if cb.Open():
            result = is_supported( format )
            cb.Close()

        return result

#-- Create a singleton instance for quick reference ----------------------------

clipboard = Clipboard()

#-- EOF ------------------------------------------------------------------------