"""
Defines the ExceptionItem class used by the VIP Shell to represent an exception
raised by executing a Python or shell command.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import basename

from facets.api \
    import Any, Str

from labeled_item \
    import LabeledItem

from facets.ui.graphics_text \
    import color_tag_for, tag_ref_for

from facets.ui.vip_shell.tags.api \
    import PythonFileTag, ContentTag

from facets.ui.vip_shell.helper \
    import max_len, trim_margin, python_colorize, source_context

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Separator line:
Separator = '\n' + color_tag_for( 'C' )

# Possible line prefixes:
LinePrefix = ( '   ', '\x00C-->' )

#-------------------------------------------------------------------------------
#  'ExceptionItem' class:
#-------------------------------------------------------------------------------

class ExceptionItem ( LabeledItem ):
    """ An exception raised by executing a command.
    """

    #-- Facet Definitions ------------------------------------------------------

    type       = 'exception'
    icon       = '@facets:shell_exception'
    color_code = '\x004'

    # Optional name of the function called from the first frame:
    callee = Str

    #-- Private Facet Definitions ----------------------------------------------

    # Mapping from referenced file names to associated tag indices:
    file_names = Any( {} )

    #-- Facet Default Values ---------------------------------------------------

    def _item_label_default ( self ):
        frame         = self.item[0]
        line          = frame.f_lineno
        caller        = frame.f_code.co_name
        file_name     = frame.f_code.co_filename
        cc, file_name = self._file_info_for( file_name, line )

        return ('\x00B%s\x004 called from \x00B%s\x004 in %s%s\x004 at \x00C%d'
                % ( self.callee, caller, cc, file_name, line ))


    def _item_contents_default ( self ):
        caller_len = max_len(
            [ frame.f_code.co_name for frame in self.item ]
        ) + 2

        call_stack = []
        for frame in self.item:
            line           = frame.f_lineno
            caller         = frame.f_code.co_name
            file_name      = frame.f_code.co_filename
            cc1, tr1       = self._source_info_for( file_name, line, frame )
            cc2, file_name = self._file_info_for( file_name, line )
            call_stack.append(
                '%s%s\x004 | %s%s\x004 at \x00C%d%s' %
                ( cc1, (caller + '\x004').ljust( caller_len ), cc2, file_name,
                  line, tr1 )
            )

        return '\n'.join( call_stack )

    #-- Public Methods ---------------------------------------------------------

    def can_execute ( self ):
        """ Returns True if the item can be 'executed' in some meaningful
            fashion, and False if it cannot.
        """
        return True


    def execute ( self ):
        """ Executes some action for this item.
        """
        for tag in self.tags:
            if isinstance( tag, ContentTag ):
                tag.enabled = False

    #-- Private Methods --------------------------------------------------------

    def _source_info_for ( self, file_name, cur_line, frame ):
        """ Returns the color code and optional tag reference for the source
            code for the file name and stack frame specified by *file_name* and
            *frame*, and where execution is currently on *cur_line*.
        """
        start, lines = self.shell.source_for_frame( frame )
        if start is None:
            return ( color_tag_for( 'B' ), '' )

        context = self.shell.context
        if context < 50:
            begin  = max( 0, cur_line - start - context ) + 1
            end    = min( len( lines ), cur_line - start + context + 1 ) + 1
            lines  = source_context( lines, begin, end )
            start += (begin - 1)

        lines = python_colorize(
            trim_margin( lines ), frame.f_locals, self.tags
        )
        format = '%%0%dd' % len( str( start + len( lines ) - 1 ) )
        source = '\n'.join(
            [ '%s \x008%s|\x00E %s' % ( LinePrefix[ (start + i) == cur_line ],
                    format % (start + i), line )
              for i, line in enumerate( lines ) ]
        )
        tag = len( self.tags )
        self.tags.append(
            ContentTag( content = '%s\n%s%s' % ( Separator, source, Separator) )
        )

        return ( color_tag_for( 'B', tag ), tag_ref_for( tag ) )


    def _file_info_for ( self, file_name, line ):
        """ Returns the color code and adjusted file name to use for a specified
            file name.
        """
        key = ( file_name, line )
        tag = self.file_names.get( key )
        if tag is None:
            self.file_names[ key ] = tag = len( self.tags )
            self.tags.append( PythonFileTag(
                file    = file_name,
                tooltip = file_name,
                line    = line
            ) )

        return ( color_tag_for( 'C', tag ), basename( file_name ) )

#-- EOF ------------------------------------------------------------------------
