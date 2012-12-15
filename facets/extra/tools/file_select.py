"""
Defines the FileSelect tool which uses a CustomFileDialogEditor to allow the
user to select files.
"""

#-------------------------------------------------------------------------------
#  License: See section (A) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from facets.api \
    import Str, File, View, UItem, CustomFileDialogEditor

from facets.ui.editors.custom_file_dialog_editor \
    import ImageExt, TextExt, WebExt, MarkdownExt, PresentationExt, AnyFilter, \
           ImageFilter, TextFilter, PythonFilter, CFilter, WebFilter,          \
           MarkdownFilter, PresentationFilter

from tools \
    import Tool

#-------------------------------------------------------------------------------
#  'FileSelect' class:
#-------------------------------------------------------------------------------

class FileSelect ( Tool ):

    #-- Facet Definitions ------------------------------------------------------

    # The name of the tool:
    name = Str( 'File Select' )

    # The name of the currently select file:
    file_name = File( connect = 'both' )

    #-- Facet View Definitions -------------------------------------------------

    view = View(
        UItem( 'file_name',
               id     = 'file_dialog',
               editor = CustomFileDialogEditor(
                   mode    = 'select',
                   exts    = [ ImageExt, TextExt, WebExt, MarkdownExt,
                               PresentationExt ],
                   filters = [ AnyFilter, ImageFilter, TextFilter, PythonFilter,
                               CFilter, WebFilter, MarkdownFilter,
                               PresentationFilter ]
               )
        ),
        id     = 'facets.extra.tools.file_select.FileSelect',
        width  = 0.60,
        height = 0.75
    )

#-- EOF ------------------------------------------------------------------------
