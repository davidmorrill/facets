"""
Defines a CustomFileDialog class for displaying a file selection dialog based on
the CustomFileDialogEditor.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import UIView, Either, Str, Bool, Instance, Enum, List, Event, View, UItem

from facets.ui.editors.custom_file_dialog_editor \
    import FSItem, FSFilter, Access, SortColumn, CustomFileDialogEditor

#-------------------------------------------------------------------------------
#  'CustomFileDialog' class:
#-------------------------------------------------------------------------------

class CustomFileDialog ( UIView ):

    #-- Facet Definitions ------------------------------------------------------

    # The default path:
    path = Either( Str, Instance( FSItem ), default = '' )

    # The operation mode for the editor. 'create' is like 'save', but prompts
    # the user for overwriting if the selected file already exists, whereas
    # 'save' will not:
    mode = Enum( 'open', 'create', 'save' )

    # The access mode the selected file must support:
    access = Access

    # List of FSFilter instances that can be used by the user to filter the list
    # of files included in the view:
    filters = List( FSFilter )

    # List of FSExt subclasses that can be used by the user to provide
    # additional information about any selected file:
    exts = List # ( FSExt subclass )

    # The facets UI persistence id to save the user preference data under:
    id = Str( 'facets.ui.editor.custom_file_dialog' )

    # Should the confirmation query for creating a new folder or for overwriting
    # a file in 'create' mode be a popup (True) or a modal dialog (False)?
    confirm_popup = Bool( True )

    # The initial sort column name:
    sort_column = SortColumn

    # Is the initial sort order ascending (True) or descending (False)?
    sort_ascending = Bool( True )

    #-- Private Facets ---------------------------------------------------------

    # Event fired when the user is done with the dialog:
    done = Event

    #-- Public Methods ---------------------------------------------------------

    def show ( self ):
        """ Shows the custom file dialog. Returns **True** if the user clicks
            the Open/Create/Save button, or **False** if the user clicks the
            Cancel button.

            If True is returned, the selected file is contained in 'path'.
        """
        return self.edit_facets( view =
            View(
                UItem( 'path',
                       id     = 'path',
                       editor = CustomFileDialogEditor(
                           mode           = self.mode,
                           access         = self.access,
                           filters        = self.filters,
                           exts           = self.exts,
                           confirm_popup  = self.confirm_popup,
                           sort_column    = self.sort_column,
                           sort_ascending = self.sort_ascending,
                           done           = 'done' )
                ),
                title     = self.mode.capitalize(),
                id        = self.id,
                width     = 0.5,
                height    = 0.5,
                resizable = True,
                kind      = 'livemodal'
            )
        ).result


    def get_path ( self ):
        """ Shows the custom file dialog. Returns the selected path if the user
            clicks the Open/Create/Save button, or **None** if the user clicks
            the Cancel button.
        """
        return (self.path if self.show() else None)

    #-- Facet Event Handlers ---------------------------------------------------

    def _done_set ( self, result ):
        """ Handles the 'done' event being fired.
        """
        self.ui_info.ui.dispose( result = result )

#-- EOF ------------------------------------------------------------------------
