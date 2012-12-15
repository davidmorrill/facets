"""
Facets UI editor for editing the value of a string based upon a specified text
template which allows for variable substitution and repeating sections.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import facets.ui

from os \
    import getcwd, environ

from os.path \
    import isfile, join, splitext, dirname

from time \
    import strftime

from facets.api \
   import HasPrivateFacets, List, Str, Bool, Int, Float, Any, Color, Instance, \
          Property, Event, UIEditor, BasicEditorFactory, View, UItem,          \
          GridEditor, EnumEditor, TextEditor, property_depends_on, on_facet_set

from facets.core.facet_base \
    import read_file

from facets.core.facet_db \
    import facet_db

from facets.ui.grid_adapter \
   import GridAdapter

from facets.ui.pyface.timer.api \
    import do_after

#-------------------------------------------------------------------------------
#  Helper functions:
#-------------------------------------------------------------------------------

def get_date ( ):
    """ Returns today's date as a string.
    """
    return strftime( '%B %d, %Y' )


def get_year ( ):
    """ Returns the current year as a string.
    """
    return strftime( '%Y' )


def get_time ( ):
    """ Returns the current time as a string.
    """
    return strftime( '%I:%M:%S %p' )

#-------------------------------------------------------------------------------
#  Constants:
#-------------------------------------------------------------------------------

# Mapping from substitution variable names to handler functions:
SubstitutionVariables = {
    'DATE': get_date,
    'YEAR': get_year,
    'TIME': get_time,
    'CWD':  getcwd
}

# The facets database key prefix used for global variables:
GlobalVariable = 'facets.ui.editors.template_editor:'

#-------------------------------------------------------------------------------
#  'TemplateValue' class:
#-------------------------------------------------------------------------------

class TemplateValue ( HasPrivateFacets ):
    """ Represents a template variable/value.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The name of the variable:
    name = Str

    # The current value of the variable:
    value = Str

    # The default value for the variable:
    default = Str

    # The (optional) enumeration values:
    enum = Any # ( None or { name: value } )

    # The description of the variable:
    description = Str

    # The group this value is part of:
    group = Int

    # Should the edit for this value pop-up?
    popup = Bool( False )

    # The TemplateSection this value is part of:
    parent = Any # Instance( TemplateSection )

    # Can this variable be deleted?
    can_delete = Bool( False )

    # Event fired when the user wants to delete this item:
    delete = Event

    #-- Public Methods ---------------------------------------------------------

    def clone ( self ):
        """ Returns a clone of this object.
        """
        return self.__class__(
            **self.get( 'name', 'value', 'default', 'description', 'parent' )
        )

    #-- Facet Event Handlers ---------------------------------------------------

    def _name_set ( self, new_name ):
        """ Handles the 'name' facet being changed.
        """
        if new_name[:1] == '$':
            self.value = self.default = facet_db.get(
                GlobalVariable + new_name, ''
            )


    def _value_set ( self, value ):
        """ Handles the 'value' facet being changed.
        """
        if self.name[:1] == '$':
            facet_db.set( GlobalVariable + self.name, value )

#-------------------------------------------------------------------------------
#  'TemplateSection' class:
#-------------------------------------------------------------------------------

