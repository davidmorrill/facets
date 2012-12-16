.. _tool_control_grabber:

ControlGrabber
==============

Allows you to *grab* any Facets UI control and make it available for use with
other tools.

To use the tool, simply click on the question mark icon and drag the mouse
pointer over other Facets UI controls. As the mouse pointer passes over a
control, the tool displays information about the control, such as: *QWidget
(197,348) has a min size of (0,0).* In addition, the current Control object
being moused over is sent to any tool connected to the control grabber's *over*
facet.

Releasing the mouse button while the pointer is over a valid Control object
*selects* the object and sends it to any tool connected to the tool's *selected*
facet. It also takes a screen grab of the selected control and sends the
resulting image to any tool coonected to the tool's *image* facet.

Module
------

facets.extra.tools.control_grabber

Input Connections
-----------------

None.


Output Connections
------------------

**selected**
  The most recently selected Control object.

**over**
  The Control object currently being moused over.

**image**
  The image of the most recently selected Control object.

Screenshots
-----------

.. image:: images/tool_control_grabber.jpg
