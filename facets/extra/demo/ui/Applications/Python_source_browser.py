"""
This demo shows a combination of the <b>DirectoryEditor</b>, the
<b>GridEditor</b> and the <b>CodeEditor</b> used to create a simple Python
source browser:

 - Use the <b>DirectoryEditor</b> on the left to navigate to and select
   directories containing Python source files.
 - Use the <b>GridEditor</b> on the top-right to view information about and
   to select Python source files in the currently selected directory.
 - View the currently selected Python source file's contents in the
   <b>CodeEditor</b> in the bottom-right.

As an extra <i>feature</i>, the <b>Grid</b> also displays a:

 - Red ball if the file size > 64KB.
 - Blue ball if the file size > 16KB.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

import facets.core
import facets.ui

from time \
    import localtime, strftime

from os \
    import listdir

from os.path \
    import getsize, getmtime, isfile, join, splitext, basename, dirname

from facets.api \
    import HasPrivateFacets, Str, Float, List, Directory, File, Code, Bool, \
           Instance, Property, cached_property, View, Item, HSplit, VSplit, \
           GridEditor

from facets.ui.grid_adapter \
    import GridAdapter

#-- FileInfo Class Definition --------------------------------------------------

class FileInfo ( HasPrivateFacets ):

    file_name = File
    name      = Property
    size      = Property
    time      = Property
    date      = Property

    @cached_property
    def _get_name ( self ):
        return basename( self.file_name )

    @cached_property
    def _get_size ( self ):
        return getsize( self.file_name )

    @cached_property
    def _get_time ( self ):
        return strftime( '%I:%M:%S %p',
                         localtime( getmtime( self.file_name ) ) )

    @cached_property
    def _get_date ( self ):
        return strftime( '%m/%d/%Y',
                         localtime( getmtime( self.file_name ) ) )

#-- Grid Adapter Definition ----------------------------------------------------

class FileInfoAdapter ( GridAdapter ):

    columns = [ ( 'File Name', 'name' ),
                ( 'Size',      'size' ),
                ( '',          'big'  ),
                ( 'Date',      'date' ),
                ( 'Time',      'time' ) ]

    even_bg_color  = ( 244, 250, 255 )
    font           = '(Courier New, Courier) 9'
    size_alignment = Str( 'right' )
    time_alignment = Str( 'right' )
    date_alignment = Str( 'right' )
    big_text       = Str
    big_width      = Float( 20 )
    big_image      = Property
    big_sortable   = Bool( False )

    def _get_big_image ( self ):
        size = self.item.size
        if size > 65536:
            return '@icons:red_ball_l'

        return ( None, '@icons:blue_ball_l' )[ size > 16384 ]

#-- Grid Editor Definition --------------------------------------------------

grid_editor = GridEditor(
    adapter    = FileInfoAdapter,
    operations = [ 'sort', 'shuffle' ],
    selected   = 'file_info'
)

#-- PythonBrowser Class Definition ---------------------------------------------

class PythonBrowser ( HasPrivateFacets ):

    #-- Facet Definitions ------------------------------------------------------

    dir       = Directory
    files     = List( FileInfo )
    file_info = Instance( FileInfo )
    code      = Code

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        HSplit(
            Item( 'dir', style = 'custom' ),
            VSplit(
                Item( 'files', id = 'files', editor = grid_editor ),
                Item( 'code',  style = 'readonly' ),
                show_labels = False ),
            show_labels = False,
            id          = 'splitter'
        ),
        title     = 'Python Source browser Demo',
        id        = 'facets.extra.demo.ui.Applications.Python_source_browser',
        resizable = True,
        width     = 0.75,
        height    = 0.75
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _dir_set ( self, dir ):
        self.files = [ FileInfo( file_name = join( dir, name ) )
                       for name in listdir( dir )
                       if ((splitext( name )[ 1 ] == '.py') and
                           isfile( join( dir, name ) )) ]

    def _file_info_set ( self, file_info ):
        fh = None
        try:
            fh = open( file_info.file_name, 'rb' )
            self.code = fh.read()
        except:
            pass

        if fh is not None:
            fh.close()

#-- Create the demo ------------------------------------------------------------

demo = PythonBrowser( dir = dirname( facets.core_api.__file__ ) )

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo.edit_facets()

#-- EOF ------------------------------------------------------------------------