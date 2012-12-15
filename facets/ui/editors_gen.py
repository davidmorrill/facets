"""
Generates a file containing definitions for editors defined in the various
backends.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import glob, sys

#-------------------------------------------------------------------------------
#  Function definitions:
#-------------------------------------------------------------------------------

def gen_editor_definitions ( target_filename = 'editors.py' ):
    """ Generates a file containing definitions for editors defined in the
        various backends.

        The idea is that if a new editor has been declared in any of the
        backends, the author needs to create a file called '***_definition' in
        the Facets package (in facets.ui). This function will be run each time
        the user runs the setup.py file, and the new editor's definition will be
        appended to the editors.py file.

        The structure of the ***_definition file should be as follows:
        ***_definition = '<file name in the backend package>:
                         <name of the Editor or the EditorFactory class'
    """
    base_import_path = 'facets.ui.'
    definition_files = glob.glob( '*_definition.py' )
    new_editors      = []

    for file in definition_files:
        import_path = base_import_path + file.rstrip( '.py' )
        __import__( import_path )
        mod = sys.modules[ import_path ]
        for name in dir( mod ):
            if '_definition' in name:
                new_editors.append( getattr( mod, name ) )

    target_file = open( target_filename, 'a' )

    for editor_name in new_editors:
            function = ( "\ndef %s( *args, **facets ):\n" %
                         editor_name.split( ':' )[1] )
            target_file.write( function )
            func_code =  ' ' * 4 + 'from toolkit import toolkit_object\n'
            func_code += ' ' * 4 + \
                         'return toolkit_object("%s")( *args, **facets )' \
                         % editor_name
            target_file.write( func_code )
            target_file.write( '\n\n' )

    target_file.close()

#-- EOF ------------------------------------------------------------------------