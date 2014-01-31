"""
A tool for creating 'demo' screen shots.

The tool uses the 'demo' framework to iterate over each demonstration contained
in a demo and create a corresponding screen shot for the demonstration.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import join, dirname, exists

from facets.api \
    import HasFacets, Instance, Str, List, Button, Image, View, HGroup, Item, \
           UItem, ImageEditor, inn

from facets.core.facet_base \
    import file_with_ext

from facets.ui.image \
    import ImageLibrary

from facets.ui.pyface.timer.api \
    import do_after

from demo \
    import demo, Demo, DemoPath, DemoFile

#-------------------------------------------------------------------------------
#  'DemoScreenShots' class:
#-------------------------------------------------------------------------------

class DemoScreenShots ( HasFacets ):

    #-- Facet Definitions ------------------------------------------------------

    # The Demo object describing the demonstration:
    # The root DemoPath for the demo tree:
    demo = Instance( Demo )

    # The list of DemoFile objects to be processed:
    demo_files = List

    # The current DemoFile object being displayed
    demo_file = Instance( DemoFile )

    # The full path of the current file being processed:
    path = Str

    # The current snapshot image:
    image = Image

    # Event fired when user wants to take a screen shot:
    snap = Button( 'Snap' )

    # Event fired when user wants to continue with next demo:
    next = Button( 'Next' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'image', editor = ImageEditor() ),
        HGroup(
            Item( 'path', style = 'readonly' ),
            UItem( 'snap', enabled_when = 'demo_file is not None' ),
            UItem( 'next', enabled_when = 'demo_file is not None' ),
            group_theme = '@xform:b?L35'
        ),
        title  = 'Demo Screen Shots',
        id     = 'facets.extra.demo.demo_screen_shots.DemoScreenShots',
        width  = 0.5,
        height = 0.5
    )

    #-- HasFacets Method Overrides ---------------------------------------------

    def facets_init ( self ):
        """ Handles initializing the object.
        """
        do_after( 250, self._initialize )

    #-- Private Methods --------------------------------------------------------

    def _initialize ( self ):
        """ Initializes the list of DemoFiles to process and then starts
            processing them.
        """
        self._process( self.demo.root )
        self._process_file()


    def _process ( self, demo_path ):
        """ Processes all of the files in the DemoPath object specified by
            *demo_path*.
        """
        use_files  = demo_path.use_files
        demo_files = self.demo_files
        for demo_object in demo_path.get_children():
            if isinstance( demo_object, DemoPath ):
                self._process( demo_object )
            elif use_files:
                demo_files.append( demo_object )


    def _process_file ( self ):
        """ Takes a screen shot for the next DemoFile object in the queue.
        """
        while len( self.demo_files ) > 0:
            demo_file = self.demo_files.pop( 0 )
            try:
                self.ui                = demo_file.demo.edit_facets()
                self.ui.control.bounds = ( 500, 500, 1280, 720 )
                self.demo_file         = demo_file
                self.path              = demo_file.path
                image_file             = file_with_ext( demo_file.path, 'png' )
                self.image = image_file if exists( image_file ) else None

                break
            except:
                pass

    #-- Facet Event Handlers ---------------------------------------------------

    def _snap_set ( self ):
        """ Handles the 'snap' event being fired.
        """
        self.image = self.ui.control.image
        self.image.save( file_with_ext( self.demo_file.path, 'png' ) )


    def _next_set ( self ):
        """ Handles the 'next' event being fired.
        """
        inn( self.demo_file.demo, 'dispose' )()
        self.ui.dispose()
        self.demo_file = self.ui = None
        self._process_file()

#-- Run the program (if invoked from the command line) -------------------------

if __name__ == '__main__':
    import facets.extra.demo.ui

    ImageLibrary().add_volume(
        join( dirname( facets.extra.demo.ui.__file__ ), 'images' )
    )
    DemoScreenShots( demo = demo( run = False ) ).edit_facets()

#-- EOF ------------------------------------------------------------------------