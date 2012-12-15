"""
Describe the module function here...
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import sys

from facets.extra.helper.ex_fbi \
    import SavedBreakPoints

#-------------------------------------------------------------------------------
#  Execute:
#-------------------------------------------------------------------------------

if __name__ == '__main__':

    # Load the file containing all current externally set breakpoints:
    bp = SavedBreakPoints()

    # If no command line arguments specified, clear all defined break points:
    if len( sys.argv ) < 2:
        bp.clear_bp()
        bp.save()

        # All done, exit:
        sys.exit( 0 )

    # Get the breakpoints associated with the specified file:
    source_file = bp.source_file_for( sys.argv[1] )

    # If no line number arguments begin with a '+' or '-' or '?' or '#' or '@'
    # or '!', then delete all current break points for the specified file:
    if len( [ line for line in sys.argv[2:]
                   if line[0:1] in '+-?#@!' ] ) == 0:
        source_file.clear_bp()

    # Process each command line source file line number:
    for line in sys.argv[2:]:
        code = ''
        col  = line.find( '[' )
        if col >= 0:
            lines = line[ col + 1: -1 ].replace( '[[]]', '    '
                                        ).split( '[[nl]]' )
            n     = ( len( lines[0] ) - len( lines[0].lstrip() ) )
            code  = '[[nl]]'.join( [ x[n:] for x in lines ] )
            line  = line[ : col ]

        lines = line.split( ',' )
        c     = line[0:1]
        if c in '?#@!':
            line = int( lines[0][1:] )
            if c == '?':
                # A line number starting with '?' means toggle the break point:
                source_file.toggle_bp( line )
            elif c == '#':
                # A line number starting with '#' means set a count break point:
                source_file.set_bp( line, bp_type = 'Count' )
            elif c == '@':
                end_line = line
                if len( lines ) > 1:
                    end_line = int( lines[1] )

                # A line number starting with '@' means set a trace break point:
                source_file.set_bp( line, end_line = end_line,
                                          bp_type  = 'Trace' )
            else:
                # A line number starting with '!' means set a patch break point:
                source_file.set_bp( line, bp_type = 'Patch', code = code )
        else:
            line = int( line )
            if code != '':
                source_file.set_bp( line, bp_type = 'Print', code = code )
            elif line >= 0:
                # A positive line number means add the break point:
                source_file.set_bp( line )
            else:
                # A negative line number means remove the break point:
                source_file.reset_bp( -line )

    # Save the external breakpoint file:
    bp.save()

#-- EOF ------------------------------------------------------------------------