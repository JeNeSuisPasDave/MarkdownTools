MarkdownTools
==============

MarkdownTools is a collection of command line utilities for processing 
Markdown text files. At the moment the collection includes only one 
utility: ``mdmerge``. Over time additional utilities will be added to 
support Markdown workflows. 

**Note:** if you are using Python 2, then you need the 
``MarkdownTools2`` package.

mdmerge
=======

``mdmerge`` is a command line utility that produces a single Markdown document
by merging a set of Markdown documents. The merge can be accomplished by 
expanding *include* declarations found in the input files, by concatenating
a list of files found in an index file, or both.

Wait, doesn't Marked 2 already do that?
---------------------------------------

Brett Terpstra's `Marked 2`_ application is a GUI product that runs on OS X;
it watches Markdown text and displays the formatted output; it has 
extensive support for multi-file Markdown documents.
*Marked* is my tool of 
choice for viewing formatted Markdown. I use it whenever I'm creating or 
reviewing Markdown content on my OS X machine.
The invaluable multi-file document support in *Marked* is what drove me to
create ``mdmerge``.

.. _Marked 2: http://marked2app.com

``mdmerge`` brings multi-file Markdown document processing to the command line.
It is useful in any automated scripting environment where Markdown is
processed. For example, I use it in automated build scripts 
(e.g., using gmake or Grunt) to produce documentation for the
software I'm building.
It is cross-platform; you can pre-process the 
Markdown files on any common OS that has a recent version of Python.

What kinds of Markdown does it work with?
-----------------------------------------

``mdmerge`` has been tested with documents containing these Markdown syntax
variants:

* classic (John Gruber's Markdown_ syntax)
* MultiMarkdown (Fletcher Penny's syntax, MultiMarkdown_ version 4)
* GHF (`GitHub Flavored Markdown`_)

.. _Markdown:
	http://daringfireball.net/projects/markdown/syntax
.. _MultiMarkdown: http://fletcherpenney.net/multimarkdown/
.. _GitHub Flavored Markdown:
	https://help.github.com/articles/github-flavored-markdown

How do files get included?
--------------------------

``mdmerge`` accepts include declarations in these styles:

* MultiMarkdown transclusions_
* `Marked file includes`_
* `LeanPub code includes`_ (as `interpreted by Marked`_)
* `LeanPub index files`_ (also known as *book* files)
* `mmd_merge index files`_

.. _Marked file includes: 
	http://marked2app.com/help/Multi-File_Documents.html
.. _interpreted by Marked: 
	http://marked2app.com/help/Special_Syntax.html#includingcode
.. _LeanPub code includes: 
	https://leanpub.com/help/manual#leanpub-auto-code
.. _LeanPub index files: 
	https://leanpub.com/help/manual#leanpub-auto-the-booktxt-file
.. _transclusions: 
	http://fletcher.github.io/MultiMarkdown-4/transclusion
.. _mmd_merge index files: 
	https://github.com/fletcher/MMD-Support/blob/master/Utilities/mmd_merge.pl

Includes can be nested; that is, a file can include another file that itself
include other files, and so on. Index (or book) files are only processed
as such when they are the primary input; they cannot be nested -- files 
listed in the index file are treated as normal input files (including
expanding include specifications found within).

Command Line Syntax
===================

The command line looks like this:

::

	mdmerge [options] [-o outputfile] inputfiles
	mdmerge [options] [-o outputfile] -

Options
-------

``options``
	One or more of `--book`, `--export-target`, `--ignore-transclusions`,
	`--just-raw`, `--leanpub`, `--version`, `--help`, `-h`.

``--book``
	Treat STDIN as an index file (a "book" file).

``--export-target [html|latex|lyx|opml|rtf|odf]``
	Indicates the ultimate output target of the markdown processor, but 
	primarily impacts wildcard substitution in Marked inclusion.

``--help``
	Help information

``-h``
	Help information
	
``--ignore-transclusions``
	Leave any MultiMarkdown transclusion specifications alone; do not include
	the specified file. Useful if you want to mix Marked/LeanPub includes and
	MultiMarkdown includes, but have MultiMarkdown handline the transclusions.

``--just-raw``
	Ignore all include specifications except for raw includes; useful for
	processing the output of the Markdown processor to pick up the raw file include
	specifications that should have passed through untouched.

``--leanpub``
	Indicates that any input file named `book.txt` should be treated as a
	LeanPub index file.

``--version``
	Gives the version information about the utility.

``-o outputfile``
	The filepath in which to store the merged text. If not specified, then 
	STDOUT is used.

``--outfile outputfile``
	same as `-o`.

``inputfiles``
	A list of space separated input files that can be merged together. If
	multiple files are given, they are treated as if they were specified 
	in a LeanPub index file.

``-``
	The input comes from STDIN.


Installation
============

**Note:** Requires Python 3.3 or later. For Python 2 environments use
the **MarkdownTools2** package.

Install with::

	pip install MarkdownTools

This will create the command ``mdmerge``. Use ``mdmerge --version`` and 
``mdmerge --help`` to confirm the installation.

For developers
==============

License and Copyright
---------------------

MarkdownTools is licensed with the `Mozilla Public License`_ Version 2.0. 

Copyright 2014 Dave Hein

.. _Mozilla Public License: http://www.mozilla.org/MPL/2.0/

Source code
-----------

The source for this project can be found on GitHub at:

https://github.com/JeNeSuisPasDave/MarkdownTools

