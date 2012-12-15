"""
Defines the TextFile class for editing and saving the contents of text files.
"""

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
   import basename

from facets.api                                                               \
   import File, Property, Code, Bool, Int, Str, List, Instance, Button, View, \
          HToolbar, UItem, CodeEditor, ThemedCheckboxEditor, HistoryEditor,   \
          property_depends_on, on_facet_set

from facets.core.facet_base \
    import read_file, write_file, save_file

from facets.ui.key_bindings \
    import KeyBindings, KeyBinding

from facets.ui.pyface.timer.api \
    import do_after

from facets.extra.api \
    import file_watch

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The list of valid characters that can appear in a symbol:
SymbolCharacters = ('abcdefghijklmnopqrstuvwxyz'
                    'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_')

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def identity ( value ):
    """ Returns *value* unchanged.
    """
    return value


def to_lower ( value ):
    """ Returns a case insensitive version of *value*.
    """
    return value.lower()

#-------------------------------------------------------------------------------
#  TextFile CodeEditor Keybindings:
#-------------------------------------------------------------------------------

TextFileBindings = KeyBindings( [
    KeyBinding( binding = 'Ctrl-Shift-Up',   method = 'move_line_up'   ),
    KeyBinding( binding = 'Ctrl-Shift-Down', method = 'move_line_down' ),
    KeyBinding( binding = 'Ctrl-Enter',      method = 'insert_line'    ),
    KeyBinding( binding = 'Ctrl-f',          method = 'find_selected'  ),
    KeyBinding( binding = 'Ctrl-n',          method = 'find_next'      ),
    KeyBinding( binding = 'Ctrl-p',          method = 'find_previous'  ),
    KeyBinding( binding = 'Ctrl-s',          method = 'save_file',
                alt_binding = 'F2'                                     ),
    KeyBinding( binding = 'Ctrl-Shift-s',    method = 'save_as_file'   ),
] )

#-------------------------------------------------------------------------------
#  'TextFile' class:
#-------------------------------------------------------------------------------

