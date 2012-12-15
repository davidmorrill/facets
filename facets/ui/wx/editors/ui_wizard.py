"""
Creates a wizard-based wxPython user interface for a specified UI object.

A wizard is a dialog box that displays a series of pages, which the user can
navigate with forward and back buttons.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

import wx
import wx.wizard as wz

from facets.core_api \
    import Facet, Str

from facets.ui.wx.constants \
    import DefaultTitle

from facets.ui.wx.helper \
    import restore_window, save_window, GroupEditor

from ui_panel \
    import fill_panel_for_group

#-------------------------------------------------------------------------------
#  Facet definitions:
#-------------------------------------------------------------------------------

# Facet that allows only None or a string value
none_str_facet = Facet( '', None, str )

#-------------------------------------------------------------------------------
#  Top-level Functions:
#-------------------------------------------------------------------------------

def ui_wizard ( ui, parent ):
    """ Creates a wizard-based wxPython user interface for a specified UI
        object.
    """
    # Create the copy of the 'context' we will need while editing:
    context     = ui.context
    ui._context = context
    new_context = {}
    for name, value in context.items():
        if value is not None:
            new_context[ name ] = value.clone_facets()
        else:
            new_context[ name ] = None

    ui.context = new_context

    # Now bind the context values to the 'info' object:
    ui.info.bind_context()

    # Create the wxPython wizard window:
    title = ui.view.title
    if title == '':
        title = DefaultTitle

    ui.control = wizard = wz.Wizard( parent(), -1, title )

    # Create all of the wizard pages:
    pages        = []
    editor_pages = []
    info         = ui.info
    shadow_group = ui.view.content.get_shadow( ui )
    min_dx = min_dy = 0
    for group in shadow_group.get_content():
        page = UIWizardPage( wizard, editor_pages )
        pages.append( page )
        fill_panel_for_group( page, group, ui )

        # Size the page correctly, then calculate cumulative minimum size:
        sizer = page.GetSizer()
        sizer.Fit( page )
        size   = sizer.CalcMin()
        min_dx = max( min_dx, size.GetWidth() )
        min_dy = max( min_dy, size.GetHeight() )

        # If necessary, create a PageGroupEditor and attach it to the right
        # places:
        id = group.id
        if id or group.enabled_when:
            page.editor = editor = PageGroupEditor( control = page )
            if id:
                page.id = id
                editor_pages.append( page )
                info.bind( id, editor )

            if group.enabled_when:
                ui.add_enabled( group.enabled_when, editor )

    # Size the wizard correctly:
    wizard.SetPageSize( wx.Size( min_dx, min_dy ) )

    # Set up the wizard 'page changing' event handler:
    wz.EVT_WIZARD_PAGE_CHANGING( wizard, wizard.GetId(), page_changing )

    # Size the wizard and the individual pages appropriately:
    prev_page = pages[0]
    wizard.FitToPage( prev_page )

    # Link the pages together:
    for page in pages[1:]:
        page.SetPrev( prev_page )
        prev_page.SetNext( page )
        prev_page = page

    # Finalize the display of the wizard:
    try:
        ui.prepare_ui()
    except:
        ui.control.Destroy()
        ui.control.ui = None
        ui.control    = None
        ui.result     = False
        raise

    # Position the wizard on the display:
    ui.handler.position( ui.info )

    # Restore the user_preference items for the user interface:
    restore_window( ui )

    # Run the wizard:
    if wizard.RunWizard( pages[0] ):
        # If successful, apply the modified context to the original context:
        original = ui._context
        for name, value in ui.context.items():
            if value is not None:
                original[ name ].copy_facets( value )
            else:
                original[ name ] = None
        ui.result = True
    else:
        ui.result = False

    # Clean up loose ends, like restoring the original context:
    save_window( ui )
    ui.finish()
    ui.context  = ui._context
    ui._context = {}


def page_changing ( event ):
    """ Handles the user attempting to change the current wizard page.
    """
    # Get the page the user is trying to go to:
    page = event.GetPage()
    if event.GetDirection():
       new_page = page.GetNext()
    else:
       new_page = page.GetPrev()

    # If the page has a disabled PageGroupEditor object, veto the page change:
    if ( ( new_page is not None ) and
        ( new_page.editor is not None ) and
        ( not new_page.editor.enabled ) ):
        event.Veto()

        # If their is a message associated with the editor, display it:
        msg = new_page.editor.msg
        if msg != '':
            wx.MessageBox( msg )

#-------------------------------------------------------------------------------
#  'UIWizardPage' class:
#-------------------------------------------------------------------------------

class UIWizardPage ( wz.PyWizardPage ):
    """ A page within a wizard interface.
    """

    #-- Public Methods ---------------------------------------------------------

    def __init__ ( self, wizard, pages ):
        wz.PyWizardPage.__init__ ( self, wizard )
        self.next  = self.previous = self.editor = None
        self.pages = pages


    def SetNext ( self, page ):
        """ Sets the next page after this one.
        """
        self.next = page


    def SetPrev ( self, page ):
        """ Sets the previous page to this one.
        """
        self.previous = page


    def GetNext ( self ):
        """ Returns the next page after this one.
        """
        editor = self.editor
        if (editor is not None) and (editor.next != ''):
            next = editor.next
            if next == None:
                return None

            for page in self.pages:
                if page.id == next:
                    return page

        return self.next


    def GetPrev ( self ):
        """ Returns the previous page to this one.
        """
        editor = self.editor
        if (editor is not None) and (editor.previous != ''):
            previous = editor.previous
            if previous is None:
                return None

            for page in self.pages:
                if page.id == previous:
                    return page

        return self.previous

#-------------------------------------------------------------------------------
#  'PageGroupEditor' class:
#-------------------------------------------------------------------------------

class PageGroupEditor ( GroupEditor ):
    """ Editor for a group, which displays a page.
    """

    #-- Facet Definitions ------------------------------------------------------

    # ID of next page to display:
    next = none_str_facet

    # ID of previous page to display:
    previous = none_str_facet

    # Message to display if user can't link to page:
    msg = Str

#-- EOF ------------------------------------------------------------------------