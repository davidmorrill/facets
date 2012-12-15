"""
Defines the HTML "editor" and the HTML editor factory, for the Qt4 user
interface toolkit. HTML editors interpret and display HTML-formatted
text, but do not modify it.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from PyQt4.QtCore \
     import Qt, QUrl, QEvent, SIGNAL

from facets.api \
    import Bool, Str, BasicEditorFactory, toolkit

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Template used to create code blocks embedded in a module comment:
block_template = """<center><table width="95%%"><tr><td bgcolor="#ECECEC"><tt>
%s</tt></td></tr></table></center>"""

# Template used to create lists embedded in a module comment:
list_template = """<%s>
%s
</%s>"""

# Generic html page template:
html_template = """
<html>
  <head>
  </head>
  <body>
%s
  </body>
</html>
"""

# The set of monitored mouse events:
ClickEvents = ( QEvent.MouseButtonPress, QEvent.MouseButtonDblClick )

#-------------------------------------------------------------------------------
#  'WebView' class:
#-------------------------------------------------------------------------------

try:
    from PyQt4.QtWebKit import QWebView

    class WebView ( QWebView ):
        """ A version of QWebView that differentiates between left and middle
            mouse clicking a page link.
        """

        #-- QWebView Method Overrides ------------------------------------------

        def __init__ ( self, parent, editor ):
            """ Initializes the object.
            """
            QWebView.__init__( self, parent )

            self._editor = editor


        def event ( self, event ):
            """ Handles an event for the object.
            """
            if event.type() in ClickEvents:
                self._editor.middle_button = (event.button() == Qt.MidButton)

            return QWebView.event( self, event )
except:
    WebView = None

#-------------------------------------------------------------------------------
#  '_HTMLEditor' class:
#-------------------------------------------------------------------------------

class _HTMLEditor ( Editor ):
    """ Simple style of editor for HTML, which displays interpreted HTML.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the HTML editor scrollable? This values override the default.
    scrollable = True

    # Does the editor actually render HTML?
    renders_html = Bool( True )

    # The URL of the link the user most recently clicked on:
    url = Str

    # The URL of the link the user most recently clicked on using the middle
    # mouse button:
    alt_url = Str

    # The current page title:
    title = Str

    # Was the middle button used to click on a link:
    middle_button = Bool( False )

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        if WebView is not None:
            from PyQt4.QtWebKit import QWebPage

            self.control = control = WebView( parent, self )

            factory = self.factory
            self.sync_value( factory.title, 'title', 'to' )
            control.connect( control, SIGNAL( 'titleChanged(QString)' ),
                             self._on_title_modified )

            url     = factory.url
            alt_url = factory.alt_url
            if (url != '') or (alt_url != ''):
                self.sync_value( url,     'url',     'to' )
                self.sync_value( alt_url, 'alt_url', 'to' )
                control.page().setLinkDelegationPolicy(
                    QWebPage.DelegateAllLinks )
                control.connect( control, SIGNAL( 'linkClicked(QUrl)' ),
                                 self._on_link_clicked )
        else:
            self.renders_html = False
            self.adapter      = toolkit().create_text_input( parent,
                                           read_only = True, multi_line = True )

        self.set_tooltip()


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        text = self.str_value.strip()
        if self.factory.format_text:
            text = self.parse_text( text ).strip()
            if text[:1] != '<':
                text = (html_template % text)[1:-1]

        if self.renders_html:
            if text[:1] != '<':
                self.control.load( QUrl( text ) )
            else:
                self.control.setHtml( text )
        else:
            self.adapter.value = text


    def parse_text ( self, text ):
        """ Parses the contents of a formatted text string into the
            corresponding HTML.
        """
        text  = text.replace( '\r\n', '\n' )
        lines = [ ( '.' + line ).strip()[1:] for line in text.split( '\n' ) ]
        ind   = min( *([ self.indent( line )
                         for line in lines
                         if line != '' ] + [ 1000, 1000 ]) )
        if ind >= 1000:
            ind = 0
        lines     = [ line[ ind: ] for line in lines ]
        new_lines = []
        i = 0
        n = len( lines )

        while i < n:
            line = lines[i]
            m    = self.indent( line )
            if m > 0:
                if line[m] in '-*':
                    i, line = self.parse_list( lines, i )
                else:
                    i, line = self.parse_block( lines, i )
                new_lines.append( line )
            else:
                new_lines.append( line )
                i += 1

        text       = '\n'.join( new_lines )
        paragraphs = [ p.strip() for p in text.split( '\n\n' ) ]

        for i, paragraph in enumerate( paragraphs ):
            if paragraph[:3].lower() != '<p>':
                paragraphs[i] = '<p>%s</p>' % paragraph

        return '\n'.join( paragraphs )


    def parse_block ( self, lines, i ):
        """ Parses a code block.
        """
        m = 1000
        n = len( lines )
        j = i
        while j < n:
            line = lines[j]
            if line != '':
                k = self.indent( line )
                if k == 0:
                    break
                m = min( m, k )
            j += 1

        j -= 1
        while (j > i) and (lines[j] == ''):
            j -= 1

        j   += 1
        temp = [ (('&nbsp;' * (self.indent( line ) - m)) +
                  line.strip())
                 for line in lines[ i: j ] ]

        return ( j, block_template % '\n<br>'.join( temp ) )


    def parse_list ( self, lines, i ):
        """ Parses a list.
        """
        line   = lines[i]
        m      = self.indent( line )
        kind   = line[m]
        result = [ '<li>' + line[ m + 1: ].strip() ]
        n      = len( lines )
        j      = i + 1
        while j < n:
            line = lines[j]
            k    = self.indent( line )
            if k < m:
                break
            if k == m:
                if line[k] != kind:
                    break
                result.append( '<li>' + line[ k + 1: ].strip() )
                j += 1
            elif line[ k ] in '-*':
                j, line = self.parse_list( lines, j )
                result.append( line )
            else:
                result.append( line.strip() )
                j += 1

        style = [ 'ul', 'ol' ][ kind == '*' ]

        return ( j, list_template % ( style, '\n'.join( result ), style ) )


    def indent ( self, line ):
        """ Calculates the amount of white space at the beginning of a line.
        """
        return (len( line ) - len( (line + '.').strip() ) + 1)

    #-- Qt Event Handlers ------------------------------------------------------

    def _on_link_clicked ( self, url ):
        """ Handles the user clicking on a web page link.
        """
        url = str( url.toString() )
        if self.middle_button:
            if self.factory.alt_url != '':
                self.alt_url = url
            else:
                self.url = url
        elif self.factory.url != '':
            self.url = url
        else:
            self.value = url
            self.update_editor()


    def _on_title_modified ( self, title ):
        """ Handles the page title being changed.
        """
        self.title = str( title )

#-------------------------------------------------------------------------------
#  'HTMLEditor' class:
#-------------------------------------------------------------------------------

class HTMLEditor ( BasicEditorFactory ):
    """ PyQt4 editor factory for HTML editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Class used to create all editor styles. This value overrides the default.
    klass = _HTMLEditor

    # Should implicit text formatting be converted to HTML?
    format_text = Bool( False )

    # The optional extended facet name of a string containing the URL for the
    # most recent link the user clicked on:
    url = Str

    # The optional extended facet name of a string containing the URL for the
    # most recent link the user clicked on using the middle mouse button.
    #
    # Note: If 'alt_url' is not specified, but 'url' is, then all urls are sent
    # to 'url', whether they were clicked using the left or middle mouse button.
    alt_url = Str

    # The optional extended facet name of a string containing the current page
    # title:
    title = Str

#-- EOF ------------------------------------------------------------------------