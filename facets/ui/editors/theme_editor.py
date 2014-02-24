"""
A custom editor for Theme objects.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import basename, splitext

from facets.api                                                       \
    import File, Instance, Button, View, HGroup, VGroup, Item, Theme, \
           HLSColorEditor, UIEditor, BasicEditorFactory, spring, toolkit

from facets.core.facet_base \
    import save_file

from facets.ui.ui_facets \
    import Border, Margin

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The group theme used around the various 'margin' editors:
margin_theme = Theme( '@xform:btd?H61L20S9', content = ( 5, 5, 5, 5 ) )

# The template used to generate the file format for a theme:
ThemeFileTemplate = """
#-- Imports --------------------------------------------------------------------

from facets.api import Theme

#-- Theme Definition -----------------------------------------------------------

%s = theme = %s

#-- View the theme (if invoked from the command line) --------------------------

if __name__ == '__main__':
    from facets.extra.tools.theme_layout import ThemeLayout

    ThemeLayout( theme = theme ).edit_facets()

#-- EOF ------------------------------------------------------------------------
"""[1:-1]

#-------------------------------------------------------------------------------
#  '_ThemeEditor' class:
#-------------------------------------------------------------------------------

class _ThemeEditor ( UIEditor ):
    """ A custom editor for Theme instances.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Indicate that the editor is resizable. This value overrides the default.
    scrollable = True

    # The border inset:
    border = Instance( Border, () )

    # The margin to use around the content:
    content = Instance( Margin, () )

    # The margin to use around the label:
    label = Instance( Margin, () )

    # The file name the theme should be saved to if the user requests it:
    file_name = File

    # Event fired when the user wants to save the theme to a file:
    save_file = Button( '@icons2:Floppy' )

    # Event fired when the user wants to copy the theme to the clipboard:
    clipboard = Button( '@icons2:Clipboard' )

    #-- HasFacets Class Method Overrides ---------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        return self.edit_facets( parent = parent )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        theme = self.value
        self.set(
            content = theme.content,
            border  = theme.border,
            label   = theme.label
        )


    def default_facets_view ( self ):
        """ Returns the default facets view for the object's class.
        """
        return View(
            HGroup(
                VGroup(
                    Item( 'content', style = 'custom' ),
                    group_theme = margin_theme,
                    label       = 'Content',
                    show_labels = False
                ),
                VGroup(
                    Item( 'label', style = 'custom' ),
                    group_theme = margin_theme,
                    label       = 'Label',
                    show_labels = False
                ),
                VGroup(
                    Item( 'border', style = 'custom' ),
                    group_theme = margin_theme,
                    label       = 'Border',
                    show_labels = False
                )
            ),
            HGroup(
                spring,
                Item( 'object.value.alignment', style = 'custom' ),
                spring,
                Item( 'save_file',
                      show_label = False,
                      tooltip    = 'Save the theme to a file'
                ),
                Item( 'clipboard',
                      show_label = False,
                      tooltip    = 'Copy the theme to the clipboard'
                ),
                group_theme = '@xform:b?H61L20S9'
            ),
            HGroup(
                VGroup(
                    Item( 'object.value.content_color',
                          label   = 'Content',
                          editor  = HLSColorEditor( edit = 'lightness' ),
                          tooltip = 'Content text color',
                    ),
                    Item( 'object.value.content_font',
                          label   = 'Font',
                          tooltip = 'Content text font',
                    ),
                    group_theme = '@xform:b?H61L20S9'
                ),
                VGroup(
                    Item( 'object.value.label_color',
                          label   = 'Label',
                          editor  = HLSColorEditor( edit = 'lightness' ),
                          tooltip = 'Label text color',
                    ),
                    Item( 'object.value.label_font',
                          label   = 'Font',
                          tooltip = 'Label text font',
                    ),
                    group_theme = '@xform:b?H61L20S9'
                )
            ),
            kind = 'subpanel'
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _save_file_set ( self ):
        """ Handles the user clicking the 'Save file' button.
        """
        file_name = save_file( self.file_name, self._theme_file )
        if file_name is not None:
            self.file_name = file_name


    def _clipboard_set ( self ):
        """ Handles the user clicking the 'Clipboard' button.
        """
        toolkit().clipboard().text = str( self.value )

    #-- Private Methods --------------------------------------------------------

    def _theme_file ( self, file_name ):
        name = splitext( basename( file_name ) )[0]

        return (ThemeFileTemplate % ( name, self.value ))

#-------------------------------------------------------------------------------
#  'ThemeEditor' class:
#-------------------------------------------------------------------------------

class ThemeEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _ThemeEditor

#-- EOF ------------------------------------------------------------------------