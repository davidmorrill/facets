"""
Defines the PrintObject tool which attempts to print the contents of any input
object it receives to stdout.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import isfile

from facets.api \
    import HasFacets, Any, Str, View

from facets.ui.pyface.timer.api \
    import do_later

from facets.extra.helper.file_position \
    import FilePosition

from facets.extra.helper.python_file_position \
    import PythonFilePosition

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'PrintObject' class:
#-------------------------------------------------------------------------------

class PrintObject ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'Print Object' )

    # The object to be printed:
    object = Any( connect = 'to' )

    #-- Facet View Definitions -------------------------------------------------

    view = View()

    #-- Facet Event Handlers ---------------------------------------------------

    def _object_set ( self, value ):
        """ Handles the 'object' facet being changed.
        """
        if value is not None:
            self._print_item( value )
            do_later( self.set, object = None )

    #-- Private Methods --------------------------------------------------------

    def _print_item ( self, item ):
        """ Prints the contents of the specified item.
        """
        if isinstance( item, basestring ):
            if isfile( item ):
                if self._print_file( item ):
                    return

        elif isinstance( item, PythonFilePosition ):
            extra = '(%s.%s' % ( item.package_name, item.module_name )
            if item.class_name != '':
                extra += (':' + item.class_name)
                if item.method_name != '':
                    extra += ('.' + item.method_name)

            if self._print_file( item.file_name, item.line, item.lines,
                                 extra + ')\n' ):
                return

        elif isinstance( item, FilePosition ):
            if self._print_file( item.file_name, item.line, item.lines ):
                return

        if isinstance( item, HasFacets ):
            class_name = '%s.%s:' % ( item.__class__.__module__,
                                      item.__class__.__name__ )
            sep        = '-' * len( class_name )
            print '%s\n%s\n%s' % ( sep, class_name, sep )
            item.print_facets()
            print

            return

        print item


    def _print_file ( self, file_name, line = 1, lines = -1, extra = '' ):
        """ Attempts to print a range of the specified file. Returns True if
            successful, and False otherwise.
        """
        try:
            fh   = open( file_name, 'rb' )
            data = fh.readlines()
            fh.close()

            sep   = '-' * max( len( file_name ) + 1, len( extra ) )
            line -= 1
            if lines == -1:
                if line > 0:
                    data = data[ line: ]
            else:
                data = data[ line: line + lines ]

            print '%s\n%s:\n%s%s\n%s\n' % ( sep, file_name, extra, sep,
                                            ''.join( data ) )

            return True
        except:
            return False

#-- EOF ------------------------------------------------------------------------