class TextFile ( Tool ):
    """ Defines a single text file editor.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Text' )

    # The name of the file being edited:
    file_name = File( connect = 'from' )

    # The short name of the file being edited:
    short_name = Property

    # The current text contents of the file:
    text = Code( connect = 'both' )

    # A list of additional View 'Item' objects that should be added to the
    # toolbar:
    toolbar_items = List # ( Item )

    # The optional key bindings associated with the text file editor:
    key_bindings = Instance( KeyBindings )

    # The currently selected text line:
    selected_line = Int

    # The currently selected text:
    selected_text = Str

    # The list of text lines in the file:
    text_lines = Property

    # The contents of the line the cursor is currently on:
    text_line = Property( connect = 'from' )

    # The text as it is saved to a file:
    file_text = Property

    # Have the contents of the file been modified since being saved or loaded?
    modified = Bool( False )

    # The current text search string:
    find = Str

    # Are 'find' searches case_sensitive?
    case_sensitive = Bool( False )

    # A callable for mapping a string to the correct case for use with 'find':
    find_case = Property

    # Event fired when the user wants to clear the 'find' string:
    clear_find = Button( '@icons2:Delete' )

    # Should we show (i.e. highlight) all 'find' matches in the file:
    show_find = Bool( False )

    # Go to the previous occurence of the current 'find' string:
    goto_previous = Button( '@icons2:ArrowLeft' )

    # Go to the next occurence of the current 'find' string:
    goto_next = Button( '@icons2:ArrowRight' )

    # The number of 'find' matches in the file:
    find_count = Property

    # The list of lines matching the current search string:
    find_matches = Property( List )

    # The current number of lines in the file:
    lines = Property

    # The current editor line:
    line = Int

    # The current editor column:
    column = Int

    # The current cursor location:
    location = Property

    # Event fired when the user wants to save the contents of the file:
    save = Button( '@icons2:Floppy' )

    # Status message for the editor:
    status = Str

    # Should auto-update ignore the next reload request?
    ignore_reload = Bool( False )

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        local_key_bindings = TextFileBindings.clone( controllers = [ self ] )
        key_bindings       = self.key_bindings
        if key_bindings is None:
            key_bindings = local_key_bindings
        else:
            key_bindings = key_bindings.clone(
                children = [ local_key_bindings ]
            )

        return  View(
            UItem( 'text',
                   editor = CodeEditor(
                       selected_line = 'selected_line',
                       selected_text = 'selected_text',
                       line          = 'line',
                       column        = 'column',
                       mark_lines    = 'find_matches',
                       key_bindings  = key_bindings
                   )
            ),
            HToolbar(
                *self._toolbar_items(),
                group_theme = '#themes:toolbar_group',
                id          = 'tb'
            ),
            id = 'facets.extra.tools.text_file.TextFile',
        )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'file_name' )
    def _get_short_name ( self ):
        return basename( self.file_name )


    @property_depends_on( 'text' )
    def _get_text_lines ( self ):
        return self.text.split( '\n' )


    @property_depends_on( 'text, line' )
    def _get_text_line ( self ):
        lines = self.text.split( '\n' )
        index = self.line - 1
        if 0 <= index < len( lines ):
            return lines[ index ]

        return ''


    def _get_file_text ( self ):
        return '\n'.join( [ line.rstrip() for line in self.text_lines ] )


    @property_depends_on( 'text_lines' )
    def _get_lines ( self ):
        return len( self.text_lines )


    @property_depends_on( 'line, column' )
    def _get_location ( self ):
        return ('%d:%d' % ( self.line, self.column ))


    @property_depends_on( 'case_sensitive' )
    def _get_find_case ( self ):
        if self.case_sensitive:
            return identity

        return to_lower


    @property_depends_on( 'find, text, find_case' )
    def _get_find_count ( self ):
        find = self.find
        if find == '':
            return ''

        count = col = 0
        n     = len( find )
        text  = self.find_case( self.text )
        find  = self.find_case( find )

        while True:
            col = text.find( find, col )
            if col < 0:
                break

            count += 1
            col   += n

        if count == 0:
            return 'No matches'

        if count == 1:
            return '1 match'

        return '%d matches' % count


    @property_depends_on( 'text, find, show_find, find_case' )
    def _get_find_matches ( self ):
        find = self.find
        if (find == '') or (not self.show_find):
            return []

        text_lines = self.text_lines
        find_case  = self.find_case
        find       = find_case( find )
        return [ (i + 1) for i in xrange( len( text_lines ) )
                         if find_case( text_lines[ i ] ).find( find ) >= 0 ]

    #-- Public Methods ---------------------------------------------------------

    def insert_line ( self ):
        """ Inserts a new, blank line below the current line.
        """
        line   = self.line - 1
        text   = self.text_lines[ line ]
        column = len( text ) - len( text.lstrip() )
        self.text_lines.insert( line + 1, ' ' * column )
        self.column = 1
        self.text   = '\n'.join( self.text_lines )
        self.line  += 1
        self.column = column + 1


    def move_line_up ( self ):
        """ Moves the current text line up one.
        """
        line = self.line - 1
        if line > 0:
            text_lines = self.text_lines
            text_lines.insert( line - 1, text_lines[ line ] )
            del text_lines[ line + 1 ]
            self.text = self.file_text
            self.line = line


    def move_line_down ( self ):
        """ Moves the current text line down one.
        """
        line       = self.line - 1
        text_lines = self.text_lines
        if line < (len( text_lines ) - 1):
            text_lines.insert( line + 2, text_lines[ line ] )
            del text_lines[ line ]
            self.text  = self.file_text
            self.line += 1


    def find_selected ( self ):
        """ Finds the next occurrence of the currently selected text.
        """
        self.find = self.selected_text or self._current_symbol()


    def find_next ( self, skip = False ):
        """ Finds the next occurence of the 'find' string in the file.
        """
        find = self.find
        if find == '':
            self.status = 'No search string specified'
        else:
            find_case    = self.find_case
            find         = find_case( find )
            line, column = self.line - 1, self.column - 1
            text_lines   = self.text_lines
            if (skip and
                (find_case( text_lines[ line ][ column: column + len( find ) ] )
                 == find)):
                column += len( find )

            end = len( text_lines )
            while line < end:
                column = find_case( text_lines[ line ] ).find( find, column )
                if column >= 0:
                    self.line, self.column = line + 1, column + 1
                    self.selected_line     = self.line
                    self.status            = ''

                    break

                column = 0
                line  += 1
            else:
                if skip:
                    self.status = 'No match found'


    def find_previous ( self ):
        """ Finds the previous occurence of the 'find' string in the file.
        """
        find = self.find
        if find == '':
            self.status = 'No search string specified'
        else:
            find_case    = self.find_case
            find         = find_case( find )
            line, column = self.line - 1, self.column - 1
            text_lines   = self.text_lines
            while line >= 0:
                text = text_lines[ line ]
                if column >= 0:
                    text = text[ : column ]

                column = find_case( text ).rfind( find )
                if column >= 0:
                    self.line, self.column = line + 1, column + 1
                    self.selected_line     = self.line
                    self.status            = ''

                    break

                line -= 1
            else:
                self.status = 'No match found'


    def save_file ( self ):
        """ Saves the text contents of the file to its assigned file name.
        """
        if self.file_name == '':
            self.save_as_file()
        else:
            self.ignore_reload = True
            if write_file( self.file_name, self.file_text ) is None:
                self.status        = 'Error occurred saving file'
                self.ignore_reload = False
            else:
                self.status   = 'File saved'
                self.modified = False


    def save_as_file ( self ):
        """ Saves the text contents of the file to a user specified file name.
        """
        try:
            self.ignore_reload = True
            file_name          = save_file( self.file_name, self.file_text )
            if file_name is not None:
                self.file_name = file_name
                self.status    = 'File saved'
                self.modified  = False

                return
        except:
            self.status = 'Error occurred saving file'

        self.ignore_reload = False


    def update ( self, file_name ):
        """ Refreshes the text file from disk if it has not been modified and is
            still the same file.
        """
        if file_name == self.file_name:
            if self.ignore_reload:
                self.ignore_reload = False
            elif not self.modified:
                self.text     = read_file( file_name )
                self.status   = 'File reloaded'
                self.modified = False
        else:
            file_watch.watch( self.update, file_name, remove = True )

    #-- Facet Event Handlers ---------------------------------------------------

    def _text_set ( self ):
        """ Handles the file 'text' being changed.
        """
        self.modified = True


    @on_facet_set( 'find, find_case' )
    def _find_modified ( self ):
        if self.find != '':
            self.find_next()


    def _clear_find_set ( self ):
        """ Handles the 'clear find' button being clicked.
        """
        self.find = ''


    def _goto_previous_set ( self ):
        """ Handles the 'go to previous' button being clicked.
        """
        self.find_previous()


    def _goto_next_set ( self ):
        """ Handles the 'go to next' button being clicked.
        """
        self.find_next( True )


    def _status_set ( self ):
        """ Handles the 'status' facet being changed.
        """
        if self.status != '':
            do_after( 5000, self.set, status = '' )


    def _save_set ( self ):
        """ Handles the 'save' button being clicked.
        """
        self.save_file()

    #-- Private Methods --------------------------------------------------------

    def _toolbar_items ( self ):
        """ Returns the list of Item objects to be displayed in the editor's
            toolbar.
        """
        items = [
            UItem( 'location',
                   style   = 'readonly',
                   width   = -50,
                   tooltip = 'Current cursor location' ),
            '_',
            UItem( 'show_find',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@icons2:Magnifier',
                       on_tooltip  = 'Highlight matches',
                       off_tooltip = 'Do not highlight matches' )
            ),
            UItem( 'case_sensitive',
                   padding = -2,
                   editor  = ThemedCheckboxEditor(
                       image       = '@icons:case_sensitive',
                       off_image   = '@icons:case_insensitive',
                       on_tooltip  = 'Use case sensitive matching',
                       off_tooltip = 'Use case insensitive matching' )
            ),
            UItem( 'goto_previous',
                   padding = -2,
                   tooltip = 'Find the previous occurence of the current '
                             'search string'
            ),
            UItem( 'goto_next',
                   padding = -2,
                   tooltip = 'Find the next occurence of the current search '
                             'string'
            ),
            UItem( 'clear_find',
                   padding = -2,
                   tooltip = 'Clear the current search string'
            ),
            UItem( 'find',
                   width   = -150,
                   tooltip = 'Enter a string to search for',
                   editor  = HistoryEditor( entries = 10 )
            ),
            UItem( 'find_count',
                   style = 'readonly',
                   width = -75
            ),
            '_',
            UItem( 'status',
                   style   = 'readonly',
                   springy = True
            ),
            '_'
        ]
        items.extend( self.toolbar_items )
        items.append(
            UItem( 'save',
                   padding      = -2,
                   tooltip      = 'Save the text to a file',
                   # fixme: Uncommenting this causes a hang when file is saved:
                   #enabled_when = 'modified'
            )
        )

        return items


    def _current_symbol ( self ):
        """ Returns the symbol at the current cursor location.
        """
        text   = self.text_line
        column = self.column - 1
        for start in xrange( column - 1, -1, -1 ):
            if text[ start ] not in SymbolCharacters:
                start += 1

                break
        else:
            start = 0

        for end in xrange( column, len( text ) ):
            if text[ end ] not in SymbolCharacters:
                break
        else:
            end = len( text )

        return text[ start: end ]

#-- EOF ------------------------------------------------------------------------
