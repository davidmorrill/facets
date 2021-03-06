"""
Defines "factory functions" for all of the standard EditorFactorys subclasses.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
#  Imports:
#-------------------------------------------------------------------------------

from toolkit \
    import toolkit

#-------------------------------------------------------------------------------
#  Define 'factory' functions for all of the GUI toolkit dependent facets:
#-------------------------------------------------------------------------------

def ColorFacet ( *args, **facets ):
    return toolkit().color_facet( *args, **facets )


def RGBColorFacet ( *args, **facets ):
    return toolkit().rgb_color_facet( *args, **facets )


def FontFacet ( *args, **facets ):
    return toolkit().font_facet( *args, **facets )

#-------------------------------------------------------------------------------
#  Define 'factory' functions for all of the standard EditorFactory subclasses:
#-------------------------------------------------------------------------------

def ArrayEditor ( *args, **facets ):
    """ Allows the user to edit 2-D Numeric arrays.
    """
    from facets.ui.editors.array_editor import ArrayEditor

    return ArrayEditor( *args, **facets )


def ArrayViewEditor ( *args, **facets ):
    """ Allows the user to view 1-d or 2-d arrays of values.
    """
    from facets.ui.editors.array_view_editor import ArrayViewEditor

    return ArrayViewEditor( *args, **facets )


def ASTEditor ( *args, **facets ):
    """ Allows the user to view the contents of a Python Abstract Syntax Tree.
    """
    from facets.ui.editors.ast_editor import ASTEditor

    return ASTEditor( *args, **facets )


def BooleanEditor ( *args, **facets ):
    """ Allows the user to select a true or false condition.
    """
    from facets.ui.editors.boolean_editor import BooleanEditor

    return BooleanEditor( *args, **facets )


def ButtonEditor ( *args, **facets ):
    """ Allows the user to click a button; this editor is typically used with
        an event facet to fire the event.
    """
    from facets.ui.editors.button_editor import ButtonEditor

    return ButtonEditor( *args, **facets )


def CheckListEditor ( *args, **facets ):
    """ Allows the user to select zero, one, or more values from a finite set of
        possibilities.

        Note that the "simple" style is limited to selecting a single value.
    """
    from facets.ui.editors.check_list_editor import CheckListEditor

    return CheckListEditor( *args, **facets )


def CodeEditor ( *args, **facets ):
    """ Allows the user to edit a multi-line string.

        The "simple" and "custom" styles of this editor display multiple lines
        of the string, with line numbers.
    """
    return toolkit().code_editor( *args, **facets )


def CollageEditor ( *args, **facets ):
    """ Allows the user to work with a collection of images using a 'collage'
        style that allows images to be moved, scaled and selected using a
        virtual pasteboard.
    """
    from facets.ui.editors.collage_editor import CollageEditor

    return CollageEditor( *args, **facets )


def ColorEditor ( *args, **facets ):
    """ Allows the user to select a color.
    """
    from facets.ui.editors.color_editor import ColorEditor

    return ColorEditor( *args, **facets )


def ColorPaletteEditor ( *args, **facets ):
    """ Allows the user to select a color using a color palette.
    """
    from facets.ui.editors.color_palette_editor import ColorPaletteEditor

    return ColorPaletteEditor( *args, **facets )


def CompoundEditor ( *args, **facets ):
    """ Allows the user to select a value based on a compound facet.

        Because a compound facet is composed of multiple facet definitions, this
        editor factory displays facet editors for each of the constituent
        facets. For example, consider the following facet attribute, defined as
        a compound that accepts integer values in the range of 1 to 6, or text
        strings corresponding to those integers::

            compound = Facet( 1, Range(1, 6), 'one', 'two', 'three', 'four',
                              'five', 'six' )

        The editor displayed for this facet attribute combines editors for
        integer ranges and for enumerations.
    """
    from facets.ui.editors.compound_editor import CompoundEditor

    return CompoundEditor( *args, **facets )


def ControlGrabberEditor ( *args, **facets ):
    """ Allows the user to 'grab' GUI toolkit neutral 'control' objects.
    """
    from facets.ui.editors.control_grabber_editor import ControlGrabberEditor

    return ControlGrabberEditor( *args, **facets )


def CustomEditor ( *args, **facets ):
    """ Creates a developer-specified custom editor.
    """
    from facets.ui.editors.custom_editor import CustomEditor

    return CustomEditor( *args, **facets )


def CustomFileDialogEditor ( *args, **facets ):
    """ Creates a CustomFileDialogEditor for performing file selection using
        custom file system definitions, filters and extensions.
    """
    from facets.ui.editors.custom_file_dialog_editor \
        import CustomFileDialogEditor

    return CustomFileDialogEditor( *args, **facets )


def DirectoryEditor ( *args, **facets ):
    """ Allows the user to specify a directory.
    """
    return toolkit().directory_editor( *args, **facets )


def DrawableCanvasEditor ( *args, **facets ):
    """ Creates an editor for displaying a canvas of drawable items.
    """
    from facets.ui.editors.drawable_canvas_editor import DrawableCanvasEditor

    return DrawableCanvasEditor( *args, **facets )


def DropEditor ( *args, **facets ):
    """ Allows dropping an object to set a value.
    """
    return toolkit().drop_editor( *args, **facets )


def DNDEditor ( *args, **facets ):
    """ Allows dragging and dropping an object.
    """
    from facets.ui.editors.dnd_editor import DNDEditor

    return DNDEditor( *args, **facets )


def EnumEditor ( *args, **facets ):
    """ Allows the user to select a single value from an enumerated list of
        values.
    """
    #from facets.ui.editors.enum_editor import EnumEditor
    #
    #return EnumEditor( *args, **facets )

    return toolkit().enum_editor( *args, **facets )


def FileEditor ( *args, **facets ):
    """ Allows the user to select a file.
    """
    return toolkit().file_editor( *args, **facets )


def FileStackEditor ( *args, **facets ):
    """ Allows the user to select a file using a dual list of paths and files.
    """
    from facets.ui.editors.file_stack_editor import FileStackEditor

    return FileStackEditor( *args, **facets )


def FileSystemEditor ( *args, **facets ):
    """ Allows the user to select a file using an 'explorer'-like view.
    """
    from facets.ui.editors.file_system_editor import FileSystemEditor

    return FileSystemEditor( *args, **facets )


def FilmStripEditor ( *args, **facets ):
    """ Allows the user to select items using a visual "filmstrip" of choices.
    """
    from facets.ui.editors.filmstrip_editor import FilmStripEditor

    return FilmStripEditor( *args, **facets )


def FilteredSetEditor ( *args, **facets ):
    """ Allows the user to edit a filterable set of items.
    """
    from facets.ui.editors.filtered_set_editor import FilteredSetEditor

    return FilteredSetEditor( *args, **facets )


def FontEditor ( *args, **facets ):
    """ Allows the user to select a typeface and type size.
    """
    return toolkit().font_editor( *args, **facets )


def GridEditor ( *args, **facets ):
    """ Displays data in a grid.
    """
    return toolkit().grid_editor( *args, **facets )


def HistogramEditor ( *args, **facets ):
    """ Displays a series of values as a histogram plot.
    """
    from facets.ui.editors.histogram_editor import HistogramEditor

    return HistogramEditor( *args, **facets )


def HistoryEditor ( *args, **facets ):
    """ Displays a text field with a history of prior values.
    """
    from facets.ui.editors.history_editor import HistoryEditor

    return HistoryEditor( *args, **facets )


def HLSADerivedImageEditor ( *args, **facets ):
    """ Allows the user to edit an HLSADerivedImage object's mask and HLSA
        settings.
    """
    from facets.ui.editors.hlsa_derived_image_editor \
        import HLSADerivedImageEditor

    return HLSADerivedImageEditor( *args, **facets )


def HLSColorEditor ( *args, **facets ):
    """ Allows the user to select a color using an HLSA-based color picker.
    """
    from facets.ui.editors.hls_color_editor import HLSColorEditor

    return HLSColorEditor( *args, **facets )


def HTMLBrowserEditor ( *args, **facets ):
    """ Displays HTML-based help/documentation with a table of contents.
    """
    from facets.ui.editors.html_browser_editor import HTMLBrowserEditor

    return HTMLBrowserEditor( *args, **facets )


def HTMLEditor ( *args, **facets ):
    """ Displays formatted HTML text.
    """
    return toolkit().html_editor( *args, **facets )


def ImageEditor ( *args, **facets ):
    """ Allows an image to be imbedded ina facets ui.
    """
    from facets.ui.editors.image_editor import ImageEditor

    return ImageEditor( *args, **facets )


def ImageEnumEditor ( *args, **facets ):
    """ Allows the user to select an image that represents a value in an
        enumerated list of values.
    """
    from facets.ui.editors.image_enum_editor import ImageEnumEditor

    return ImageEnumEditor( *args, **facets )


def ImageLibraryEditor ( *args, **facets ):
    """ Allows the user to select select images contained in the Facets image
        library.
    """
    from facets.ui.editors.image_library_editor import ImageLibraryEditor

    return ImageLibraryEditor( *args, **facets )


def ImageTilerEditor ( *args, **facets ):
    """ Allows the user to tile an image over the background of a control.
    """
    from facets.ui.editors.image_tiler_editor import ImageTilerEditor

    return ImageTilerEditor( *args, **facets )


def ImageZoomEditor ( *args, **facets ):
    """ Allows an image to zoomed in and out.
    """
    from facets.ui.editors.image_zoom_editor import ImageZoomEditor

    return ImageZoomEditor( *args, **facets )


def InstanceEditor ( *args, **facets ):
    """ Allows the user to modify a facet attribute whose value is an instance,
        by modifying the facet attribute values on the instance.
    """
    from facets.ui.editors.instance_editor import InstanceEditor

    return InstanceEditor( *args, **facets )


def JSONEditor ( *args, **facets ):
    """ Allows the user to view the contents of a Python JSON object
    """
    from facets.ui.editors.json_editor import JSONEditor

    return JSONEditor( *args, **facets )


def KeyBindingEditor ( *args, **facets ):
    """ Allows the user to bind methods to keys.
    """
    from facets.ui.editors.key_binding_editor import KeyBindingEditor

    return KeyBindingEditor( *args, **facets )


def LightTableEditor ( *args, **facets ):
    """ Allows the user to view/select image files using a 'light table'.
    """
    from facets.ui.editors.light_table_editor import LightTableEditor

    return LightTableEditor( *args, **facets )


def ListEditor ( *args, **facets ):
    """ Allows the user to modify a list of values.

        The user can add, delete, or reorder items, or change the content of
        items.
    """
    return toolkit().list_editor( *args, **facets )


def ListStrEditor ( *args, **facets ):
    """ Allows the user to modify a list of strings (or values that can be
        mapped to strings).
    """
    return toolkit().list_str_editor( *args, **facets )


def ListViewEditor ( *args, **facets ):
    """ Allows the user to view, edit and organize a collection of objects or
        values.
    """
    from facets.ui.editors.list_view_editor import ListViewEditor

    return ListViewEditor( *args, **facets )


def MultipleInstanceEditor ( *args, **facets ):
    """ Allows the user to modify a facet attribute whose value is a list of
        (presumably) related objects which are to be edited in parallel as if
        they were a single object.
    """
    from facets.ui.editors.multiple_instance_editor \
        import MultipleInstanceEditor

    return MultipleInstanceEditor( *args, **facets )


def NotebookEditor ( *args, **facets ):
    """ Allows the user to edit a list of objects, with each object represented
        by a notebook tab.
    """
    from facets.ui.editors.notebook_editor import NotebookEditor

    return NotebookEditor( *args, **facets )


def NullEditor ( *args, **facets ):
    """ Defines an empty (placeholder) editor.
    """
    from facets.ui.editors.null_editor import NullEditor

    return NullEditor( *args, **facets )


def PopupEditor ( *args, **facets ):
    """ Allows the user to use a clickable popup editor.
    """
    from facets.ui.editors.popup_editor import PopupEditor

    return PopupEditor( *args, **facets )


def PresentationEditor ( *args, **facets ):
    """ Allows the user to view the contents of a string as a series of one or
        more presentation 'slides' using a simple set of formatting rules.
    """
    from facets.ui.editors.presentation_editor import PresentationEditor

    return PresentationEditor( *args, **facets )


def ProgressBarEditor ( *args, **facets ):
    """ Allows the user to use a progress bar editor.
    """
    from facets.ui.editors.progress_bar_editor import ProgressBarEditor

    return ProgressBarEditor( *args, **facets )
PresentationEditor

def PropertyListEditor ( *args, **facets ):
    """ Allows the user to use a property sheet editor.
    """
    from facets.ui.editors.property_list_editor import PropertyListEditor

    return PropertyListEditor( *args, **facets )


def PropertySheetEditor ( *args, **facets ):
    """ Allows the user to use a property sheet editor.
    """
    from facets.ui.editors.property_sheet_editor import PropertySheetEditor

    return PropertySheetEditor( *args, **facets )


def RangeEditor ( *args, **facets ):
    """ Allows the user to specify a value within a range.
    """
    from facets.ui.editors.range_editor import RangeEditor

    return RangeEditor( *args, **facets )


def RangeSliderEditor ( *args, **facets ):
    """ Allows the user to use a clickable popup editor.
    """
    from facets.ui.editors.range_slider_editor import RangeSliderEditor

    return RangeSliderEditor( *args, **facets )


def ScrubberEditor ( *args, **facets ):
    from facets.ui.editors.scrubber_editor import ScrubberEditor

    return ScrubberEditor( *args, **facets )


def SetEditor ( *args, **facets ):
    from facets.ui.editors.set_editor import SetEditor

    return SetEditor( *args, **facets )


def ShellEditor ( *args, **facets ):
    from facets.ui.editors.shell_editor import ShellEditor

    return ShellEditor( *args, **facets )


def SlideshowEditor ( *args, **facets ):
    from facets.ui.editors.slideshow_editor import SlideshowEditor

    return SlideshowEditor( *args, **facets )


def StackEditor ( *args, **facets ):
    """ Allows the user to edit a list of objects using a flexible, lightweight
        editor supporting highly customized graphics.
    """
    from facets.ui.editors.stack_editor import StackEditor

    return StackEditor( *args, **facets )


def StringGridEditor ( *args, **facets ):
    """ Allows the user to select an item from a list of strings.
    """
    from facets.ui.editors.string_grid_editor import StringGridEditor

    return StringGridEditor( *args, **facets )


def TemplateEditor ( *args, **facets ):
    """ Allows the user to edit a string using a template.
    """
    from facets.ui.editors.template_editor import TemplateEditor

    return TemplateEditor( *args, **facets )


def TextEditor ( *args, **facets ):
    """ Allows the user to modify a text string.

        The string value entered by the user is coerced to the appropriate type
        for the facet attribute being modified.
    """
    from facets.ui.editors.text_editor import TextEditor

    return TextEditor( *args, **facets )


def ThemedButtonEditor ( *args, **facets ):
    from facets.ui.editors.themed_button_editor import ThemedButtonEditor

    return ThemedButtonEditor( *args, **facets )


def ThemedCheckboxEditor ( *args, **facets ):
    from facets.ui.editors.themed_checkbox_editor import ThemedCheckboxEditor

    return ThemedCheckboxEditor( *args, **facets )


def ThemeEditor ( *args, **facets ):
    """ Allows the user to edit the appearance of a Theme object visually.
    """
    from facets.ui.editors.theme_editor import ThemeEditor

    return ThemeEditor( *args, **facets )


def ThemeLayoutEditor ( *args, **facets ):
    """ Allows the user to test what a layout using a specified theme will look
        like visually.
    """
    from facets.ui.editors.theme_layout_editor import ThemeLayoutEditor

    return ThemeLayoutEditor( *args, **facets )


def ThemedSliderEditor ( *args, **facets ):
    from facets.ui.editors.themed_slider_editor import ThemedSliderEditor

    return ThemedSliderEditor( *args, **facets )


def ThemedTextEditor ( *args, **facets ):
    from facets.ui.editors.themed_text_editor import ThemedTextEditor

    return ThemedTextEditor( *args, **facets )


def TokenEditor ( *args, **facets ):
    """ Allows the user to view the contents of some Python source as a list of
        tokens.
    """
    from facets.ui.editors.token_editor import TokenEditor

    return TokenEditor( *args, **facets )


def ToolbarEditor ( *args, **facets ):
    from facets.ui.editors.toolbar_editor import ToolbarEditor

    return ToolbarEditor( *args, **facets )


def VerticalNotebookEditor ( *args, **facets ):
    """ Allows the user display a list of objects using a vertically oriented
        notebook.
    """
    from facets.ui.editors.vertical_notebook_editor import VerticalNotebookEditor

    return VerticalNotebookEditor( *args, **facets )


def TitleEditor ( *args, **facets ):
    """ Displays a dynamic value using a title control.
    """
    from facets.ui.editors.title_editor import TitleEditor

    return TitleEditor( *args, **facets )


def TreeEditor ( *args, **facets ):
    """ Allows the user to modify a tree data structure.
    """
    return toolkit().tree_editor( *args, **facets )


def TupleEditor ( *args, **facets ):
    """ Allows the user to edit the contents of a tuple with a constant number
        of elements of known types.
    """
    from facets.ui.editors.tuple_editor import TupleEditor

    return TupleEditor( *args, **facets )


def UniversalEditor ( *args, **facets ):
    """ Allows a user to edit/display the contents of an arbitrary Python object
        using the most appropriate type of editor or viewer.
    """
    from facets.ui.editors.universal_editor import UniversalEditor

    return UniversalEditor( *args, **facets )


def ValueEditor ( *args, **facets ):
    """ Allows the user to display a hierarchic view of an arbitrary Python
        value.
    """
    from facets.ui.editors.value_editor import ValueEditor

    return ValueEditor( *args, **facets )


def VIPShellEditor ( *args, **facets ):
    """ Allows the user to use the Visual Interactive Python shell.
    """
    from facets.ui.editors.vip_shell_editor import VIPShellEditor

    return VIPShellEditor( *args, **facets )

#-- EOF ------------------------------------------------------------------------