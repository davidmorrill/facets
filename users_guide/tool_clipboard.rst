.. _tool_clipboard:

Clipboard
=========

Defines a clipboard tool that allows copying and pasting text, images and
arbitrary Python objects to and from the system clipboard.

You should connect to the input or output connection facet appropriate to the
type of data (text, image or Python object) that you want to send to or receive
from the system clipboard.

Module
------

facets.extra.tools.clipboard

Input Connections
-----------------

text
  A string of text copied to the system clipboard.

image
  An image copied to the system clipboard.

object
  An arbitrary Python object copied to the system clipboard.

Output Connections
------------------

text
  A string of text copied from the system clipboard.

image
  An image copied from the system clipboard.

object
  An arbitrary Python copied from the system clipboard.

Screenshots
-----------

.. image:: images/tool_clipboard.jpg

Since the clipboard tool is only used to move data to and from the system
clipboard, its visual representation is minimal, consisting only of the tab that
provides access to its feature toolbar.

