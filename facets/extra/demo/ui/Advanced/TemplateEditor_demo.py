"""
# TemplateEditor Demo #

This example demonstrates the use of the **TemplateEditor**, an editor which
allows the user to create a string using a template.

The **TemplateEditor** has a ***template*** facet which allows you to specify
the template used for the string being edited by the editor. The value can be:

- A string containing a template definition.
- The name of a text file containing a template definition.
- A name of the form: *@template_file*, where *template_file* is a standard
  template located in the Facets *templates* subdirectory.

For the demo, the initial template is specified as the value of the
**TemplateEditorDemo** object's *template* facet. The initial template provides
a simple example of creating a Facets compatible module by
*filling in the blanks*.

You can fill in the template using the **TemplateEditor** located in the top
part of the view. The editor uses a tabular display organized into *sections*
(the dark colored lines) containing one or more *value* entries (the
lighter-colored lines).

Click on any of the white fields located in the *Value* column and type in a new
value. As you type, you will see the updated template value appear in the
*Results* tab in the bottom part of the view. This view displays the string the
**TemplateEditor** is editing.

You can click the *X* icon just to the left of any filled-in *Value* column
field to reset the value back to its default.

The fields under the *Facet Definitions* section are *repeating* fields. Any
time you type in a non-default value, the editor automatically creates a new set
of values at the end of the section, allowing you to create as many copies of
the template section as you need. Consecutive repeating groups use alternating
background colors to help make each group visually distinct.

You can delete any group of filled-in repeating fields by clicking the *X* icon
located in the leftmost column of the view. All fields in the repeating group
will be deleted at the same time.

You can close and open a section by clicking the *triangle* icon in the
leftmost column of a section header. In the demo, the *Facets Definition*
section is also a *conditional* section and can be enabled or disabled by
clicking the *checkmark* icon in the section's *C* column. When disabled, the
contents of the section do not appear in the template's generated value.

You can also view (and modify) the template controlling the
**TemplateEditor** using the *Template* tab in the bottom part of the view. You
can use it to gain a better understanding of how a template is constructed.

Feel free to make changes to the contents of the *Template* tab and watch the
**TemplateEditor** and *Results* tab update appropriatetely. The
**TemplateEditor** is designed to be forgiving, so even if you make a syntax
error, the editor will try to make some sense out of what you have typed.

A template is normal test intermixed with two types of template specific data:

- *Sections*
- *Values*

A *section* has the form:

    '[[' ['(' [*name*] ['*' | '+' | '-' | '<' | '>']* ')' [*content*] ']]'

where:

- *name* is the name of the section and appears in the *Description* column of
  the **TemplateEditor**, unless *name* is omitted, in which case the section
  header is not displayed.

- The *name* can be followed by zero, one or more modifier characters:

  - *\**: The section is *optional*. If none of the *values* contained in the
    section have non-default values, the entire section is omitted.

  - *+*: The section is *repeated*. Each time any of the *values* in the section
    is assigned a non-default default, a new set of *values* with default values
    is added to the end of the section. This can be used to allow the user to
    enter lists of values without knowing in advance how many values will be
    entered.

  - *-*: The section is initially *closed*. Normally a section is initially
    displayed in the open state. The user can click the leftmost column of the
    section header to open or close its contents.

  - *<*: The section is initially *disabled*. A disabled section does not
    generate any content in the result. The user can enable the section by
    clicking the *checkmark* icon in the section's header.

  - *>*: The section is initially *enabled*. An enabled section adds its content
    to the generated result. The user can disable the section by clicking the
    *checkmark* icon in the section header. Note that a section which is not
    explicitly enabled or disabled is not conditional at all, and its contents
    will always appear in the template results. In this case, no *checkmark*
    icon appears in the section's header.

- The *content* of the section is what the section adds to the generated
  template result, and can be a mixture of regular text, nested *sections* and
  *values*.

A *value* has the form:

    '{{' [*name*] ['^' | '!']* [';' *description*] ['=' *value*] '}}'

where:

 - *name* is the name of the value.

 - *description* is the description of the value that appears in the
   *Description* column of the **TemplateEditor**. If the description is
   omitted, the *name* is used as the description. If neither *name* nor
   *description* is specified, *Value* is used as the *name* and *description*.

 - *value* is the default value. If omitted, the empty string is used as the
   default value.

 - If *name* is followed by a *^* character, a popup editor will be used to edit
   the value when the user clicks on the value's *Description* column entry.
   This can be used to edit long values, or values which can contain carriage
   returns.

 - If *name* is followed by a *!* character, then the value is a *definition*,
   and will not generate any content in the template. This is usually used to
   control the order in which values appear in the **TemplateEditor**, by
   placing the definition of various values at the beginning of the section in
   the order they should appear in the **TemplateEditor**, and then adding the
   actual variable references (without the *!* character) at other locations
   within the section body.

Other points to take note of:

- If you need to enter *[[*, *]]*, *{{* or *}}* sequences into a template
  without having them treated as part of a *section* or *value*, insert a *\*
  character between the first and second character of the sequence (e.g. *[\[*).

- Variable definitions are *scoped*. A variable defined in one section is
  available in all the sections it contains, including all nested sections.

- Variables are listed in the section they first appear in and in the order they
  appear within the template. If you want variables to appear in a certain
  order, place them in the correct order at the beginning of the section. If
  necessary, be sure to add the *!* character to the variable name to indicate
  that it is a definition rather than a reference.

- You can redefine a variable in a nested section by using the *!* character at
  the end of the variable name to indicate that it is a definition. The
  redefined variable will appear in the new section as well as the parent
  section.

- The first definition or use of a variable defines it. All subsequent
  occurrences simply refer to the value of the original variable. This allows
  you to use the value of a variable at multiple locations within a template.

- If you want a variable that can only have a fixed set of values, you can
  create an *enumeration* by writing the variable value as a string of the form:
  '||' *name* [':' *value*] '||' *name* [':'*value*] ... ['||'], where each
  *name* will appear in the enumeration drop-down list within the
  **TemplateEditor**, and each *value* will be assigned as the variable value
  when the user selects the associated *name* from the drop-down list. If the
  *name* and *value* are the same, only the *name* needs to be specified. For
  example: *{{Visible?=||True||False}}* and *{{Visible?=||True:1||False:0}}*
  both define valid enumerations. Note that white space should not be inserted
  anywhere in the enumeration definition unless you want it to appear in the
  template result or drop-down list. Also, the first item in the enumeration
  list is used as the default value for the variable.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Code, View, VSplit, Tabbed, UItem, TemplateEditor, \
           SyncValue

#-- The Demo Template ----------------------------------------------------------

DemoTemplate = '''
[[(Module)
{{Class name!=MyClass}}
{{Base class name!=HasFacets}}
"""
{{Comment^;Module and class comment=Comment goes here...}}
"""
[[(Include facets license<)

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------
]]
#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \\
    import {{Base class name}}

#-------------------------------------------------------------------------------
#  '{{Class name}}' class:
#-------------------------------------------------------------------------------

class {{Class name}} ( {{Base class name}} ):
    """ {{Comment}}
    """

[[(Include facets definitions*<)
    #-- Facet Definitions ------------------------------------------------------[[(+*)
{{Facet name!}}
{{Facet type!}}
{{FComment!;Comment=Describe the facet here...}}
[[(*)\

    # {{FComment}}:]][[\
    {{Facet name=?}} = {{Facet type=Str}}]]]]

]]
[[(Include view definitions<)
    #-- Facet View Definitions -------------------------------------------------

    view = View(
    )

]]
[[(Include facet default values*<)
    #-- Facet Default Values ---------------------------------------------------
[[(+*){{Facet name!=?}}

    def _{{Facet name}}_default ( self ):
        """ Returns the default value for the '{{Facet name}}' facet.
        """
        return None

]]]]
[[(Include facet property implementations*<)
    #-- Property Implementations -----------------------------------------------
[[(+*)
{{Facet name!=?}}
{{Property depends on!=?}}

[[(*)
    @property_depends_on( '{{Property depends on}}' )
]]
[[
    def _get_{{Facet name}} ( self ):
        """ Returns the property value for the '{{Facet name}}' facet.
        """
        return None

]]]]]]
[[(Include facet event handlers*<)
    #-- Facet Event Handlers ---------------------------------------------------
[[(+*)
{{Facet name!=?}}

    def _{{Facet name}}_set ( self ):
        """ Handles the '{{Facet name}}' facet being changed.
        """
        pass

]]]]
[[(Include public methods*<)
    #-- Public Methods ---------------------------------------------------------
[[(+*)
{{Method name!=?}}
{{Method arguments!=?}}
{{Method comment^!=Returns ...}}

    def {{Method name}} ( self[[(*), {{Method arguments}}]] ):[[(*)\
        """ {{Method comment}}
        """]]
        pass

]]]]
[[(Include private methods*<)
    #-- Private Methods --------------------------------------------------------
[[(+*)
{{Method name!=?}}
{{Method arguments!=?}}
{{Method comment^!=Returns ...}}

    def _{{Method name}} ( self[[(*), {{Method arguments}}]] ):[[(*)\
        """ {{Method comment}}
        """]]
        pass

]]]]
[[(Include test code<)
#-- Allow class to be used with demo framework or view tester tool -------------

demo = {{Class name}}

#-- Run the test case (if invoked from the command line) -----------------------

if __name__ == '__main__':
    {{Class name}}().edit_facets()

]]#-- EOF ------------------------------------------------------------------------]]
'''[1:-1]

#-- TemplateEditorDemo class ---------------------------------------------------

class TemplateEditorDemo ( HasFacets ):

    result   = Code
    template = Code( DemoTemplate )

    def default_facets_view ( self ):
        return View(
            VSplit(
                UItem( 'result',
                       editor = TemplateEditor(
                           template = SyncValue( self, 'template' )
                       ),
                       height = 300
                ),
                Tabbed(
                    UItem( 'result', style = 'readonly' ),
                    UItem( 'template' )
                )
            ),
            width  = 0.5,
            height = 0.5
        )

#-- Create the demo ------------------------------------------------------------

demo = TemplateEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
