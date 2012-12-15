"""
Defines the PythonFileItem class used by the VIP Shell to represent a file
system Python source file.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import HasFacets

from facets.ui.menu \
    import Action

from facets.ui.vip_shell.helper \
    import python_colorize

from file_item \
    import FileItem

from view_item \
    import ViewItem

#-------------------------------------------------------------------------------
#  'PythonFileItem' class:
#-------------------------------------------------------------------------------

class PythonFileItem ( FileItem ):
    """ A Python source file.
    """

    #-- Class Constants --------------------------------------------------------

    # The user intername for an an item of this class:
    ui_name = 'Python File'

    #-- Facet Definitions ------------------------------------------------------

    icon       = '@facets:shell_pythonfile'
    color_code = '\x007'

    # The custom tool bar actions supported by the item (if any):
    actions = [
        Action( image   = '@icons2:Application_1',
                tooltip = 'Display the view for the source file',
                action  = 'item.display_view()' ),

        Action( image   = '@icons2:Pencil?H45L3|h9H17',
                tooltip = 'Edit the source file inline',
                action  = 'item.edit_source_inline()' ),

        Action( image   = '@icons2:EditTab?H45L3|L65s74',
                tooltip = 'Edit the source file in an editor tab',
                action  = 'item.edit_source()' ),

        Action( image   = '@icons2:EditWindow?H45L3|h6H61l50L86',
                tooltip = 'Edit the source file in a separate window',
                action  = 'item.edit_source_window()' ),
    ]

    #-- Public Methods ---------------------------------------------------------

    def key_d ( self, event ):
        """ Displays the view associated with the Python source file.

            The [[d]] key displays the view associated with the shell item's
            associated Python source file. This command is normally used with
            source files that are part of the Facets UI or tools demo.

            If the source file defines a <<demo>> object, the default Facets
            view of that object is displayed inline with the shell. If the
            source file defines a <<popup>> object, the default facets view of
            that object is displayed in a separate pop-up window.
        """
        self.display_view()


    def key_e ( self, event ):
        """ Creates a tab containing the Python source code for the item.
        """
        self.edit_source()


    def display_view ( self ):
        """ Displays the view associated with the Python source file.
        """
        locals       = self.shell.locals
        demo_before  = locals.get( 'demo' )
        popup_before = locals.get( 'popup' )
        self.execute()
        demo = locals.get( 'demo' )
        if (demo is not None) and (demo is not demo_before):
            if not isinstance( demo, HasFacets ):
                demo = demo()

            self.shell.add_history_item_for( ViewItem, demo, lod = 1 )
        else:
            popup = locals.get( 'popup' )
            if (popup is not None) and (popup is not popup_before):
                if not isinstance( popup, HasFacets ):
                    popup = popup()

                popup.edit_facets()


    def edit_source ( self ):
        """ Creates a tab containing the Python source code for the item.
        """
        from facets.ui.editors.vip_shell_editor import VIPShellCode

        self.shell.add_code_item( VIPShellCode( file_name = self.item ) )


    def edit_source_inline ( self ):
        """ Creates an inline Python source code editor for the item.
        """
        from facets.ui.editors.vip_shell_editor import VIPShellCode

        self.shell.add_item_for( self, self.shell.history_item_for(
            ViewItem, VIPShellCode( file_name = self.item ), lod = 1
        ) )


    def edit_source_window ( self ):
        """ Creates a window containing a Python source code editor for the
            item.
        """
        from facets.ui.editors.vip_shell_editor import VIPShellCode

        VIPShellCode(
            file_name = self.item,
            shell     = self.shell,
            id        = 'facets.ui.vip_shell.python_file_item.PythonFileItem'
        ).edit_facets()


    def can_execute ( self ):
        """ Returns True if the item can be 'executed' in some meaningful
            fashion, and False if it cannot.
        """
        return True


    def execute ( self ):
        """ Executes the file (if it is a valid Python source file).
        """
        self.shell.execute_file( self.item )


    def str ( self, item ):
        """ Returns the string value of *item*.
        """
        return python_colorize( self.item_contents )

#-- EOF ------------------------------------------------------------------------
