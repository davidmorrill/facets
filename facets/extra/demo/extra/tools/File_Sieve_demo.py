"""
A demonstration of the <i>File Sieve</i> tool, which is part of the
<b>facets.extra</b> package.

This demo is displayed as a popup window because it requires a fairly wide
screen area in order to display all of the viewer columns. However, it can be
embedded within any Facets UI view if desired.

The top portion of the File Sieve is a <i>live filter</i>, meaning that you can
type information into any of the various fields to filter the set of files
shown.

For fields such as <i>volume<i>, the information you type can appear anywhere in
the volume name to produce a match. The match is case insensitive.

For numeric fields, such as <i>height</i> and <i>width</i>, you can type a
number or a numeric relation (e.g. <=32). If you do not specify a relation,
<i>less than or equal</i> is assumed. The valud relations are: '=', '!=', '<',
'<=', '>' or '>='.

If an image in the view is 32x32 or smaller, it will appear in the first column
of the viewer. If it is larger than 32x32, then the value for that cell will
be blank. However, you can click on the cell to display a pop-up view of the
complete image.

In order for this demo to run, you must have the facets.extra package
installed.
"""

#-------------------------------------------------------------------------------
#  License: See sections (A) and (B) of the .../facets/LICENSE.txt file.
#-------------------------------------------------------------------------------

from facets.extra.tools.file_sieve \
     import FileSieve

#-- Create the demo ------------------------------------------------------------

popup = FileSieve

#-- Run the demo (if invoked from the command line) ----------------------------

if __name__ == '__main__':
    popup().edit_facets()

#-- EOF ------------------------------------------------------------------------