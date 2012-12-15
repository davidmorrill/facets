"""
Defines the abstract ViewElement class that all facet view template items
    (i.e., View, Group, Item, Include) derive from.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import re

from string \
    import rfind

from facets.core.has_facets \
    import HasPrivateFacets

from facets.core.facet_defs \
    import Facet

from facets.core.facet_types \
    import Bool

from ui_facets \
    import Image, ATheme, AnObject, EditorStyle, DockStyle, ExportType, HelpId

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

label_pat  = re.compile( r"^(.*)\[(.*)\](.*)$", re.MULTILINE | re.DOTALL )
label_pat2 = re.compile( r"^(.*){(.*)}(.*)$",   re.MULTILINE | re.DOTALL )

#-------------------------------------------------------------------------------
#  'ViewElement' class (abstract):
#-------------------------------------------------------------------------------

class ViewElement ( HasPrivateFacets ):
    """ An element of a view.
    """

    #-- Public Methods ---------------------------------------------------------

    def replace_include ( self, view_elements ):
        """ Searches the current object's **content** attribute for objects that
            have an **id** attribute, and replaces each one with an Include
            object with the same **id** value, and puts the replaced object into
            the specified ViewElements object.

            Parameters
            ----------
            view_elements : ViewElements object
                Object containing Group, Item, and Include objects
        """
        pass # Normally overridden in a subclass


    def is_includable ( self ):
        """ Returns whether the object is replacable by an Include object.
        """
        return False # Normally overridden in a subclass


    def _repr_format ( self, content, *options ):
        """ Returns a "pretty print" version of the object.
        """
        result  = [ ]
        items   = ',\n'.join( [ item.__repr__() for item in content ] )
        if len( items ) > 0:
            result.append( items )

        options = self._repr_options( *options )
        if options is not None:
            result.append( options )

        content = ',\n'.join( result )
        if len( content ) == 0:
            return self.__class__.__name__ + '()'

        return '%s(\n%s\n)' % (
               self.__class__.__name__, self._indent( content ) )


    def _repr_options ( self, *names ):
        """ Returns a 'pretty print' version of a list of facets.
        """
        result = []
        for name in names:
            value = getattr( self, name )
            if value != self.facet( name ).default_value_for( self, name ):
                result.append( ( name, repr( value ) ) )

        if len( result ) > 0:
            n = max( [ len( name ) for name, value in result ] )

            return ',\n'.join( [ '%s = %s' % ( name.ljust( n ), value )
                                 for name, value in result ] )

        return None


    def _indent ( self, string, indent = '    ' ):
        """ Indents each line in a specified string by 4 spaces.
        """
        return '\n'.join( [ indent + s for s in string.split( '\n' ) ] )

#-------------------------------------------------------------------------------
#  'DefaultViewElement' class:
#-------------------------------------------------------------------------------

class DefaultViewElement ( ViewElement ):
    """ A view element that can be used as a default value for facets whose
        value is a view element.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The default context object to edit:
    object = AnObject

    # The default editor style to use:
    style = EditorStyle

    # The default dock style to use:
    dock = DockStyle

    # The default notebook tab image to use:
    image = Image

    # The category of elements dragged out of the view:
    export = ExportType

    # Should labels be added to items in a group?
    show_labels = Bool( True )

    # The default theme to use for a contained item:
    item_theme = ATheme

    # The default theme to use for a contained item's label:
    label_theme = ATheme

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# The container facet used by ViewSubElements:
Container = Facet( DefaultViewElement(), ViewElement )

#-------------------------------------------------------------------------------
#  'ViewSubElement' class (abstract):
#-------------------------------------------------------------------------------

class ViewSubElement ( ViewElement ):
    """ Abstract class representing elements that can be contained in a view.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The object this ViewSubElement is contained in; must be a ViewElement.
    container = Container

    # External help context identifier:
    help_id = HelpId

    #-- Private Methods --------------------------------------------------------

    def _split ( self, name, value, char, finder, assign, result ):
        """ Splits a string at a specified character.
        """
        col = finder( value, char )
        if col < 0:
            return value

        items = (value[ : col ].strip(), value[ col + 1: ].strip())
        if items[ assign ] != '':
            setattr( self, name, items[ assign ] )

        return items[ result ]


    def _option ( self, string, option, name, value ):
        """ Sets a object facet if a specified option string is found.
        """
        col = string.find( option )
        if col >= 0:
            string = string[ : col ] + string[ col + len( option ): ]
            setattr( self, name, value )

        return string


    def _parse_style ( self, value ):
        """ Parses any of the one-character forms of the **style** facet.
        """
        value = self._option( value, '$', 'style', 'simple' )
        value = self._option( value, '@', 'style', 'custom' )
        value = self._option( value, '*', 'style', 'text' )
        value = self._option( value, '~', 'style', 'readonly' )
        value = self._split( 'style',  value, ';', rfind, 1, 0 )

        return value


    def _parse_label ( self, value ):
        """ Parses a '[label]' value from the string definition.
        """
        match = label_pat.match( value )
        if match is not None:
            self._parsed_label()
        else:
            match = label_pat2.match( value )

        empty = False
        if match is not None:
            self.label = match.group( 2 ).strip()
            empty      = (self.label == '')
            value      = match.group( 1 ) + match.group( 3 )

        return ( value, empty )


    def _parsed_label ( self ):
        """ Handles a label being found in the string definition.
        """
        pass


    def _repr_value ( self, value, prefix = '', suffix = '', ignore = '' ):
        """ Returns a "pretty print" version of a specified Item facet value.
        """
        if value == ignore:
            return ''

        return '%s%s%s' % ( prefix, value, suffix )

#-- EOF ------------------------------------------------------------------------