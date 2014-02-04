"""
# PresentationEditor Demo #

Demonstrates using the **PresentationEditor**, an editor which converts a text
string into a series of one or more animated slides suitable for giving
presentations.

The demo uses the PresentationEditor to display a presentation explaining
how to use and create slides for use with the editor. It also contains a text
editor containing the text used to define the presentation. You can change the
presentation text using the text editor and immediately view its effect in
the PresentationEditor tab.
"""

#-- Imports --------------------------------------------------------------------

from facets.api \
    import HasFacets, Str, Code, View, Tabbed, UItem

from facets.extra.editors.presentation_editor \
    import PresentationEditor

from facets.ui.pyface.timer.api \
    import do_after

#-- PresentationEditorDemo class -----------------------------------------------

class PresentationEditorDemo ( HasFacets ):

    presentation = Str
    text         = Code

    view = View(
        Tabbed(
            UItem( 'presentation',
                   dock   = 'tab',
                   editor = PresentationEditor()
            ),
            UItem( 'text', dock = 'tab' )
        ),
        width  = 0.7,
        height = 0.7
    )

    def _presentation_default ( self ):
        return PresentationText

    def _text_default ( self ):
        return PresentationText

    def _text_set ( self ):
        # Delay the update so that every keystroke does not update the
        # presentation immediately:
        do_after( 500, self._update_presentation )

    def _update_presentation ( self ):
        self.presentation = self.text

#-- The sample presentation content --------------------------------------------

PresentationText = """
:hc PresentationEditor: %title
:sa slide
:st hide
:< *

-- Navigation ------------------------------------------------------------------
< Use mouse wheel or left mouse button click

< Mouse wheel:
  < Roll down: Go to next slide item or slide
  < Roll up: Go to previous slide item or slide

< Left mouse button click:
  < Display divided into five logical regions
  < Clicking in each region has different effect
  < Top left: Go to first slide
  < Top right: Go to last slide
  < Bottom left: Go to previous slide
  < Bottom right: Go to next slide
  < Center: Display pop-up list of slide titles

-- Editor Basics ---------------------------------------------------------------
< PresentationEditor accepts a text string as input
< Parses the text into one or more slides
< Displays first slide and lets user navigate to view others
< Editor does not modify text
< External changes to text cause slides to be reparsed and displayed
< Editor tries to keep same position in slide sequence after a change

-- Slide Text Format -----------------------------------------------------------
< Slide text format is:
  < Very simple
  < Line oriented
  < Each line defines a single item

< Five line types:
  < Slide title
  < Slide item
  < Vertical space
  < Command
  < Comment

-- Slide Title -----------------------------------------------------------------
< Line starts with at least two dashes: '--'
< Followed by the slide title (e.g. 'Slide Title')
< May optionally be followed by more trailing dashes

< Examples:
  < -- Slide Title
  | ----- Slide Title -----

-- Slide Item ------------------------------------------------------------------
< Any non-blank line not starting with --, : or #
< Usually starts with *, -, <, >, /, \, ? or |
  < Defines the item animation style

< Each slide item defines a separate display item
  < Exception: Line starting with | continues previous item

< Indented lines create indented display items
  < Only one level of indenting supported

-- Animation Styles ------------------------------------------------------------
:< <
* Leading character of a display item defines animation style:
  * *: No animation
  - -: Fade in
  < <: Right to left
  > >: Left to right
  / /: Bottom to top
  \ \: Top to bottom
  ? ?: Use random animation style

* If no style is specified, it defaults to *
  * Example: This line uses the default * style
:< *

-- Slide Item Content ----------------------------------------------------------
< Two types of slide item content:
  < Text
  < Picture (i.e. image)

< A picture is indicated using a special character:
  < File from file system: !file_name
  < File from Facets image library: @library:file_name

< Pictures are normally displayed 1:1
  < Exception: Slide with a single image item zooms image to fit display

-- Vertical Space --------------------------------------------------------------
< A blank line inserts vertical space between items
< The amount is controlled by 'vertical_space' (vs) variable
  < Example: ':vs 15' changes value to 15 pixels
< Multiple blank lines insert even more space

< A line containing a positive integer 'n' inserts 'n' pixels of space

< Examples:
  < * Item 1
  | - Item 2
  |                <-- Inserts 'vs' pixels of space
  | - Item 3
  | 30             <-- Inserts 30 pixels of space
  | - Item 4

-- Command ---------------------------------------------------------------------
< A line starting with : is a command
< Format of line is: :command value
< Commands change values of presentation global variables
< Commands affect subsequent variable usage only
< Most commands have a long form and a two character short form

< Examples:
  < :header_font Arial 20
  | :hf Arial 20
  | :slide_advance slide
  | :sa slide

-- Comment ---------------------------------------------------------------------
< Any line starting with a '#' is a comment
< Comments are ignored

< Examples:
  < # This is a comment
  | #This is another comment

-- Slide Content ---------------------------------------------------------------
< Each slide has the following content:
  < Optional header at top
  < One or more body items
  < Optional footer at bottom

< Five types of body items:
  < Bullet item
  < Multiline item (created using | prefix)
  < Indented item
  < Code item (multiline indented item created with | prefix)
  < Picture item

-- Item Formatting (1/2) -------------------------------------------------------
< Each slide item type has customizable formatting
< Formatting controlled by global variables
< Global variables are changed using commands
< Variables are defined based on item type and format type
  < Example: 'header_theme' for header item theme data
  < Usually there is a shortcut ('ht' for 'header_theme')
< Changing a variable only affects subsequent usage
< Make global changes at beginning of presentation text

-- Item Formatting (2/2) -------------------------------------------------------
< Header/Footer global variables:
  < header_font/footer_font (hf/ff)
  < header_theme/footer_theme (ht/ft)
  < header_content/footer_content (hc/fc)
  < header_image/footer_image (hi/fi)
  < header_alignment/footer_alignment (ha/fa)

< Body item global variables:
  < bullet_font (bf)
  < bullet_theme (bt)
  < indented_font (if)
  < indented_theme (it)
  < multiline_font (mf)
  < multiline_theme (mt)
  < code_font (cf)
  < code_theme (ct)
  < picture_theme (pt)

-- Header/Footer Substitutions -------------------------------------------------
< Headers and footers with text content can use special variables:
  < %title: The title of the current slide
  < %index: One-based index of the current slide
  < %count: Total number of slides

< Examples:
  < :hc PresentationEditor: %title
  | :fc Slide %index of %count
"""[1:-1]

#-- Create the demo ------------------------------------------------------------

demo = PresentationEditorDemo

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    demo().edit_facets()

#-- EOF ------------------------------------------------------------------------
