"""
Defines the HTML "editor" and the HTML editor factory, for the wxPython
user interface toolkit. HTML editors interpret and display HTML-formatted
text, but do not modify it.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx.html as wh

from facets.api \
    import Bool, BasicEditorFactory

from editor \
    import Editor

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Template used to create code blocks embedded in the module comment
block_template = """<center><table width="95%%"><tr><td bgcolor="#ECECEC"><tt>
%s</tt></td></tr></table></center>"""

# Template used to create lists embedded in the module comment
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

#-------------------------------------------------------------------------------
#  '_HTMLEditor' class:
#-------------------------------------------------------------------------------

class _HTMLEditor ( Editor ):
    """ Simple style of editor for HTML, which displays interpreted HTML.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Is the HTML editor scrollable? This values override the default.
    scrollable = True

    #-- Public Methods ---------------------------------------------------------

    def init ( self, parent ):
        """ Finishes initializing the editor by creating the underlying toolkit
            widget.
        """
        self.control = wh.HtmlWindow( parent )
        self.control.SetBorders( 2 )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes external to the
            editor.
        """
        text = self.str_value
        if self.factory.format_text:
            text = self.parse_text( text ).strip()
            if text[0:1] != '<':
                text = (html_template % text)[1:-1]

        self.control.SetPage( text )


    def parse_text ( self, text ):
        """ Parses the contents of a formatted text string into the
            corresponding HTML.
        """
        text  = text.replace( '\r\n', '\n' )
        lines = [ ( '.' + line ).strip()[1:] for line in text.split( '\n' ) ]
        ind   = min( * ( [ self.indent( line ) for line in lines
                         if line != '' ] + [ 1000, 1000 ] ) )
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

        j += 1
        temp = [ ( ( '&nbsp;' * ( self.indent( line ) - m ) ) +
                 line.strip() ) for line in lines[ i: j ] ]

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
        return len( line ) - len( ( line + '.' ).strip() ) + 1

#-------------------------------------------------------------------------------
#  'HTMLEditor' class:
#-------------------------------------------------------------------------------

class HTMLEditor ( BasicEditorFactory ):
    """ wxPython editor factory for HTML editors.
    """

    #-- Facet Definitions ------------------------------------------------------

    # Class used to create all editor styles. This value overrides the default.
    klass = _HTMLEditor

    # Should implicit text formatting be converted to HTML?
    format_text = Bool( True )

#-- EOF ------------------------------------------------------------------------