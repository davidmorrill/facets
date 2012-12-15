"""
Defines the interactive Facets UI view tester tool.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from time \
    import strftime

from os.path \
    import exists

from facets.api \
    import HasFacets, List, File, Str, Bool, View, VGroup, Item, UItem, \
           NotebookEditor

from facets.extra.features.api \
    import CustomFeature

from facets.extra.api \
    import file_watch

from facets.extra.helper.themes \
    import TTitle

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'ViewTester' class:
#-------------------------------------------------------------------------------

class ViewTester ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'View Tester'

    # Should a changed file be automatically reloaded:
    auto_load = Bool( True, save_state = True )

    # Should old view be automatically closed when a new one is run?
    auto_close = Bool( True, save_state = True )

    # Custom feature for creating a dynamic 'run' button:
    run_button = CustomFeature(
        image   = '@facets:run',
        click   = 'run_file',
        tooltip = 'Click to run the current file',
        enabled = False
    )

    # The source file containing the view code to be tested:
    file_name = File( droppable = 'Drag a Python source code file here.',
                      connect   = 'to' )

    # The object containing the view being tested:
    view_objects = List( HasFacets )

    # Information message on how to use the view tester:
    info = Str( "Drag a Python file containing an object named 'view' to the "
                "tab for this view." )

    # Status message:
    status = Str

    #-- Facet View Definitions -------------------------------------------------

    facets_view = View(
        VGroup(
            TTitle( 'info', visible_when = 'len(view_objects)==0' ),
            UItem( 'view_objects@',
                   editor     = NotebookEditor( deletable  = True,
                                                export     = 'DockWindowShell',
                                                dock_style = 'auto' ),
            ),
            UItem( 'status',
                   style        = 'readonly',
                   visible_when = 'status!=""',
                   item_theme   = '#themes:title'
            )
        ),
        title = 'View Tester'
    )


    options = View(
        VGroup(
            Item( 'auto_load',
                  label = 'Automatically run a changed file '
            ),
            Item( 'auto_close',
                  label = 'Automatically close old views'
            ),
            group_theme = '#themes:tool_options_group'
        )
    )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, old, new ):
        """ Handles the 'file_name' facet being changed.
        """
        self.set_listener( old, True )
        self.set_listener( new, False )
        self.run_button.enabled = False
        if new != '':
            self.run_file()


    def _auto_load_set ( self, auto_load ):
        """ Handles the 'auto_load' facet being changed.
        """
        if auto_load and self.run_button.enabled:
            self.run_file()

        self.run_button.enabled = False

    #-- Private Methods --------------------------------------------------------

    def run_file ( self ):
        """ Runs the current file and creates it view.
        """
        file_name = self.file_name
        dic       = {}
        try:
            execfile( file_name, dic, dic )
        except Exception, excp:
            self.status = str( excp )

            return

        view = dic.get( 'view' )
        if view is None:
            view = dic.get( 'demo' )

        if view is not None:
            if (not isinstance( view, HasFacets )) and callable( view ):
                    view = view()

            if isinstance( view, HasFacets ):
                if self.auto_close:
                    self.view_objects = [ view ]
                else:
                    self.view_objects.append( view )

                self.status = ('View for %s loaded successfully at %s' %
                               ( file_name, strftime( '%I:%M:%S %p' ) ))
            else:
                self.status = ("%r has a 'view' or 'demo' object that does not "
                               "derive from HasFacets") % self.file_name
        else:
            self.status = ("%r does not contain a 'view' or 'demo' object" %
                           file_name)

        self.run_button.enabled = False


    def set_listener ( self, file_name, remove ):
        """ Sets up/Removes a file watch on a specified file.
        """
        if exists( file_name ):
            file_watch.watch( self.file_changed, file_name, remove = remove )


    def file_changed ( self, file_name ):
        """ Handles the current file being updated.
        """
        if self.auto_load:
            self.run_file()
        else:
            self.run_button.enabled = True

#-- EOF ------------------------------------------------------------------------