"""
Defines the ResultItem class used by the VIP Shell to represent a result
returned by evaluating a Python expression.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from types \
    import NoneType

from facets.api \
    import HasFacets, HasPrivateFacets, Any, List, Str, Property, Theme, View, \
           VGroup, Item, UItem, ValueEditor

from facets.core.facet_base \
    import not_event

from facets.ui.graphics_text \
    import color_tag_for

from facets.ui.menu \
    import Action

from facets.ui.editors.set_editor \
    import SetEditor

from facets.ui.vip_shell.helper \
    import remove_color, source_files_for

from facets.ui.vip_shell.tags.api \
    import ValueTag

from shell_item \
    import ShellItem

from view_item \
    import ViewItem

from generated_item \
    import GeneratedItem

try:
    from numpy \
        import ndarray
except:
    ndarray = type( None )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Extra space to add for each level of indenting:
IndentLevel = '   '

# Maximum level of indenting allowed (to prevent recursion):
MaxIndent = 3 * len( IndentLevel )

# The list of directly convertible simple types:
SimpleTypes    = ( int, float, long, bool, NoneType, ShellItem )
AllSimpleTypes = SimpleTypes + ( basestring, list, tuple, set, dict )

#-------------------------------------------------------------------------------
#  'ResultItem' class:
#-------------------------------------------------------------------------------

class ResultItem ( GeneratedItem ):
    """ The result produced by evaluating a command.
    """

    #-- Facet Definitions ------------------------------------------------------

    type       = 'result'
    icon       = '@facets:shell_result'
    color_code = '\x002'

    # An optional label to add to the result:
    label = Str

    # The DisplayAttributes instance for the item (if it is an object instance):
    display_attributes = Any # Instance( DisplayAttributes )

    #-- Facet View Definitions -------------------------------------------------

    value_view = View(
        Item( 'item',
              show_label = False,
              editor     = ValueEditor()
        )
    )

    #-- Default Facet Values ---------------------------------------------------

    def _actions_default ( self ):
        actions = [
            Action( image   = '@icons:wireframe?L31',
                    tooltip = 'Show the complete structure of the item',
                    action  = 'item.show_value()' ),
        ]

        item = self.item
        if source_files_for( item ):
            actions.append(
                Action( image   = '@icons2:Link?H66l11S38|L75',
                        tooltip = 'Show the Python source files for the item',
                        action  = 'item.show_implementation()' ),
            )

        if isinstance( item, HasFacets ):
            actions.append(
                Action( image   = '@icons2:Application_1',
                        tooltip = 'Display the default view for the item',
                        action  = 'item.show_view()' )
            )

        if self.is_object( item ):
            actions.append(
                Action( image   = '@facets:shell_view',
                        tooltip = 'Select the object facets to display',
                        action  = 'item.select_attributes()' )
            )

        return actions

    #-- ShellItem Method Overrides ---------------------------------------------

    def initialized ( self ):
        """ Called when the shell item has been fully initialized.
        """
        super( ResultItem, self ).initialized()

        self._set_listeners()


    def dispose ( self ):
        """ Disposes of the item when it is no longer needed.
        """
        self._set_listeners( remove = True )

    #-- Public Methods ---------------------------------------------------------

    def text_value_for_0 ( self ):
        """ Returns the text to display for level of detail 0.
        """
        value   = self.str( self.item )
        lines   = value.split( '\n' )
        display = self.lookup( 'display' )
        if len( lines ) <= 1:
            return display( value )

        is_object = self.is_object( self.item )
        text      = ''
        len_text  = 0
        lens      = [ ( 0, 0 ) ]
        for line in lines:
            line = line.strip()
            if is_object:
                line = ' '.join( [ x.strip() for x in line.split( ' ', 1 ) ] )

            len_line = len( remove_color( line ) )
            if (len_text + len_line) > 90:
                break

            if len_text > 0:
                text     += ' '
                len_text += 1

            text     += line
            len_text += len_line
            lens.insert( 0, ( len_text, len( text ) ) )
        else:
            return display( text )

        for len1, len2 in lens:
            if len1 <= 70:
                return display( '%s  \x00A[...%d lines...]\x002' %
                                ( text[:len2], len( lines ) ) )


    def str ( self, item ):
        """ Returns the string value of *item*.
        """
        label = ''
        if self.label != '':
            label = '\x00C%s\x002: ' % self.label

        return (label + self.as_str( item ))


    def execute ( self ):
        """ Makes this result the current shell value.
        """
        self.shell.lock_result( self.item )


    def key_a ( self, event ):
        """ Select the object attributes to display.

            The [[a]] key displays a popup dialog that allows selecting which
            object attributes are displayed and in what order. Click on an item
            in the popup dialog to toggle its visibility. Drag the icon on the
            right side of an item up or down to change its display order.
        """
        if ((not isinstance( self.item, AllSimpleTypes)) and
            self.is_object( self.item )):
            self.select_attributes()


    def key_i ( self, event ):
        """ Display the implementation source files of the result.

            The [[i]] key attempts to locate and display Python source file
            shell items for the classes used to implement the value for the
            result item.
        """
        self.show_implementation()


    def show_implementation ( self ):
        """ Display the implementation source files of the result.
        """
        self.shell.do_command( '/li __[%d]' % self.id, self, False )


    def show_value ( self ):
        """ Display the complete structure of the item using the ValueEditor.
        """
        self.shell.add_item_for(
            self,
            self.shell.history_item_for(
                ViewItem, self, view = 'value_view', lod = 1
            )
        )


    def show_view ( self ):
        """ Displays the default Facets view for the item.
        """
        item = self.item
        if isinstance( item, HasFacets ):
            item.edit_facets()


    def select_attributes ( self ):
        """ Displays a popup dialog that allows the user to select which item
            object attributes are displayed.
        """
        self.display_attributes.edit_facets()

    #-- Conversion Methods -----------------------------------------------------

    def as_str ( self, item, indent = '', name = '', is_array = False ):
        """ Returns the string value of *item*.
        """
        if indent == '':
            del self.tags[:]

        if isinstance( item, basestring ):
            return self.as_string( item, indent )

        if isinstance( item, SimpleTypes ):
            return ('%s\x00F%s\x002' % ( indent, repr( item ) ))

        if (isinstance( item, list ) or
            (is_array and isinstance( item, ndarray ))):
            return self.as_list( item, indent, name = name )

        if isinstance( item, tuple ):
            return self.as_list( item, indent, '(', ')', name )

        if isinstance( item, set ):
            return self.as_list( item, indent, 'set( [', '] )', name )

        if isinstance( item, ndarray ):
            return self.as_list(item, indent, 'array( [', '] )', name )

        if isinstance( item, dict ):
            return self.as_dict( item, indent, name )

        if self.is_object( item ):
            return self.as_object( item, indent, name )

        return (indent + repr( item ))


    def as_string ( self, item, indent, show_length = True ):
        """ Returns the string *item* pretty-printed as a string.
        """
        n = len( item )
        if (self.lod == 0) or (len( indent ) > 0):
            if n > 100:
                item = item[:50] + item[-50:]

            value = repr( item )
            if len( value ) <= 82:
                return ('%s\x00F%s\x002' % ( indent, value ))

            return ('%s\x00F%s \x00A...\x00F %s  \x00A[%d]\x002' % ( indent,
                    value[:36], value[-36:], n ))

        if n > 100000:
            return ('%s\n\x00A[...omitted data...]\x002\n%s  \x00A[%d]\x002' % (
                    self.as_string( item[:50000],  indent, False ),
                    self.as_string( item[-50000:], indent, False ),
                    n ))

        value = repr( item )
        if len( value ) <= 82:
            return ('%s\x00F%s\x002' % ( indent, value ))

        lines  = [ '\x00F%s\x002' % value[ i: i + 80 ]
                   for i in xrange( 1, len( value ), 80 ) ]
        result = "\x00F'%s" % (('\n '.join( lines ))[2:])
        if show_length:
            result += ('  \x00A[%d]\x002' % n)

        return result


    def as_list ( self, item, indent, prefix = '[', suffix = ']',
                                      name   = '<list>' ):
        """ Returns the list *item* pretty-printed as a string.
        """
        n = len( item )
        if n == 0:
            return '%s\x002%s%s' % ( indent, prefix, suffix )

        if len( indent ) >= MaxIndent:
            return ('%s\x002%s \x00A...%d item%s... \x002%s' %
                    ( indent, prefix, n, 's'[ (n == 1): ], suffix ))

        next_indent = indent + IndentLevel
        max_items   = self.shell.max_items
        is_array    = prefix.startswith( 'array' )
        if (max_items == 0) or (n <= max_items):
            result = [ self.as_str( element, next_indent,
                                    '%s[%d]' % ( name, i ), is_array )
                       for i, element in enumerate( item ) ]

            # If the result is short enough, return it formatted for single line
            # display:
            length = reduce( lambda x, y: x + len( y ), result, 0 )
            if (length - (n * (len( next_indent ) + 2))) <= 50:
                return ('%s\x002%s %s \x002%s' % ( indent, prefix,
                        ', '.join( [ item.strip() for item in result ] ),
                        suffix ))
        else:
            n1     = (max_items + 1) / 2
            n2     = n - max_items
            part1  = [ self.as_str( item[ i ], next_indent,
                                    '%s[%d]' % ( name, i ), is_array )
                       for i in xrange( n1 ) ]
            part2  = [ self.as_str( item[ i ], next_indent,
                                    '%s[%d]' % ( name, i ), is_array )
                       for i in xrange( n - (max_items - n1), n ) ]
            result = [
                ',\n'.join( part1 ),
                (('%s\x00A[...%d item%s omitted...]\x002\n' %
                 ( next_indent, n2, 's'[ (n2 == 1): ] )) +
                 ',\n'.join( part2 )).rstrip()
            ]

        return ('%s\x002%s\n%s\n%s\x002%s' %
                ( indent, prefix, ',\n'.join( result ), indent, suffix ))


    def as_dict ( self, item, indent, name = '<dict>' ):
        """ Returns the dictionary *item* pretty_printed as a string.
        """
        n = len( item )
        if n == 0:
            return '%s\x002{}' % indent

        if len( indent ) >= MaxIndent:
            return ('%s\x002{ \x00A...%d item%s... \x002}' %
                    ( indent, n, 's'[ (n == 1): ] ))

        items = item.items()
        try:
            items.sort( lambda l, r: cmp( l[0], r[0] ) )
        except:
            pass

        next_indent   = indent + IndentLevel
        nested_indent = next_indent + IndentLevel
        max_items     = self.shell.max_items

        def formatter ( key, value ):
            return ('%s%s: %s' % (
                next_indent,
                self.as_str( key,   nested_indent ).strip(),
                self.as_str( value, nested_indent,
                            '%s[%s]' % ( name, key ) ).strip()
            ))

        if (max_items == 0) or (n <= max_items):
            result = [ formatter( *items[ i ] ) for i in xrange( n ) ]
        else:
            n1     = (max_items + 1) / 2
            n2     = n - max_items
            part1  = [ formatter( *items[ i ] )
                       for i in xrange( n1 ) ]
            part2  = [ formatter( *items[ i ] )
                       for i in xrange( n - (max_items - n1), n ) ]
            result = [
                ',\n'.join( part1 ),
                (('%s\x00A[...%d item%s omitted...]\x002\n' %
                 ( next_indent, n2, 's'[ (n2 == 1): ] )) +
                 ',\n'.join( part2 )).rstrip()
            ]

        return ('%s\x002{\n%s\n%s\x002}' %
                ( indent, ',\n'.join( result ), indent ))


    def as_object ( self, item, indent, name = '<object>' ):
        """ Returns the 'object' *item* pretty-printed as a string.
        """
        if indent != '':
            cc = color_tag_for( 'B', self.tags )
            self.tags.append( ValueTag( label = name, value = item ) )

            return ('%s%s%s\x002( \x00A@0x%X\x002 )' %
                    ( indent, cc, item.__class__.__name__, id( item ) ))

        da    = self.display_attributes
        names = da.names
        if (len( names ) == 1) and (names[0] is None):
            da.names = da.all_names = names = sorted(
                [ name for name in item.__dict__.iterkeys() ]
            )

        result      = []
        next_indent = indent + IndentLevel
        max_len     = -(reduce( lambda x, y: max( x, len( y ) ), names, 0 ) + 1)
        for name in names:
            try:
                value = getattr( item, name )
            except:
                # If we can't retrieve the value, then just ignore it:
                continue

            result.append( "%s\x00C%*s\x002= %s" % (
                next_indent, max_len, name,
                self.as_str( value, next_indent, name ).strip()
            ) )

        return ('%s\x00B%s\x002( \x00A@0x%X\x002,\n%s\n%s)' %
                ( indent, item.__class__.__name__, id( item ),
                  ',\n'.join( result ), indent ))


    def is_object ( self, value ):
        """ Returns **True** if *value* is an object whose structure can be
            displayed, and **False** otherwise.
        """
        return (isinstance( value, object ) and hasattr( value, '__class__'))

    #-- Facet Default Values ---------------------------------------------------

    def _display_attributes_default ( self ):
        return DisplayAttributes.attributes_for( self.item )

    #-- Facet Event Handlers ---------------------------------------------------

    def _label_set ( self ):
        """ Handles the 'label' facet being changed by updating the item's
            content value.
        """
        self.update = True


    def _hidden_set ( self ):
        """ Handles the 'hidden' facet being changed.
        """
        self._set_listeners( remove = self.hidden )
        if not self.hidden:
            self._label_set()

        super( ResultItem, self )._hidden_set()

    #-- Private Methods --------------------------------------------------------

    def _set_listeners ( self, remove = False ):
        """ Adds/removes listeners based on the specified *remove* boolean and
            the item's associated object.
        """
        item = self.item
        if self.is_object( item ):
            self.display_attributes.on_facet_set( self._label_set, 'names',
                                                  remove = remove )
            if isinstance( item, HasFacets ):
                item.on_facet_set( self._label_set, remove = remove )

#-------------------------------------------------------------------------------
#  'DisplayAttributes' class:
#-------------------------------------------------------------------------------

class DisplayAttributes ( HasPrivateFacets ):
    """ Keeps track of the attributes that a user wants to display for a
        specific 'object' subclass.
    """

    #-- Class Values -----------------------------------------------------------

    # A cache of all active DisplayAttributes instances:
    cache = {}

    #-- Facet Definitions ------------------------------------------------------

    # The 'object' subclass this item is for:
    subclass = Any

    # The list of attribute names the user wants to display for this subclass:
    names = List # ( Str )

    # The list of all possible attribute names for the item's subclass:
    all_names = List # ( Str )

    # The Facets database key the attribute names are saved under:
    db_key = Property

    #-- Facet View Definitions -------------------------------------------------

    def default_facets_view ( self ):
        return View(
            VGroup(
                UItem( 'names',
                       editor = SetEditor(
                           values   = self.all_names,
                           ordering = 'user'
                       )
                ),
                label       = 'Object attributes',
                group_theme = Theme( '@xform:btd?L26~H53L32S16|l57',
                                     content = -1, label = ( -5, 0 ) )
            ),
            width  = 180,
            height = 0.5,
            kind   = 'popout'
        )

    #-- Facet Default Values ---------------------------------------------------

    def _names_default ( self ):
        return self.facet_db_get( self.db_key, self.all_names )


    def _all_names_default ( self ):
        if not issubclass( self.subclass, HasFacets ):
            return [ None ]

        return sorted( self.subclass.class_facet_names( type = not_event ) )

    #-- Property Implementations -----------------------------------------------

    def _get_db_key ( self ):
        return ('DisplayFacets:%s.%s' %
                ( self.subclass.__module__, self.subclass.__name__ ))

    #-- Facet Event Handlers ---------------------------------------------------

    def _names_set ( self ):
        """ Handles the 'names' facet being changed.
        """
        self.facet_db_set( self.db_key, self.names[:] )

    #-- Class Methods ----------------------------------------------------------

    @classmethod
    def attributes_for ( cls, object ):
        """ Returns the DisplayAttributes instance to use for the object
            specified by *object*.
        """
        subclass = object.__class__
        result   = cls.cache.get( subclass )
        if result is None:
            result                = cls( subclass = subclass )
            cls.cache[ subclass ] = result

        return result

#-- EOF ------------------------------------------------------------------------
