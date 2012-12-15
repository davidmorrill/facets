"""
Defines a tool for displaying presentations consisting of one or more animated
slides.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import dirname

from facets.api \
    import HasFacets, Str, File, Instance, View, UItem, SyncValue

from facets.core.facet_base \
    import read_file

from facets.ui.pyface.timer.api \
    import do_after

from facets.extra.editors.presentation_editor \
    import PresentationEditor

from facets.extra.services.file_watch \
    import file_watch

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The default initial presentation to display:
DefaultPresentation = """
:hc Connect a file name or text to display a presentation.
-- Default Presentation --
"""[1:-1]

#-------------------------------------------------------------------------------
#  'Presentation' class:
#-------------------------------------------------------------------------------

class Presentation ( Tool ):
    """ Defines a tool for displaying presentations consisting of one or more
        animated slides.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = 'Presentation'

    # The name of a text file containing a presentation to display:
    file_name = File( connect = 'to: text file containing a presentation' )

    # The text string containing a presentation to display:
    text = Str( connect = 'to: presentation text' )

    # The name of a file or directory to use as the presentation file base:
    file_base = File( connect = 'to: presentation file base directory' )

    # A HasFacets object exported by the presentation as a result of an 'xo'
    # command:
    object = Instance( HasFacets,
                       connect = 'from: exported presentation object' )

    # The current presentation:
    presentation = Str( DefaultPresentation )

    #-- Facets View Definitions ------------------------------------------------

    def default_facets_view ( self ):
        return View(
            UItem( 'presentation',
                   editor = PresentationEditor(
                       file_base = SyncValue( self, 'file_base' ),
                       object    = SyncValue( self, 'object' )
                   )
            )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _file_name_set ( self, file_name, old ):
        """ Handles the 'file_name' facet being changed.
        """
        if old != '':
            file_watch.watch( self._update_file, old, remove = True )

        if self._update_file( file_name ):
            file_watch.watch( self._update_file, file_name )


    def _text_set ( self ):
        """ Handles the 'text' facet being changed.
        """
        do_after( 1000, self._update_presentation )

    #-- Private Methods --------------------------------------------------------

    def _update_file ( self, file_name ):
        """ Updates the current presentation with the contents of the file
            specified by *file_name*.
        """
        text = read_file( file_name )
        if ((text is not None)        and
            (text.find( '\x00' ) < 0) and
            (text.find( '\xFF' ) < 0)):
            self.file_base    = dirname( file_name )
            self.presentation = text

            return True

        return False


    def _update_presentation ( self ):
        """ Updates the presentation based on the current value of 'text'.
        """
        self.presentation = self.text

#-- EOF ------------------------------------------------------------------------
