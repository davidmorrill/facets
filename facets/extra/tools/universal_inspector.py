"""
Defines the universal data inspector tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import basename, splitext, isfile, dirname

from cPickle \
    import load

from cStringIO \
    import StringIO

from facets.api \
    import HasPrivateFacets, Instance, Any, Int, Str, Code, List, Range,   \
           Theme, Property, Image, SyncValue, View, HGroup, VGroup, UItem, \
           NotebookEditor, ValueEditor, CodeEditor, ImageZoomEditor,       \
           PresentationEditor, spring

from facets.core.facet_base \
    import read_file

from facets.lib.io.file \
    import File

from facets.ui.pyface.timer.api \
    import do_later

from facets.ui.pyface.i_image_resource \
    import AnImageResource

from facets.extra.features.api \
    import DragDropFeature

from facets.extra.helper.themes \
    import TTitle, Scrubber

from facets.extra.api \
    import HasPayload, FilePosition, file_watch

from facets.extra.markdown.markdown \
    import Markdown

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# All valid text characters:
text_characters = ('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
                   '0123456789`~!@#$%^&*()-_=+[]{}\\|\'";:,<.>/?\r\n\t ')

# Allowed extensions for image files:
ImageTypes = [ '.png', '.jpg', '.bmp', '.gif', '.ico' ]

#-------------------------------------------------------------------------------
#  'UniversalInspector' class:
#-------------------------------------------------------------------------------

class UniversalInspector ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Universal Inspector'

    # Maximum number of open inspectors allowed:
    max_inspectors = Range( 1, 50, 3, mode        = 'spinner',
                                      save_state  = True,
                                      facet_value = True )

    # The current item being inspected:
    item = Any( droppable = 'Drop a Python object or value here.',
                connect   = 'both: object to inspect' )

    # The most recently selected inspector sub-item:
    selected = Any( connect = 'from: selected item' )

    # Current list of items being inspected:
    inspectors = List

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        UItem( 'inspectors',
               editor = NotebookEditor(
                   deletable  = True,
                   page_name  = '.name',
                   export     = 'DockWindowShell',
                   dock_style = 'auto',
                   features   = [ DragDropFeature ]
               )
        )
    )


    options = View(
        HGroup(
            Scrubber( 'max_inspectors',
                label = 'Maximum number of open inspectors',
                width = 50
            ),
            spring,
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _max_inspectors_set ( self, max_inspectors ):
        """ Handles the 'max_inspectors' facet being changed.
        """
        delta = len( self.inspectors ) - max_inspectors
        if delta > 0:
            del self.inspectors[ : delta ]


    def _item_set ( self, item ):
        """ Handles the 'item' facet being changed.
        """
        # Check to see if it is a list of File objects, which represent files
        # dropped onto the view from an external source (like MS Explorer):
        if isinstance( item, list ) and (len( item ) > 0):
            for an_item in item:
                if not (isinstance( an_item, File ) or
                       (isinstance( an_item, basestring ) and
                        isfile( an_item ))):
                    break
            else:
                for an_item in item:
                    self._item_set( an_item )

                return

        # Set up the default values:
        name  = full_name = ''
        line  = 0
        lines = -1

        # Extract the file name from a File object:
        if isinstance( item, File ):
            item = item.absolute_path

        # Handle the case of an item which contains a payload:
        elif isinstance( item, HasPayload ):
            name      = item.payload_name
            full_name = item.payload_full_name
            item      = item.payload

        # Handle the case of a file position, which has a file name and a
        # possible starting line and range of lines:
        if isinstance( item, FilePosition ):
            name  = item.name
            line  = item.line
            lines = item.lines
            item  = item.file_name

        # Only create an inspector if there actually is a valid item:
        if item is not None:
            inspector = None

            # If it is an image, create an ImageInspector for it:
            if isinstance( item, AnImageResource ):
                inspector = ImageInspector( image = item )

            # If it is a theme, create a ThemeLayout tool to view it:
            elif isinstance( item, Theme ):
                from theme_layout import ThemeLayout

                inspector = ThemeLayout( theme = item )

            # If it is a string value, check to see if it is a valid file name:
            elif isinstance( item, basestring ) and isfile( item ):
                ext = splitext( item )[1].lower()
                if ext in ImageTypes:
                    inspector = ImageInspector( image = item )
                elif ext == '.md':
                    inspector = MarkdownInspector( file = item )
                elif ext == '.pres':
                    inspector = PresentationInspector( file = item )
                else:
                    data = read_file( item, 'r' )
                    if data is not None:
                        if name == '':
                            name      = basename( item )
                            full_name = item
                        try:
                            inspector = ObjectInspector(
                                object    = self._object_from_pickle( data ),
                                name      = name,
                                full_name = full_name,
                                owner     = self )
                        except:
                            try:
                                inspector = ObjectInspector(
                                    object    = self._object_from_pickle(
                                                    read_file( item ) ),
                                    name      = name,
                                    full_name = full_name,
                                    owner     = self
                                )
                            except:
                                inspector = FileInspector(
                                    name      = name,
                                    line      = line,
                                    lines     = lines ).set(
                                    file_name = item
                                )

            # If it is not a file, then it must just be a generic object:
            if inspector is None:
                inspector = ObjectInspector( object    = item,
                                             name      = name,
                                             full_name = full_name,
                                             owner     = self )

            inspectors = self.inspectors

            # Make sure the # of inspectors doesn't exceed the maximum allowed:
            if len( inspectors ) >= self.max_inspectors:
                del inspectors[0]

            # Add the new inspector to the list of inspectors (which will
            # cause it to appear as a new notebook page):
            inspectors.append( inspector )

            # Reset the current item to None, so we are ready for a new item:
            do_later( self.set, item = None )

    #-- Private Methods --------------------------------------------------------

    def _object_from_pickle ( self, data ):
        """ Tries the return the objects contained in a 'pickle' buffer.
        """
        buffer = StringIO( data )
        object = [ load( buffer ) ]
        try:
            while True:
                object.append( load( buffer ) )
        except:
            import traceback
            traceback.print_exc()

        if len( object ) == 1:
            object = object[0]

        return object

#-------------------------------------------------------------------------------
#  'ObjectInspector' class:
#-------------------------------------------------------------------------------

class ObjectInspector ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The UniversalInspector object that creating this inspector:
    owner = Instance( UniversalInspector )

    # The inspector page name:
    name = Property

    # The inspector's full object name:
    full_name = Property

    # The object being inspected:
    object = Any( draggable = 'Drag the object.' )

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            TTitle( 'full_name' ),
            UItem( 'object',
                   editor = ValueEditor( selected = 'object.owner.selected' )
            ),
            show_labels = False
        )
    )

    def _selected_set ( self, new ):
        print "new:", new

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        if self._name != '':
            return self._name

        return '%s [0x%08X]' % ( self.object.__class__.__name__,
                                 id( self.object ) )

    def _set_name ( self, name ):
        self._name = name


    def _get_full_name ( self ):
        if self._full_name != '':
            return self._full_name

        return '%s [0x%08X]' % ( self.object.__class__.__name__,
                                 id( self.object ) )

    def _set_full_name ( self, full_name ):
        self._full_name = full_name

#-------------------------------------------------------------------------------
#  'ImageInspector' class:
#-------------------------------------------------------------------------------

class ImageInspector ( HasPayload ):
    """ Allows viewing an image using the ImageZoomEditor.
    """

    #-- Facet Definitions ----------------------------------------------------------

    # The image to be displayed:
    image = Image

    # The name of the image:
    name = Property

    #-- Facets View Definitions-----------------------------------------------------

    view = View(
        VGroup(
            TTitle( 'object.image.name' ),
            UItem( 'image', editor = ImageZoomEditor( channel = 'red' ) ),
            show_labels = False
        )
    )

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        return basename( self.image.name )

#-------------------------------------------------------------------------------
#  'MarkdownInspector' class:
#-------------------------------------------------------------------------------

class MarkdownInspector ( HasPrivateFacets ):
    """ Allows viewing a markdown encoded file.
    """

    #-- Facet Definitions ----------------------------------------------------------

    # The name of the markdown file:
    name = Property

    # The markdown encoded text or file name to display:
    file = Markdown( draggable = 'Drag the file name.' )

    #-- Facets View Definitions-----------------------------------------------------

    view = View(
        TTitle( 'file' ),
        UItem(  'file' )
    )

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        return basename( self.file )

#-------------------------------------------------------------------------------
#  'PresentationInspector' class:
#-------------------------------------------------------------------------------

class PresentationInspector ( MarkdownInspector ):
    """ Allows viewing a Facets presentation file.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The current presentation:
    presentation = Str

    # The name of a file or directory to use as the presentation file base:
    file_base = Str

    #-- Facets View Definitions-----------------------------------------------------

    def default_facets_view ( self ):
        return View(
            TTitle( 'file' ),
            UItem(  'presentation',
                    editor = PresentationEditor(
                                file_base = SyncValue( self, 'file_base' ) )
            )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_set ( self, file ):
        self.presentation = read_file( file )
        self.file_base    = dirname( file )

#-------------------------------------------------------------------------------
#  'FileInspector' class:
#-------------------------------------------------------------------------------

class FileInspector ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The inspector page name:
    name = Property

    # The name of the file being inspected:
    file_name = Str( draggable = 'Drag the file name.' )

    # The starting line number:
    line = Int

    # The number of lines (start at 'line'):
    lines = Int( -1 )

    # The text being inspected:
    text = Code

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        VGroup(
            TTitle( 'file_name' ),
            UItem( 'text',
                   style  = 'readonly',
                   editor = CodeEditor( selected_line = 'line' )
            ),
            show_labels = False
        )
    )

    #-- Property Implementations -----------------------------------------------

    def _get_name ( self ):
        if self._name != '':
            return self._name

        return basename( self.file_name )

    def _set_name ( self, name ):
        self._name = name

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, old, new ):
        """ Handles the 'file_name' facet being changed.
        """
        if old != '':
            file_watch.watch( self._update, old, remove = True )

        if new != '':
            file_watch.watch( self._update, new )
            self._update( new )

    #-- Private Methods --------------------------------------------------------

    def _update ( self, file_name ):
        """ Updates the view with the contents of the specified file.
        """
        data = read_file( file_name )
        if data is not None:
            if self.is_text( data ):
                if self.lines > 0:
                    self.text = '\n'.join( data.split( '\n' )
                                [ max( 0, self.line - 1 ):
                                  self.line + self.lines - 1 ] )
                else:
                    self.text = data
            else:
                format    = self.format
                self.text = '\n'.join( [ format( i, data[ i: i + 16 ] )
                                       for i in range( 0, len( data ), 16 ) ] )


    def is_text ( self, buffer ):
        """ Returns whether a specified buffer contains only valid text
            characters.
        """
        for i in range( min( 256, len( buffer ) ) ):
            if not buffer[i] in text_characters:
                return False

        return True


    def format ( self, offset, data ):
        """ Formats a binary string of data as a hex encoded string.
        """
        hb = [ self.hex_bytes( data[ i: i + 4 ] ) for i in range( 0, 16, 4 ) ]
        return ('#%08X  %s %s %s %s  |%s|' % (
                offset, hb[0], hb[1], hb[2], hb[3], self.ascii_bytes( data ) ))


    def hex_bytes ( self, data ):
        return ''.join( [ self.hex_byte( data[ i: i + 1 ] )
                        for i in range( 0, 4 ) ] )


    def hex_byte ( self, byte ):
        """ Returns the hex encoding of a 0 or 1 length string of data.
        """
        if len( byte ) == 0:
            return '  '

        return ( '%02X' % ord( byte ) )


    def ascii_bytes ( self, data ):
        return ''.join( [ self.ascii_byte( data[ i: i + 1 ] )
                        for i in range( 0, 16 ) ] )


    def ascii_byte ( self, byte ):
        """ Returns the hex encoding of a 0 or 1 length string of data.
        """
        if len( byte ) == 0:
            return ' '

        n = ord( byte )
        if 32 <= n <= 127:
            return byte

        return '.'

#-- EOF ------------------------------------------------------------------------