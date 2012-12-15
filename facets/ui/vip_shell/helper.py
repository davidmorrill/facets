"""
Defines common constants and functions used by the VIP Shell.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re
import sys

from os \
    import stat

from os.path \
    import isdir, isfile, basename, splitext

from time \
    import localtime, strftime

from cStringIO \
    import StringIO

from tokenize \
    import generate_tokens

from types \
    import BuiltinFunctionType, BuiltinMethodType, MethodType, \
           UnboundMethodType, FunctionType

from facets.ui.graphics_text \
    import ColorTableCode, color_tag_for

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The list of shell item types:
ItemTypes = [
    'miscellaneous', 'command', 'result', 'output', 'error', 'exception', 'file',
    'view'
]

# The set of shell item types:
ItemSet = set( ItemTypes )

# Mapping from type codes to item types:
TypeCodes = {
    'c': 'command',
    'e': 'error',
    'f': 'file',
    'm': 'miscellaneous',
    'o': 'output',
    'r': 'result',
    'v': 'view',
    'x': 'exception',
}

# The set of Python keywords:
PythonKeywords = set( [
    'def', 'if', 'else', 'elif', 'for', 'in', 'try', 'except', 'finally',
    'from', 'import', 'class', 'return', 'break', 'continue', 'while', 'not',
    'and', 'or', 'assert', 'raise', 'del', 'print', 'yield', 'global', 'exec',
    'with', 'as', 'is'
] )

# The set of special Python values:
PythonSpecial = set( [
    'True', 'False', 'None'
] )

# The mapping from Python token types (from the 'token' module) to color codes:
TokenColor = {
    2:  'G',    # Number
    3:  'F',    # String
    53: 'I'     # Comment
}

# Recognized image extensions:
ImageExtensions = set( [ '.png', '.jpg', '.jpeg', '.gif' ] )

# The types which are not worth showing as tagged items in a traceback:
BoringTypes = (
    FunctionType, MethodType, UnboundMethodType, BuiltinFunctionType,
    BuiltinMethodType
)

#-------------------------------------------------------------------------------
#  Helper Functions:
#-------------------------------------------------------------------------------

def max_len ( strings, limit = sys.maxint ):
    """ Returns the maximum length of a list of strings.
    """
    return reduce( lambda x, y: max( x, len( y ) * (len( y ) <= limit) ),
                   strings, 0 )


def as_repr ( value, max_len = 80 ):
    """ Returns the string form of *value* with a maximum length specified by
        *max_len*.
    """
    result = repr( value )
    if len( result ) <= max_len:
        return result

    n = max_len - 5

    return ('%s ... %s' % ( result[ : (n + 1) / 2 ],
                            result[  -n / 2: ] ))


def as_lines ( text ):
    """ Returns *text*, which can either be a list of strings, or a single
        string, as a list of strings. If *text* is a single string, it will be
        split into lines at each newline (i.e. '\n') character.
    """
    if isinstance( text, basestring ):
        return text.split( '\n' )

    return text


def as_string ( text ):
    """ Returns *text*, which can either be a list of strings, or a single
        string, as a list of strings. If *text* is a list of strings, it will be
        converted into a single string by joining each line using newline
        (i.e. '\n') characters.
    """
    if not isinstance ( text, basestring ):
        return '\n'.join( text )

    return text


def as_like ( in_data, out_data ):
    """ Returns *in_data* in the same form as *out_data*, where *in_data* and
        *out_data* can be either a list of strings or a single string.
    """
    if isinstance( out_data, basestring ):
        return as_string( in_data )

    return as_lines( in_data )


def trim_margin ( text ):
    """ Returns a block of *text* with its left margin trimmed off. *text* can
        either be a string containing '\n' characters or a list of strings. The
        result is in the same form as the input *text*.
    """
    min_ws = 999999
    lines  = as_lines( text )

    for line in lines:
        sline = line.lstrip()
        if sline != '':
            min_ws = min( min_ws, len( line ) - len( sline ) )

    for i, line in enumerate( lines ):
        lines[ i ] = line.rstrip()[ min_ws: ]

    return as_like( lines, text )


def remove_color ( text ):
    """ Return *text* with any embedded color codes removed.
    """
    if text[:1] == ColorTableCode:
        text = text[ text.find( '.' ) + 1: ]

    return re.sub( '(\x00.)|(\x01.....)', '', text )


def replace_markers ( text, emphasis = 'B', example = 'C' ):
    """ Returns the specified *text* with all [[...]] and <<...>> markers
        replaced with their corresponding color codes, as specified by
        *emphasis* and *example*.
    """
    return text.replace( '[[', '\x00' + emphasis
              ).replace( ']]', '\x000'
              ).replace( '<<', '\x00' + example
              ).replace( '>>', '\x000' )


def source_context ( code, start, end ):
    """ Returns the subset of the Python source code *code* that exists between
        line *start* and *end*.
    """
    last_column = last_line = 0
    prev_line   = ''
    tokens      = []
    tokenizer   = generate_tokens( StringIO( as_string( code ) ).readline )
    try:
        for type, token, first, last, line in tokenizer:
            if type == 0:
                break

            if type in ( 5, 6 ):
                continue

            end_line, end_column   = last_line, last_column
            last_line, last_column = last
            if last_line < start:
                continue

            first_line, first_column = first
            if first_line >= end:
                break

            if end_line != first_line:
                if prev_line[-2:] == '\\\n':
                    tokens.append( ' \\\n' )

                end_column = 0

            if type != 4:
                token = (' ' * (first_column - end_column)) + token

            tokens.append( token )
            prev_line = line
    except:
        pass

    return as_like( ''.join( tokens ).rstrip(), code )


def python_colorize ( code, locals = {}, tags = None ):
    """ Returns a colorized version of the specified Python *code*.
    """
    from facets.ui.vip_shell.tags.value_tag import ValueTag

    last_color  = ''
    last_column = last_line = 0
    prev_line   = ''
    was_dot     = False
    context     = None
    cache       = {}
    tokens      = []
    tokenizer   = generate_tokens( StringIO( as_string( code ) ).readline )
    try:
        for type, token, first, last, line in tokenizer:
            if type == 0:
                break

            if type in ( 5, 6 ):
                continue

            if type == 1:
                if token in PythonKeywords:
                    color = 'H'
                elif token in PythonSpecial:
                    color = 'J'
                else:
                    color = 'E'
                    if was_dot:
                        if context is not None:
                            try:
                                context = getattr( context, token )
                                label  += ('.' + token)
                            except:
                                context = label = None
                        else:
                            label = None
                    else:
                        context = label = None
                        if token in locals:
                            context = locals[ token ]
                            label   = token

                    if label is not None:
                        tag = cache.get( label )
                        if ((tag is None) and
                            (not isinstance( context, BoringTypes ))):
                            cache[ label ] = tag = len( tags )
                            tags.append(
                                ValueTag( label = label, value = context )
                            )

                        if tag is not None:
                            color = last_color = 'E'
                            token = ('%s%s%s' % (
                                     color_tag_for( 'C', tag ), token,
                                     color_tag_for( color ) ))
                        else:
                            context = None
            else:
                color = TokenColor.get( type, 'E' )

            first_line, first_column = first
            if last_line != first_line:
                if prev_line[-2:] == '\\\n':
                    tokens.append( ' \\\n' )

                last_column = 0

            prefix = ' ' * (first_column - last_column)

            if color != last_color:
                token = color_tag_for( color ) + token

            if type != 4:
                if color != 'E':
                    token = token.replace( '\n', '\n' + color_tag_for( color ) )

                token = prefix + token

            tokens.append( token )
            prev_line  = line
            last_color = color
            was_dot    = (token == '.')
            last_line, last_column = last
    except:
        pass

    return as_like( ''.join( tokens ), code )


def file_info_for ( file_name, cc1 = '', cc2 = '' ):
    """ Returns a formatted string containing information about the specified
        *file_name*. *cc1* and *cc2* are optional color codes to insert before
        and after the file name.
    """
    info = stat( file_name )
    size = info.st_size
    if isdir( file_name ):
        size = '/'

    time   = strftime( '%m/%d/%Y  %I:%M:%S %p', localtime( info.st_mtime ) )
    format = '%s%-40s %11s  %s'
    if cc2 != '':
        format = '%s%-42s %11s  %s'

    return (format % ( cc1, basename( file_name ) + cc2, size, time ))


def file_class_for ( file_name ):
    """ Returns the appropriate PathItem subclass to use for a specified
        *file_name*.
    """
    from items.api import DirectoryItem, FileItem, PythonFileItem, ImageFileItem

    if isdir( file_name ):
        return DirectoryItem

    ext = splitext( file_name )[1].lower()
    if ext == '.py':
        return PythonFileItem

    if ext in ImageExtensions:
        return ImageFileItem

    return FileItem


def source_files_for ( value ):
    """ Returns a list containing the file names for each source file used
        in the implementation of the specified *value*. Returns None if no
        implementation information could be determined.
    """
    # Try to get the list of the value's base classes:
    try:
        classes = value.__mro__
    except:
        try:
            classes = value.__class__.__mro__
        except:
            return None

    # Get the file name of each base class whose source file can be found:
    file_names = []
    if classes is not None:
        for klass in classes:
            module = sys.modules.get( klass.__module__ )
            if module is not None:
                file_name = getattr( module, '__file__', None )
                if file_name is not None:
                    base, ext = splitext( file_name )
                    if ext == '.pyc':
                        file_name = base + '.py'

                    if isfile( file_name ) and (file_name not in file_names):
                        file_names.append( file_name )

    return file_names

#-- EOF ------------------------------------------------------------------------
