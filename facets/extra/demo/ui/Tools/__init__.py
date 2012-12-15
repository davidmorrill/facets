"""
The demos in this section are not really demos at all, but are actual
Facets-based tools created and used by the author. They are included to
illustrate the types of tools it is possible to build using the Facets
<b><i>tools</i></b> framework.

Each tool was created using the tools framework, which can be started using the
command:

 python <i>.../facets/extra/tools/run.py</i>

In each case, once the framework starts, the following steps were taken to make
a new tool:

 - Create a new <i>perspective</i> using the <b><i>Perspective/New...</i></b>
   menu option, which creates a new tool perspective view.
 - Delete unneeded tools from the starter set provided by clicking the <b>X</b>
   icon in the tool's tab.
 - Add new tools by selecting them from the list of more than 50 tools in the
   <b><i>Tools</i></b> menu.
 - Arrange the tools within the perspective by dragging tabs and adjusting
   splitter bars as needed.
 - Connect the tools together using the <b><i>connect</i></b> feature which is
   accessed by hovering the mouse pointer over the circular icon shown in each
   tool's tab.
 - Test the resulting composite tool and iterate on the above steps until it has
   the desired behavior.
 - Once a satisfactory composite tool has been created, select the
   <b><i>Perspective/Export as stand-alone tool...</i></b> menu option and
   adjust the default values in the pop-up dialog that appears.
 - Click the <b><i>Save</i></b> button in the pop-up dialog to create a new
   stand-alone tool that has the same behavior as the tool you just composed.
 - Close the pop-up dialog.

Each demo/tool in this section was created using this procedure. The only
changes made by hand to the files, for the purpose of allowing them to work with
the demo framework, were to add the lines:

 #-- Create the demo version of the tool ----------------------------------------

 demo = <i>tool_class_name</i>

located near the end of each file, and also to reformat the automatically
generated module comment to format more nicely within the demo.

Because these are automatically generated files created by the tools framework,
all of the files have the same basic structure, so there is very little to be
gained from studying the source of more than one file in any detail.

The real value of these demos is to illustrate the kinds of tools you can easily
create just by selecting a few menu options...
"""
