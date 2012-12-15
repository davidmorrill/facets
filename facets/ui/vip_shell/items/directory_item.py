"""
Defines the DirectoryItem class used by the VIP Shell to represent a file system
directory.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os \
    import listdir

from os.path \
    import join, isdir

from facets.ui.graphics_text \
    import color_tag_for

from facets.ui.menu \
    import Action

from facets.ui.vip_shell.helper \
    import file_info_for

from facets.ui.vip_shell.tags.api \
    import FileTag

from path_item \
    import PathItem

#-------------------------------------------------------------------------------
#  'DirectoryItem' class:
#-------------------------------------------------------------------------------

class DirectoryItem ( PathItem ):
    """ A directory.
    """

    #-- Facet Definitions ------------------------------------------------------

    type       = 'file'
    icon       = '@facets:shell_directory'
    color_code = '\x005'

    # The custom tool bar actions supported by the item (if any):
    actions = [
        Action( image   = '@icons2:WindowHorizontal?H84',
                tooltip = 'List Python source files in the directory',
                action  = 'item.list_source_files()' ),
    ]

    #-- Public Methods ---------------------------------------------------------

    def click ( self, event ):
        """ Handles the user clicking an item without the shift or alt
            modifiers.
        """
        if event.control_down:
            self.shell.append( self.item )
        else:
            self.shell.append( self.item_contents )


    def can_execute ( self ):
        """ Returns True if the item can be 'executed' in some meaningful
            fashion, and False if it cannot.
        """
        return True


    def execute ( self ):
        """ Executes the directory by listing its contents.
        """
        self.shell.do_command( '/ls ' + self.item, self )


    def key_l ( self, event ):
        """ Lists the Python source files in the directory.

            The [[l]] key creates a list of Python source file shell items for
            all Python source files found in the directory.
        """
        self.list_source_files()


    def list_source_files ( self ):
        """ Lists the Python source files in the directory.
        """
        self.shell.do_command( '/l ' + self.item, self )

    #-- Facet Default Values ---------------------------------------------------

    def _item_label_default ( self ):
        return file_info_for( self.item )


    def _item_contents_default ( self ):
        files       = []
        directories = []
        tags        = self.tags
        path        = self.item
        cc2         = color_tag_for( '5' )
        for name in listdir( path ):
            file_name = join( path, name )
            if isdir( file_name ):
                directories.append(
                    file_info_for( file_name, color_tag_for( 'B', tags ), cc2 )
                )
            else:
                files.append(
                    file_info_for( file_name, color_tag_for( 'C', tags ), cc2 )
                )

            tags.append( FileTag( file = file_name ) )

        return '\n'.join( directories + files )

#-- EOF ------------------------------------------------------------------------
