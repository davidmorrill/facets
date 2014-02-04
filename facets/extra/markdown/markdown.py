"""
Defines the Markdown facet and MarkdownEditor used for displaying markdown
formatted strings as rendered HTML.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from os.path \
    import abspath

from markdown2 \
    import markdown

from facets.api \
    import Str, Bool, File, View, UItem, CodeEditor, HTMLEditor, UIEditor, \
           BasicEditorFactory, on_facet_set

from facets.core.facet_base \
    import read_file, get_resource

from facets.extra.api \
    import watch

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# The list of extra markdown features to enable:
MarkdownExtras = [ 'code-friendly', 'cuddled-lists', 'fenced-code-blocks' ]

# The HTML template used to create a web page from the converted markdown text:
HTMLTemplate = ("""
<html>
  <head>
    <title>Markdown</title>
    <link rel="stylesheet" type="text/css" href="file:///%s">
    %%s
  </head>
  <body>
%%s  </body>
</html>
"""[1:-1]) % get_resource( 'default.css' )

# The CSS <style> template to use when CSS rules are provided:
CSSStyleTemplate = '<style type="text/css">\n%s\n</style>'

#-------------------------------------------------------------------------------
#  'Markdown' facet definition:
#-------------------------------------------------------------------------------

class Markdown ( Str ):
    """ Defines a facet whose value is a *markdown* encoded string.
    """

    def create_editor ( self ):
        """ Returns the default facets UI editor for this type of facet.
        """
        return MarkdownEditor( **self.settings( 'css', 'show_raw' ) )

#-------------------------------------------------------------------------------
#  '_MarkdownEditor' class:
#-------------------------------------------------------------------------------

class _MarkdownEditor ( UIEditor ):
    """ Defines the implementation of the editor class for viewing a markdown
        encoded string as an HTML formatted web page.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Mark the editor as scrollable. This value overrides the default:
    scrollable = True

    # The HTML generated from the markdown encoded string:
    html = Str

    # The current CSS rules used to style the generated HTML:
    css = Str

    # The most recently read contents of a markdown file:
    markdown = Str

    # The name of the current markdown source file being watched (if any):
    markdown_file = File

    # The name of the current CSS source file being watched (if any):
    css_file = File

    #-- Facet View Definitions -------------------------------------------------

    raw_view = View( UItem( 'html', editor = CodeEditor() ) )
    web_view = View( UItem( 'html', editor = HTMLEditor() ) )

    #-- Editor Method Overrides ------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        self._css_update()
        return self.edit_facets(
            parent = parent,
            view   = 'raw_view' if self.factory.show_raw else 'web_view',
            kind   = 'editor'
        )


    @on_facet_set( 'css, markdown' )
    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        md = self.value.rstrip()
        if md[-3:].lower() == '.md':
            md = abspath( md )
            if self.markdown_file != md:
                self._markdown_file_watch( True )
                self.markdown_file = md
                self._markdown_file_watch()
                self._update_markdown_file( md )

            md = self.markdown

        html      = markdown( md, extras = MarkdownExtras )
        self.html = (html if self.factory.show_raw else
                     (HTMLTemplate % ( self.css, html )))


    def dispose ( self ):
        """ Disposes of the contents of an editor.
        """
        self._markdown_file_watch( True )
        self._css_file_watch( True )

        super( _MarkdownEditor, self ).dispose()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:css' )
    def _css_update ( self ):
        """ Handles the 'factory.css' facet being changed.
        """
        css = self.factory.css.strip()
        if css == '':
            self.css = ''
        elif css[-4:].lower() == '.css':
            css = abspath( css )
            if self.css_file != css:
                self._css_file_watch( True )
                self.css_file = css
                self._css_file_watch()
                self._update_css_file( css )
        else:
            self.css = CSSStyleTemplate % css

    #-- FileWatch Event Handlers -----------------------------------------------

    def _update_css_file ( self, css_file ):
        """ Handles the current .css file being updated in some way.
        """
        css      = read_file( css_file )
        self.css = ('' if css is None else (CSSStyleTemplate % css))


    def _update_markdown_file ( self, markdown_file ):
        """ Handles the current markdown file being updated in some way.
        """
        self.markdown = read_file( markdown_file ) or ''

    #-- Private Methods --------------------------------------------------------

    def _css_file_watch ( self, remove = False ):
        """ Set/Remove a CSS file watcher.
        """
        if self.css_file != '':
            watch( self._update_css_file, self.css_file, remove = remove )


    def _markdown_file_watch ( self, remove = False ):
        """ Set/Remove a markdown file watcher.
        """
        if self.markdown_file != '':
            watch( self._update_markdown_file, self.markdown_file,
                   remove = remove )

#-------------------------------------------------------------------------------
#  'MarkdownEditor' class:
#-------------------------------------------------------------------------------

class MarkdownEditor ( BasicEditorFactory ):
    """ Defines an editor class for viewing a markdown encoded string as a
        HTML formatted web page.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _MarkdownEditor

    # The optional CSS styles to apply to the HTML generated from the markdown
    # input string (can either be the name of a file containing CSS rules or a
    # string containing CSS rules):
    css = Str( facet_value = True )

    # Should the generated HTML be shown as raw text (True) or as a fully
    # formatted browser web page (False)?
    show_raw = Bool( False )

#-- EOF ------------------------------------------------------------------------
