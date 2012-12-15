"""
Demonstrates the use of the <b>TemplateEditor</b>, an editor which allows the
user to create a string using a template.

The <b>TemplateEditor</b> has a <b><i>template</i></b> facet which allows you
to specify the template used for the string being edited by the editor. The
value can be:
 - A string containing a template definition.
 - The name of a text file containing a template definition.
 - A name of the form: <i>@template_file</i>, where <i>template_file</i> is a
   standard template located in the Facets <i>templates</i> subdirectory.

For the demo, the initial template is specified as the value of the
<b>TemplateEditorDemo</b> object's <b><i>template</i></b> facet. The initial
template provides a simple example of creating a Facets compatible module
by <i>filling in the blanks</i>.

You can fill in the template using the <b>TemplateEditor</b> located in the top
part of the view. The editor uses a tabular display organized into
<i>sections</i> (the dark colored lines) containing one or more <i>value</i>
entries (the lighter-colored lines).

Click on any of the white fields located in the <b><i>Value</i></b> column and
type in a new value. As you type, you will see the updated template value appear
in the <b><i>Results</i></b> tab in the bottom part of the view. This view
displays the string the <b>TemplateEditor</b> is editing.

You can click the <b>X</b> icon just to the left of any filled-in
<b><i>Value</i></b> column field to reset the value back to its default.

The fields under the <b><i>Facet Definitions</b></i> section are
<i>repeating</i> fields. Any time you type in a non-default value, the editor
automatically creates a new set of values at the end of the section, allowing
you to create as many copies of the template section as you need. Consecutive
repeating groups use alternating background colors to help make each group
visually distinct.

You can delete any group of filled-in repeating fields by clicking the <b>X</b>
icon located in the leftmost column of the view. All fields in the repeating
group will be deleted at the same time.

You can close and open a section by clicking the <i>triangle</i> icon in the
leftmost column of a section header. In the demo, the <b><i>Facets
Definition</i></b> section is also a <i>conditional</i> section and can be
enabled or disabled by clicking the <i>checkmark</i> icon in the section's
<b><i>C</i></b> column. When disabled, the contents of the section do not
appear in the template's generated value.

You can also view (and modify) the template controlling the
<b>TemplateEditor</b> using the <b><i>Template</i></b> tab in the bottom part
of the view. You can use it to gain a better understanding of how a template is
constructed.

Feel free to make changes to the contents of the <b><i>Template</i></b> tab and
watch the <b>TemplateEditor</b> and <b><i>Results</i></b> tab update
appropriatetely. The <b>TemplateEditor</b> is designed to be forgiving, so even
if you make a syntax error, the editor will try to make some sense out of what
you have typed.

A template is normal test intermixed with two types of template specific data:
 - <b>Sections</b>
 - <b>Values</b>

A <b>section</b> has the form:

  '[[' ['(' [<i>name</i>] ['*' | '+' | '-' | '<' | '>']* ')' [<i>content</i>] ']]'

where:
 - <b><i>name</i></b> is the name of the section and appears in the
   <b><i>Description</i></b> column of the <b>TemplateEditor</b>, unless
   <b><i>name</i></b> is omitted, in which case the section header is not
   displayed.
 - The <b><i>name</i></b> can be followed by zero, one or more modifier
   characters:
   - <b><i>*</i></b>: The section is <i>optional</i>. If none of the
     <b><i>values</i></b> contained in the section have non-default values, the
     entire section is omitted.
   - <b><i>+</i></b>: The section is <i>repeated</i>. Each time any of the
     <b><i>values</i></b> in the section is assigned a non-default default, a
     new set of <b><i>values</i></b> with default values is added to the end of
     the section. This can be used to allow the user to enter lists of values
     without knowing in advance how many values will be entered.
   - <b><i>-</i></b>: The section is initially <i>closed</i>. Normally a section
     is initially displayed in the open state. The user can click the leftmost
     column of the section header to open or close its contents.
   - <b><i><</i></b>: The section is initially <i>disabled</i>. A disabled
     section does not generate any content in the result. The user can enable
     the section by clicking the <i>checkmark</i> icon in the section's header.
   - <b><i>></i></b>: The section is initially <i>enabled</i>. An enabled
     section adds its content to the generated result. The user can disable the
     section by clicking the <i>checkmark</i> icon in the section header. Note
     that a section which is not explicitly enabled or disabled is not
     conditional at all, and its contents will always appear in the template
     results. In this case, no <i>checkmark</i> icon appears in the section's
     header.
 - The <b><i>content</i></b> of the section is what the section adds to the
   generated template result, and can be a mixture of regular text, nested
   <b><i>sections</i></b> and <b><i>values</i></b>.

A <b><i>value</i></b> has the form:

  '{{' [<i>name</i>] ['^' | '!']* [';' <i>description</i>] ['=' <i>value</i>] '}}'

where:
 - <b><i>name</i></b> is the name of the value.
 - <b><i>description</i></b> is the description of the value that appears in the
   <b><i>Description</i></b> column of the <b>TemplateEditor</b>. If the
   description is omitted, the <b><i>name</i></b> is used as the description.
   If neither <b><i>name</i></b> nor <b><i>description</i></b> is specified,
   <i>Value</i> is used as the <b><i>name</i></b> and <b><i>description</i></b>.
 - <b><i>value</i></b> is the default value. If omitted, the empty string is
   used as the default value.
 - If <b><i>name</i></b> is followed by a <i>^</i> character, a popup editor
   will be used to edit the value when the user clicks on the value's
   <b><i>Description</i></b> column entry. This can be used to edit long values,
   or values which can contain carriage returns.
 - If <b><i>name</i></b> is followed by a <i>!</i> character, then the value
   is a <i>definition</i>, and will not generate any content in the template.
   This is usually used to control the order in which values appear in the
   <b>TemplateEditor</b>, by placing the definition of various values at the
   beginning of the section in the order they should appear in the
   <b>TemplateEditor</b>, and then adding the actual variable references
   (without the <i>!</i> character) at other locations within the section body.

Other points to take note of:
 - If you need to enter <i>[[</i>, <i>]]</i>, <i>{{</i> or <i>}}</i> sequences
   into a template without having them treated as part of a
   <b><i>section</i></b> or <b><i>value</i></b>, insert a <i>\</i> character
   between the first and second character of the sequence (e.g. <i>[\[</i>).
 - Variable definitions are <i>scoped</i>. A variable defined in one section is
   available in all the sections it contains, including all nested sections.
 - Variables are listed in the section they first appear in and in the order
   they appear within the template. If you want variables to appear in a
   certain order, place them in the correct order at the beginning of the
   section. If necessary, be sure to add the <i>!</i> character to the variable
   name to indicate that it is a definition rather than a reference.
 - You can redefine a variable in a nested section by using the <i>!</i>
   character at the end of the variable name to indicate that it is a
   definition. The redefined variable will appear in the new section as well
   as the parent section.
 - The first definition or use of a variable defines it. All subsequent
   occurrences simply refer to the value of the original variable. This allows
   you to use the value of a variable at multiple locations within a template.
 - If you want a variable that can only have a fixed set of values, you can
   create an <i>enumeration</i> by writing the variable value as a string of
   the form: '||' <i>name</i> [':' <i>value</i>] '||' <i>name</i> [':'
   <i>value</i>] ... ['||'], where each <i>name</i> will appear in the
   enumeration drop-down list within the <b>TemplateEditor</b>, and each
   <i>value</i> will be assigned as the variable value when the user selects the
   associated <i>name</i> from the drop-down list. If the <i>name</i> and
   <i>value</i> are the same, only the <i>name</i> needs to be specified. For
   example: <b><i>{{Visible?=||True||False}}</i></b> and
   <b><i>{{Visible?=||True:1||False:0}}</i></b> both define valid enumerations.
   Note that white space should not be inserted anywhere in the enumeration
   definition unless you want it to appear in the template result or drop-down
   list. Also, the first item in the enumeration list is used as the default
   value for the variable.
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
