"""
A demonstration of KeyBinding, KeyBindings and the KeyBindingEditor.

A KeyBinding represents a mapping from a keyboard key sequence (such as Ctrl-u)
to a named object method which performs some action. A single KeyBinding object
can map either one or two (i.e. a primary and an alternate) key sequences to a
single action.

A KeyBindings object is a collection of KeyBinding objects which represents the
set of keyboard actions a user can perform in some application context.

And finally, a KeyBindingEditor is an editor which allows a user to
interactively change the set of key sequences bound to application actions for
the KeyBinding objects contained in a single KeyBindings object.

Visually, the KeyBindingEditor appears as a list with one entry for each
KeyBinding object in the associated KeyBindings object. Each entry has three
fields:
 - The primary key sequence.
 - The secondary (i.e. alternate) key sequence.
 - A description of the action associated with the binding.

To change a key sequence assignment, click on either the primary or secondary
key sequence field of an entry and then press the key sequence you want to
assign the action to (e.g. Ctrl-Shift-q). The new assignment appears in the
associated key sequence field for the entry. If the key sequence is already
assigned to a different action in the same KeyBindings object, you are prompted
to either continue or cancel the assignment. Continuing with the assignment
removes the key sequence from the original KeyBinding object it was assigned to.

The purpose of these three classes is to provide a simple and flexible means
of supplying custom key bindings for application actions. In many cases, the
user customized KeyBindings object is automatically saved by Facets as part of
the application's persisted state.

In the demo, the view is divided into a CodeEditor at the top, and a
KeyBindingEditor at the bottom. The CodeEditor provides two custom
actions:
 - Uppercasing the current line (initially Ctrl-u).
 - Lowercasing the current line (initially Ctrl-y).

You can use the associated KeyBindingEditor at the bottom of the view to
customize which key sequences invoke these editor actions.

Of course, in a real application the KeyBindingEditor would probably appear in
a separate user preferences dialog, but we have included it directly in the view
for illustrative purposes.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-- Imports --------------------------------------------------------------------

from facets.api \
    import Handler, Code, Int, Constant, Property, View, VGroup, Item, \
           CodeEditor, InstanceEditor

from facets.ui.key_bindings \
    import KeyBindings, KeyBinding

from facets.ui.pyface.timer.api \
    import do_later

#-- KeyBinding Definitions -----------------------------------------------------

DemoBindings = KeyBindings( [
    KeyBinding( binding     = 'Ctrl-u',
                description = 'Upper cases the line the cursor is on',
                method      = 'uppercase_line' ),
    KeyBinding( binding     = 'Ctrl-y',
                description = 'Lower cases the line the cursor is on',
                method      = 'lowercase_line' )
] )

#-- Initial Code to Edit -------------------------------------------------------

SampleCode = """
Now is the time
for all good men
to come to the aid
of their country.
"""[1:-1]

#-- Demo Class -----------------------------------------------------------------

class Demo ( Handler ):

    #-- Facet Definitions ------------------------------------------------------

    # The code being edited:
    code = Code( SampleCode )

    # The list of text lines contained in 'code':
    lines = Property

    # The line the cursor is on currently:
    line = Int

    # A reference to the KeyBindings object:
    bindings = Constant( DemoBindings )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        VGroup(
            Item( 'code',
                  id     = 'code',
                  editor = CodeEditor( line         = 'line',
                                       key_bindings = DemoBindings )
            ),
            Item( 'bindings',
                  style  = 'custom',
                  editor = InstanceEditor()
            ),
            show_labels = False
        ),
        title     = 'KeyBindings Demo',
        id        = 'facets.extra.demo.ui.Advanced.KeyBindings_demo',
        width     = 0.50,
        height    = 0.70,
        resizable = True
    )

    #-- KeyBinding Method Implementations --------------------------------------

    def uppercase_line ( self, info ):
        lines = self.lines
        lines[ self.line ] = lines[ self.line ].upper()
        self.lines = lines

    def lowercase_line ( self, info ):
        lines = self.lines
        lines[ self.line ] = lines[ self.line ].lower()
        self.lines = lines

    #-- Property Implementations -----------------------------------------------

    def _get_lines ( self ):
        return ('\n' + self.code).split( '\n' )

    def _set_lines ( self, lines ):
        line      = self.line
        self.code = '\n'.join( lines[1:] )
        do_later( self.facet_set, line = min( line, len( lines ) - 1 ) )

#-- Create The Demo ------------------------------------------------------------

demo = Demo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == "__main__":
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
