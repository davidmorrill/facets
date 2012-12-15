"""
Defines the SyntaxChecker tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from exceptions \
    import SyntaxError

from os.path \
    import exists

from facets.api \
    import File, Int, Str, Bool, false, Button, View, VGroup, HGroup, Item, \
           CodeEditor

from facets.core.facet_base \
    import read_file

from facets.ui.pyface.timer.api \
    import do_after

from facets.extra.features.api \
    import DropFile

from facets.extra.api \
    import Saveable, file_watch

from facets.extra.helper.themes \
    import TTitle

#-------------------------------------------------------------------------------
#  'SyntaxChecker' class:
#-------------------------------------------------------------------------------

class SyntaxChecker ( Saveable ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Syntax Checker' )

    # The persistence id for this object:
    id = Str( 'facets.extra.tools.syntax_checker.state',
              save_state_id = True )

    # Should the syntax checker automatically go to the current syntax error?
    auto_goto = Bool( False, save_state = True )

    # Should a changed file be automatically reloaded:
    auto_load = Bool( True, save_state = True )

    # The name of the file currently being syntax checked:
    file_name = File( drop_file = DropFile( extensions = [ '.py' ],
                                    draggable = True,
                                    tooltip   = 'Drop a Python source file to '
                                          'syntax check it.\nDrag this file.' ),
                      connect   = 'to' )

    # The current source code being syntax checked:
    source = Str

    # The current syntax error message:
    error = Str

    # Current error line:
    error_line = Int

    # Current error column:
    error_column = Int

    # Current editor line:
    line = Int

    # Current editor column:
    column = Int

    # 'Go to' button:
    go_to = Button( 'Go To' )

    # Can the current file be saved?
    can_save = false

    #-- Facets View Definitions ------------------------------------------------

    facets_view = View(
        VGroup(
            TTitle( 'file_name' ),
            Item( 'source@',
                  editor = CodeEditor( selected_line = 'line' )
            ),
            HGroup(
                TTitle( 'error', springy = True ),
                Item( 'go_to',
                      show_label   = False,
                      enabled_when = '(error_line > 0) and (not auto_goto)'
                ),
            ),
            show_labels = False
        ),
        title = 'Syntax Checker'
    )

    options = View(
        VGroup(
            Item( 'auto_goto',
                  label = 'Automatically move cursor to syntax error'
            ),
            Item( 'auto_load',
                  label = 'Automatically reload externally changed files'
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Public Methods ---------------------------------------------------------

    def save ( self ):
        """ Saves the current source back to the associated file.
        """
        fh = None
        try:
            fh = file( self.file_name, 'wb' )
            fh.write( self.source )
            fh.close()
            self.needs_save = False
        except:
            if fh is not None:
                try:
                    fh.close()
                except:
                    pass

    #-- Facet Event Handlers ---------------------------------------------------

    def _auto_goto_set ( self, auto_goto ):
        """ Handles the 'auto_goto' facet being changed.
        """
        if auto_goto and (self.error_line > 0):
            self._go_to_set()


    def _go_to_set ( self ):
        """ Handles the 'Go To' button being clicked.
        """
        self.line   = self.error_line
        self.column = self.error_column


    def _file_name_set ( self, old, new ):
        """ Handles the 'file_name' facet being changed.
        """
        self._set_listener( old, True )
        self._set_listener( new, False )
        self._load_file_name( new )


    def _source_set ( self, source ):
        """ Handles the 'source' facet being changed.
        """
        if self.can_save:
            if not self._dont_update:
                self.needs_save = True
                do_after( 750, self._syntax_check )
            else:
                self._syntax_check()


    def _file_set ( self, file_name ):
        """ Handles the current file being updated.
        """
        if self.auto_load:
            self._load_file_name( file_name )

    #-- Private Methods --------------------------------------------------------

    def _set_listener ( self, file_name, remove ):
        """ Sets up/Removes a file watch on a specified file.
        """
        if exists( file_name ):
            file_watch.watch( self._file_set, file_name, remove = remove )


    def _load_file_name ( self, file_name ):
        """ Loads a specified source file.
        """
        self._dont_update = True
        self.can_save     = True
        source            = read_file( file_name )
        if source is None:
            self.error    = 'Error reading file'
            self.can_save = False
            source        = ''

        self.source       = source
        self._dont_update = False
        self.needs_save   = False


    def _syntax_check ( self ):
        """ Checks the current source for syntax errors.
        """
        try:
            compile( self.source.replace( '\r\n', '\n' ),
                     self.file_name, 'exec' )
            self.error      = 'Syntactically correct'
            self.error_line = 0
        except SyntaxError, excp:
            self.error_line   = excp.lineno
            self.error_column = excp.offset + 1
            self.error        = '%s on line %d, column %d' % (
                                excp.msg, excp.lineno, self.error_column )
            if self.auto_goto:
                self._go_to_set()

#-- EOF ------------------------------------------------------------------------