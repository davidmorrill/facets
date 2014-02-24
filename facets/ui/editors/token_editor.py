"""
Defines the TokenEditor class for viewing the contents of some Python source as
a list of tokens.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from tokenize \
    import generate_tokens

from token \
    import tok_name

from cStringIO \
    import StringIO

from facets.api \
    import HasFacets, Str, Int, Float, List, View, UItem, UIEditor, \
           GridEditor, BasicEditorFactory

from facets.ui.grid_adapter \
    import GridAdapter

#-------------------------------------------------------------------------------
#  'TokenAdapter' class:
#-------------------------------------------------------------------------------

class TokenAdapter ( GridAdapter ):
    """ Adapts Token objects for display using a GridEditor.
    """

    columns = [
        ( 'Type',   'type'   ),
        ( 'Token',  'token'  ),
        ( 'SLine',  'sline'  ),
        ( 'SCol',   'scol'   ),
        ( 'ELine',  'eline'  ),
        ( 'ECol',   'ecol'   ),
        ( 'Source', 'source' )
    ]

    type_width      = Float( 110 )
    sline_width     = Float( 40 )
    scol_width      = Float( 40 )
    eline_width     = Float( 40 )
    ecol_width      = Float( 40 )
    sline_alignment = Str( 'right' )
    scol_alignment  = Str( 'right' )
    eline_alignment = Str( 'right' )
    ecol_alignment  = Str( 'right' )

#-------------------------------------------------------------------------------
#  'Token' class:
#-------------------------------------------------------------------------------

class Token ( HasFacets ):
    """ Represents a Python source code token.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The type of the token:
    type = Str

    # The token:
    token = Str

    # The starting line of the token:
    sline = Int

    # The starting column of the token:
    scol = Int

    # The ending line of the token:
    eline = Int

    # The ending column of the token:
    ecol = Int

    # The source code line containing the token:
    source = Str

#-------------------------------------------------------------------------------
#  '_TokenEditor' class:
#-------------------------------------------------------------------------------

class _TokenEditor ( UIEditor ):
    """ Defines the implementation of the editor class for viewing the tokens
        of a Python source code string.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The list of tokens:
    tokens = List # ( Token )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'tokens', editor = GridEditor( adapter    = TokenAdapter,
                                              operations = [] )
        )
    )

    #-- Editor Method Overrides ------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        return self.edit_facets( parent = parent, kind = 'editor' )


    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        value  = self.value
        tokens = []
        if isinstance( value, basestring ):
            tokenizer = generate_tokens( StringIO( value ).readline )
            source    = ''
            try:
                for type, token, first, last, line in tokenizer:
                    if line == source:
                        line = ''
                    else:
                        source = line

                    tokens.append( Token(
                        type   = '%s (%d)' %
                                 ( tok_name.get( type, '???' ).lower(), type ),
                        token  = token.replace( '\n', '\\n' ),
                        sline  = first[0],
                        scol   = first[1] + 1,
                        eline  = last[0],
                        ecol   = last[1] + 1,
                        source = line.strip().replace( '\n', '\\n' )
                    ) )
            except:
                pass

        self.tokens = tokens

#-------------------------------------------------------------------------------
#  'TokenEditor' class:
#-------------------------------------------------------------------------------

class TokenEditor ( BasicEditorFactory ):
    """ Defines an editor class for viewing the tokens of a Python source code
        string.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _TokenEditor

#-- EOF ------------------------------------------------------------------------
