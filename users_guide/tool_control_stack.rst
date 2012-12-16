.. _tool_control_stack:

ControlStack
============

Displays the parent and child Controls of its input Control object and allows
the user to select any displayed Control for further processing by other tools.

The tool's view is divided into two halves:

* The left half shows the parent control hierarchy for the current Control
  object. The topmost parent is shown first with the current Control shown at
  the bottom of the list.
* The right half shows all child Control objects of the current Control.

Each half of the view displays two columns for each Control object:

* The class type of the underlying GUI toolkit control.
* The hexadecimal address of the Control object.

Selecting any item in either the left or right half of the view assigns the
selected control to the tool's *selected* facet, making it available for use by
other connected tools. It also makes the selected Control the new *current*
Control, causing both the left and right halves of the tool view to update
accordingly.

Module
------

facets.extra.tools.control_stack

Input Connections
-----------------

control
  The current Control object whose parent and child Controls are being
  displayed.

Output Connections
------------------

selected
  The currently selected Control object.

Screenshots
-----------

.. image:: images/tool_controL_stack.jpg

A view of a control stack tool whose *control* input is connected to a
:ref:`tool_control_grabber` tool.