class TemplateSection ( HasPrivateFacets ):
    """ Represents a single normal or repeating section within a template.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The template section text (containing string interpolation codes):
    template = Str

    # The name of the section:
    name = Str

    # The list of template values defined within the section:
    values = List # ( TemplateValue )

    # The list of prototype template values (for a repeating section):
    prototypes = List # ( TemplateValue )

    # The list of template values referenced within the section:
    references = List # ( TemplateValue )

    # The list of sections contained within this section:
    sections = List # ( TemplateSection )

    # Are the values in this section visible in the template editor?
    visible = Bool( True )

    # Is this a repeating section:
    repeating = Bool( False )

    # Is this an optional section?
    optional = Bool( False )

    # Is this section conditional?
    conditional = Bool( False )

    # Is this conditional section enabled?
    enabled = Bool( True )

    # The section (if any) this section is contained in:
    parent = Any # Instance( TemplateSection )

    # Event fired when something affecting the section's value changes:
    modified = Event

    # The list of template entries to display in the editor:
    items = Property( List ) # ( Either( TemplateVariable, TemplateSection ) )

     #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'values, visible, enabled, sections:items' )
    def _get_items ( self ):
        items = []
        if self.name != '':
            items.append( self )

        if (self.visible and ((not self.conditional) or self.enabled)):
            items.extend( self.values )

            for section in self.sections:
                items.extend( section.items )

        return items

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'values.value, modified, enabled' )
    def _value_modified ( self ):
        self.parent.modified = True


    @on_facet_set( 'values.value' )
    def _values_modified ( self ):
        """ Handles the user modifying any of the constituent values.
        """
        if self.repeating:
            for tv in self.values[ -len( self.prototypes ): ]:
                if tv.value != tv.default:
                    do_after( 1000, self._add_clones )

                    break


    @on_facet_set( 'values:delete' )
    def _delete_requested ( self, notify ):
        n = len( self.prototypes )
        i = (self.values.index( notify.object ) / n) * n
        del self.values[ i: i + n ]
        self._renumber_groups()

    #-- Public Methods ---------------------------------------------------------

    def definition_of ( self, name, definition = False, create = False ):
        """ Returns the TemplateValue definition for the specified *name*. If
            *create* is True and no definition is found, a new definition is
            created.
        """
        for tv in self.values:
            if name == tv.name:
                return tv

        if not definition:
            parent = self.parent
            if isinstance( parent, TemplateSection ):
                tv = parent.definition_of( name )
                if tv is not None:
                    return tv

            if not create:
                return None

        tv = TemplateValue( name = name, parent = self )
        self.values.append( tv )

        return tv


    def value ( self, context = {} ):
        """ Returns the value of the template, evaluated using the specified
            evaluation *context*.
        """
        if ((self.conditional and (not self.enabled)) or
            (self.optional and self._is_default( context ))):
            return ''

        n = len( self.prototypes )
        if self.repeating and (n > 0):
            return ''.join(
                [ self._evaluate( context, self.values[ i: i + n ] )
                  for i in xrange( 0, max( 1, len( self.values ) - n ), n ) ]
            )

        return self._evaluate( context, self.values )

    #-- Private Methods --------------------------------------------------------

    def _context_for ( self, context, values ):
        """ Returns a clone of *context* containing all of the values defined
            in the specified list of *values*.
        """
        context = context.copy()
        for tv in values:
            context[ tv.name ] = tv.value

        return context


    def _evaluate ( self, context, values ):
        """ Returns the result of evaluating the template for the specified set
            of TemplateValue *values* using the specified evaluation *context*.
        """
        context  = self._context_for( context, values )
        sections = dict( [ ( '+%d' % i, section.value( context ) )
                           for i, section in enumerate( self.sections ) ] )

        context.update( sections )

        return (self.template % context)


    def _is_default ( self, context ):
        """ Returns whether the value of the template is generated using only
            default values for the values in the specified *context*.
        """
        if self.conditional and (not self.enabled):
            return True

        n = len( self.prototypes )
        if self.repeating and (n > 0):
            for i in xrange( 0, max( 1, len( self.values ) - n ), n ):
                if not self._is_default_for( context, self.values[ i: i + n ] ):
                    return False

            return True

        return self._is_default_for( context, self.values )


    def _is_default_for ( self, context, values ):
        """ Returns whether the value of the template is generated using only
            default values for the values in the specified *context*.
        """
        context = self._context_for( context, values )

        for tv in self.references:
            if context[ tv.name ] != tv.default:
                return False

        for section in self.sections:
            if not section._is_default( context ):
                return False

        return True


    def _add_clones ( self ):
        """ Add clones of the prototype values to create a new set of values.
        """
        # Mark the first entry of all of the old sections as deletable:
        values = self.values
        for i in xrange( 0, len( self.values ), len( self.prototypes ) ):
            values[ i ].can_delete = True

        # Add the new clones to the end of the list:
        self.values.extend( [ ptv.clone() for ptv in self.prototypes ] )
        self._renumber_groups()


    def _renumber_groups ( self ):
        """ Renumber all of the groups within a repeating section.
        """
        n = len( self.prototypes )
        for i, tv in enumerate( self.values ):
            tv.group = i / n

#-------------------------------------------------------------------------------
#  'TemplateAdapter' class:
#-------------------------------------------------------------------------------

class TemplateAdapter ( GridAdapter ):

    columns = [
        ( 'X',           'action'      ),
        ( 'Description', 'description' ),
        ( 'C',           'clear'       ),
        ( 'Value',       'value'       ),
    ]

    # Can edit:
    can_edit                       = Bool( False )
    value_can_edit                 = Bool( True  )
    TemplateSection_value_can_edit = Bool( False )

    # Text:
    action_text                    = Str
    clear_text                     = Str
    TemplateSection_value_text     = Str
    TemplateSection_clear_text     = Str

    # Alignment
    action_alignment               = Str( 'center' )
    clear_alignment                = Str( 'center' )

    # Background color:
    TemplateSection_bg_color       = Color( 0x989898 )
    TemplateSection_text_color     = Color( 0xFFFFFF )
    TemplateValue_value_bg_color   = Color( 0xFCFCFC )

    # Width:
    action_width                   = Float( 25 )
    description_width              = Float( 0.50 )
    clear_width                    = Float( 25 )
    value_width                    = Float( 0.50 )

    #-- Computed Values --------------------------------------------------------

    def TemplateSection_description_text ( self ):
        return self.item.name


    def TemplateSection_clear_image ( self ):
        item = self.item
        if not item.conditional:
            return None

        return ('@icons2:OK' if item.enabled else '@icons2:OK?s99')


    def TemplateSection_clear_clicked ( self ):
        item = self.item
        if item.conditional:
            item.enabled = not item.enabled


    def TemplateSection_action_clicked ( self ):
        self.item.visible = not self.item.visible


    def TemplateSection_action_image ( self ):
        item = self.item
        if ((item.conditional and (not item.enabled)) or
            (item.visible and (len( item.items ) == 1))):
            return None

        return ('@icons:open_dark'
                if item.visible and ((not item.conditional) or item.enabled)
                else '@icons:closed_dark')


    def action_clicked ( self ):
        if self.item.can_delete:
            self.item.delete = True


    def TemplateValue_action_image ( self ):
        return ('@icons2:Delete' if self.item.can_delete else None)


    def TemplateValue_clear_image ( self ):
        item = self.item

        return (None if item.value == item.default else '@icons2:Delete')


    def TemplateValue_clear_clicked ( self ):
        self.item.value = self.item.default


    def TemplateValue_description_text ( self ):
        return self.item.description.lstrip( '$' )


    def TemplateValue_value_clicked ( self ):
        return ('popup' if self.item.popup else 'edit')


    def TemplateValue_value_content ( self ):
        enum  = self.item.enum
        value = self.item.value
        if enum is not None:
            return enum[ value ][5:]

        return value


    def TemplateValue_value_editor ( self ):
        enum = self.item.enum
        if enum is None:
            return TextEditor()

        return EnumEditor( values = enum )


    def TemplateValue_bg_color ( self ):
        return (0xEEEEEE if (self.item.group % 2) == 0 else 0xCCCCCC)

#-------------------------------------------------------------------------------
#  '_TemplateEditor' class:
#-------------------------------------------------------------------------------

class _TemplateEditor ( UIEditor ):
    """ Facets UI editor for editing the value of a string based upon a
        specified text template which allows for variable substitution and
        repeating sections.
    """

    #-- Facet Definitions ------------------------------------------------------

    # The parsed version of the factory template:
    template = Instance( TemplateSection )

    # The template items being processed:
    items = Property( List )

    # Event fired when something affecting the template's value changes:
    modified = Event

    #-- Facets View Definitions ------------------------------------------------

    view = View(
        UItem( 'items',
               editor = GridEditor(
                   adapter    = TemplateAdapter,
                   operations = [ 'edit' ],
                   monitor    = 'selected'
               )
        )
    )

    #-- Property Implementations -----------------------------------------------

    @property_depends_on( 'template.items' )
    def _get_items ( self ):
        return self.template.items

    #-- Method Definitions -----------------------------------------------------

    def init_ui ( self, parent ):
        """ Creates the facets UI for the editor.
        """
        self._update_template()

        return self.edit_facets( parent = parent, kind = 'editor' )


    @on_facet_set( 'template, modified' )
    def update_editor ( self ):
        """ Updates the editor when the object facet changes externally to the
            editor.
        """
        template = self.template
        if (template is not None) and (self.ui is not None):
            self.value = template.value()

    #-- Facet Event Handlers ---------------------------------------------------

    @on_facet_set( 'factory:template' )
    def _update_template ( self ):
        """ Handles the factory template being modified.
        """
        self.template = self._template_for()

    #-- Private Methods --------------------------------------------------------

    def _template_for ( self ):
        """ Returns the Template object derived from the current value of the
            factory's 'template' value.
        """
        template = self.factory.template
        if template.find( '{{' ) < 0:
            file_name = template
            if file_name[:1] == '@':
                file_name = join( dirname( facets.ui.__file__ ), 'templates',
                                  splitext( file_name[1:] )[0] + '.tmp' )

            if isfile( file_name ):
                template = read_file( file_name ) or ''

        return self._section_for( template, self )


    def _section_for ( self, body, parent = None,
                       name    = '',   repeating   = False, optional = False,
                       visible = True, conditional = False, enabled  = True ):
        """ Returns the TemplateSection object defined by the specified template
            *body* string, the parent TemplateSection *parent*, the template
            *name*, whether it is a *repeating* or *optional* section, whether
            its contents are initially *visible*, whether it is a *conditional*
            section, and if so, whether or not it is *enabled*.
        """
        section = TemplateSection(
            parent      = parent,
            name        = name,
            repeating   = repeating,
            optional    = optional,
            visible     = visible,
            conditional = conditional,
            enabled     = enabled
        )
        chunks  = []
        current = 0
        last    = len( body )
        while True:
            start = body.find( '[[', current )
            if start < 0:
                break

            if start > current:
                self._chunks_for( body[ current: start ], section, chunks )

            start  += 2
            scan    = start
            nesting = 1
            while nesting > 0:
                end = body.find( ']]', scan )
                if end < 0:
                    end = last

                next = body.find( '[[', scan )
                if (next >= 0) and (next < end):
                    nesting += 1
                    scan     = next + 2
                else:
                    nesting -= 1
                    scan     = end + 2

            current  = end + 2
            current += (body[ current: current + 2 ] == '\n[')
            chunks.append( '%%(+%d)s' % len( section.sections ) )
            section.sections.append(
                self._section_from( body[ start: end ], section )
            )

        remaining = body[ current: ]
        if remaining != '':
            self._chunks_for( remaining, section, chunks )

        section.template = ''.join( chunks ).replace( '{\\{', '{{'
                                           ).replace( '}\\}', '}}' )
        if repeating:
            section.prototypes = [ tv.clone() for tv in section.values ]

        return section


    def _section_from ( self, body, parent ):
        """ Parses a section *body* header and returns the TemplateSection
            object it defines. *Parent* is the parent TemplateSection for the
            new section.
        """
        name     = ''
        optional = repeating = conditional = False
        visible  = enabled   = True
        if body[:1] == '(':
            if body[1:2] == '(':
                body = body[1:]
            else:
                col = body.find( ')' )
                if col >= 0:
                    name = body[ 1: col ]
                    body = body[ col + 1: ]

                    while True:
                        c = name[-1:]
                        if c == '-':
                            visible   = False
                        elif c == '+':
                            repeating = True
                        elif c == '*':
                            optional  = True
                        elif (c == '<') or (c == '>'):
                            conditional = True
                            enabled     = (c == '>')
                        else:
                            break

                        name = name[:-1]

                    visible = visible or (name == '')

        if (body[:1] == '\n') or (body[:2] == '\\\n'):
            body = body[1:]

        return self._section_for( body, parent, name, repeating, optional,
                                  visible, conditional, enabled )


    def _chunks_for ( self, body, parent, chunks ):
        """ Updates the TemplateSection information with all of the value
            references contained in the specified template *body*. The *parent*
            is the parent TemplateSection object. *Values* is a list of all
            TemplateValues defined in the section, and chunks contains the
            pieces of text that will be used to build the final template
            interpolation string.
        """
        body    = body.replace( '[\\[', '[[' ).replace( ']\\]', ']]' )
        current = 0
        last    = len( body )
        while True:
            start = body.find( '{{', current )
            if start < 0:
                break

            chunks.append( body[ current: start ] )
            start += 2
            end    = body.find( '}}', start )
            if end < 0:
                end = last

            chunk = self._value_for( body[ start: end ], parent )
            chunks.append( chunk )
            current  = end + 2
            current += ((chunk == '') and
                        (body[ current: current + 1 ] == '\n'))

        chunks.append( body[ current: ] )


    def _value_for ( self, body, parent ):
        """ Adds the TemplateValue object defined by the *body* string to
            *values* if it is not already defined. Returns the template string
            interpolation value corresponding to the TemplateValue. *Parent*
            is the TemplateSection instance that value belongs to.
        """
        name  = body
        value = description = ''
        col   = body.find( '=' )
        if col >= 0:
            name  = body[ : col ]
            value = body[ col + 1: ]
            col   = name.find( ';' )
            if col >= 0:
                description = name[ col + 1: ]
                name        = name[ : col ]

        popup = definition = False
        while True:
            c = name[-1:]
            if c == '!':
                definition = True
            elif c == '^':
                popup = True
            else:
                break

            name = name[:-1]

        name        = name.strip() or 'Value'
        description = description.strip() or name
        enum        = None

        # Handle the case of a substitution value of the form: $$...$$:
        if value.startswith( '$$' ) and value.endswith( '$$' ):
            variable  = value[2:-2]
            sub_value = SubstitutionVariables.get( variable )
            if sub_value is not None:
                value = sub_value()
            else:
                sub_value = environ.get( value[ 2: -2 ] )
                if sub_value is not None:
                    value = sub_value
        elif value.startswith( '||' ):
            value, enum = self._enum_for( value )

        tv = parent.definition_of( name, definition, True )
        tv.set(
            value       = tv.value       or value,
            default     = tv.default     or value,
            enum        = tv.enum        or enum,
            description = tv.description or description,
            popup       = tv.popup       or popup
        )

        if definition:
            return ''

        parent.references.append( tv )

        return ('%%(%s)s' % name)


    def _enum_for ( self, body ):
        """ Returns the value and enumeration dictionary for a variable whose
            value is the enumeration specified by *body*, which should be a
            string of the form: ||name1:value1||name2:value2||...
        """
        last = len( body )
        if last == 2:
            return ( body, None )

        default = None
        enum    = {}
        current = 2
        count   = 0
        while current < last:
            end = body.find( '||', current )
            if end < 0:
                end = last

            items             = body[ current: end ].split( ':', 1 )
            enum[ items[-1] ] = '%04d:%s' % ( count, items[0] )

            if default is None:
                default = items[-1]

            count  += 1
            current = end + 2

        return ( default, enum )

#-------------------------------------------------------------------------------
#  'TemplateEditor' class:
#-------------------------------------------------------------------------------

class TemplateEditor ( BasicEditorFactory ):

    #-- Facet Definitions ------------------------------------------------------

    # The editor class to be created:
    klass = _TemplateEditor

    # The template (string or file name) to use:
    template = Str( facet_value = True )

#-- EOF ------------------------------------------------------------------------
