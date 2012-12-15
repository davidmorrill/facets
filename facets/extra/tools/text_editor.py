"""
Defines the TextEditor tool for editing multiple text files.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
   import abspath

from facets.api \
   import File, Property, Bool, Str, List, Instance, View, VGroup, Item, UItem, \
          NotebookEditor, property_depends_on, on_facet_set

from facets.core.facet_base \
    import read_file

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.api \
    import file_watch

from facets.extra.helper.file_position \
    import FilePosition

from text_file \
    import TextFile

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'TextEditor' class:
#-------------------------------------------------------------------------------

class TextEditor ( Tool ):
    """ Defines the TextEditor tool for editing multiple text files.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Text Editor'

    # The name of the most recent file to edit:
    file_name = File( connect = 'to: file name' )

    # The file position of the most recent file to edit:
    file_position = Instance( FilePosition, connect = 'to: file position' )

    # The contents of the currently selected TextFile's current line:
    line = Property( Str, connect = 'from' )

    # Should unmodified files be automatically closed when a new file is opened?
    auto_close = Bool( True, save_state = True )

    # The list of active TextFile's:
    text_files = List # ( TextFile )

    # The currently selected TextFile:
    text_file = Instance( TextFile )

    #-- Facet View Definitions -------------------------------------------------

    facets_view = View(
        UItem( 'text_files',
               editor = NotebookEditor(
                   deletable = True,
                   export    = 'DockWindowShell',
                   page_name = '.short_name',
                   selected  = 'text_file' )
        )
    )


    options = View(
        VGroup(
            Item( 'auto_close',
                  tooltip = 'Should unmodified files be automatically\n'
                            'closed when a new file is opened?'
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'text_file:text_line' )
    def _get_line ( self ):
        if self.text_file is not None:
            return self.text_file.text_line

        return ''

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name ):
        """ Handles the 'file_name' facet being changed.
        """
        if file_name != '':
            file_name  = abspath( file_name )
            text_files = self.text_files
            if self.auto_close:
                for i in xrange( len( text_files ) - 1, -1, -1 ):
                    text_file = text_files[ i ]
                    if ((not text_file.modified) and
                        (file_name != text_file.file_name)):
                        del text_files[ i ]

            for text_file in text_files:
                if file_name == text_file.file_name:
                    break
            else:
                text_file = TextFile(
                    file_name = file_name,
                    text      = read_file( file_name ) or ''
                ).set(
                    modified  = False
                )
                text_files.append( text_file )
                self.text_file = text_file

            do_later( self.set, file_name = '' )


    def _file_position_set ( self, file_position ):
        """ Handles the 'file_position' facet being changed.
        """
        self.file_name               = file_position.file_name
        self.text_file.selected_line = file_position.line


    @on_facet_set( 'text_files[]' )
    def _text_files_modified ( self, removed, added ):
        for tf in removed:
            file_watch.watch( tf.update, tf.file_name, remove = True )

        for tf in added:
            file_watch.watch( tf.update, tf.file_name )

#-- EOF ------------------------------------------------------------------------
