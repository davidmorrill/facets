.. _tool_tools:

The Standard Tools
==================

In addition to defining the core tool architecture, Facets also includes several
dozen predefined tools, contained in the *facets.extra.tools* package. Useful in
their own right, this collection of tools also provides a rich collection of
examples to study or use when creating your own tools.

The remainder of this section contains descriptions of each available standard
tool, providing information about:

* The module and class name for the tool.
* The purpose and function of the tool.
* The available input and output connections provided by the tool.
* Any additional features or options supported by the tool.
* Screenshots of the tool in use.

The Tools Catalog
-----------------

:ref:`tool_app_monitor`
  Displays views of all application objects associated with its containing tool
  window or any other DockWindow specified by its input Control object.

:ref:`tool_class_browser`
  Displays a hierarchical tree view of all packages, modules, classes and
  methods containing in the application's *PYTHONPATH*.

:ref:`tool_clipboard`
  Defines a clipboard tool that allows copying and pasting text, images and
  arbitrary Python objects to and from the system clipboard.

:ref:`tool_control_flasher`
  A tool that causes any input Control object to flash briefly on the screen.

:ref:`tool_control_grabber`
  Allows you to *grab* any Facets UI control and make it available for use with
  other tools.

:ref:`tool_control_stack`
  Displays the parent and child Controls of an input Control object and allows
  you to select any displayed Control for further processing by other tools.

:ref:`tool_cross_reference`
  Allows you display and select information about the various module-level
  symbols defined and referenced within a specified Python source code tree.

:ref:`tool_drop_zone`
  Allows you to drag and drop objects which are forwarded to all connected
  tools.

:ref:`tool_facet_db`
  Allows you to view the contents of, and optionally delete, the items contained
  in a Facets database.

:ref:`tool_file_browser`
  Allows you to display a hierarchical tree view of a specified portion of your
  file system and select directories or files within the hierarchy.

:ref:`tool_file_stack`
  Allows you to select files using a FileStackEditor.

:ref:`tool_image_collector`
  Allows you to collect, organize, display and select images.

:ref:`tool_image_library_selector`
  Allows you to select any image contained within the Facets ImageLibrary.

:ref:`tool_image_library_viewer`
  Allows you to display, filter and select multiple images contained within the
  Facets ImageLibrary.

:ref:`tool_image_zoomer`
  Allows you to display an input image as a zoomable image using the standard
  Facets *ImageZoomEditor*.

:ref:`tool_object_source`
  Displays a series of tabs, one for each Python source module used to implement
  any HasFacets object it receives. Each tab in turn displays a hierarchical
  tree view of all classes and methods defined by the source module.

:ref:`tool_print_object`
  Prints the contents of any input object it receives to *stdout*.

:ref:`tool_select_dock_window_theme`
  Allows you to select a new default DockWindow theme from a list of available
  factory defined themes.

:ref:`tool_stdout`
  Allows you to intercept, display, filter and search text sent to the
  application's *stdout* and/or *stderr* files.

:ref:`tool_syntax_checker`
  Performs syntax checking on an input Python source file.

:ref:`tool_text_collector`
  Allows you to organize, filter, display and select from a collection of input
  text strings.

:ref:`tool_traceback_viewer`
  Allows you to display and select information about Python tracebacks.

:ref:`tool_view_tester`
  Allows you to display and/or test the Facets UI View associated with an input
  source file.

:ref:`tool_vip_shell`
  Displays an instance of the standard Facets VIP Shell, a graphical,
  interactive Python shell.

.. toctree::
   :hidden:
   :maxdepth: 1

   tool_app_monitor
   tool_class_browser
   tool_clipboard
   tool_control_flasher
   tool_control_grabber
   tool_control_stack
   tool_cross_reference
   tool_drop_zone
   tool_facet_db
   tool_file_browser
   tool_file_stack
   tool_image_collector
   tool_image_library_selector
   tool_image_library_viewer
   tool_image_zoomer
   tool_object_source
   tool_print_object
   tool_select_dock_window_theme
   tool_stdout
   tool_syntax_checker
   tool_text_collector
   tool_traceback_viewer
   tool_view_tester
   tool_vip_shell

