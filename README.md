# MarkdownTools

MarkdownTools is a collection of command line utilities for processing Markdown text files. At the moment the collection includes only one utility: *mdmerge*. Over time additional utilities will be added to support Markdown workflows. 

## mdmerge

mdmerge is a command line utility that produces a single Markdown document by merging a set of Markdown documents. The merge can be accomplished by expanding *include* specifications found in the input files, by concatenating a list of files found in an index file, or both.

### Synergy with Marked

Brett Terpstra's [Marked 2][] application is a GUI product that runs on OS X; it watches Markdown text files and displays the formatted output; it has extensive support for multi-file Markdown documents. *Marked* is my tool of choice for viewing formatted Markdown. I use it whenever I'm creating or reviewing Markdown content on my OS X machine. The invaluable multi-file document support in *Marked* is what drove me to create *mdmerge*.

[Marked 2]: http://marked2app.com

*mdmerge* brings that same multi-file Markdown document processing to the command line. It is useful in any automated scripting environment where Markdown is processed. For example, I use it in automated build scripts (e.g., using gmake or Grunt) to produce documentation for the software I'm building. It is cross-platform; you can pre-process the Markdown files on any common OS that has a recent version of Python.

### Markdown and include file syntax support

mdmerge has been tested with documents containing these Markdown syntax variants:

* classic ([John Gruber's Markdown syntax][gruber])
* MultiMarkdown (Fletcher Penny's syntax, [MultiMarkdown][mmd] version 4)
* [GHF][ghf] (GitHub Flavored Markdown)

[gruber]: http://daringfireball.net/projects/markdown/syntax
[mmd]: http://fletcherpenney.net/multimarkdown/
[ghf]: https://help.github.com/articles/github-flavored-markdown

mdmerge accepts include declarations in these styles

* [MultiMarkdown transclusion][mmdtrans]
* [Marked file includes][terpstramf]
* [LeanPub code includes][leanpubcd] (as [interpreted by Marked][terpstracd])
* [LeanPub index files][leanpubidx]
* [mmd_merge index files][mmdidx]

[terpstramf]: http://marked2app.com/help/Multi-File_Documents.html
[terpstracd]: http://marked2app.com/help/Special_Syntax.html#includingcode
[leanpubcd]: https://leanpub.com/help/manual#leanpub-auto-code
[leanpubidx]: https://leanpub.com/help/manual#leanpub-auto-the-booktxt-file
[mmdtrans]: http://fletcher.github.io/MultiMarkdown-4/transclusion
[mmdidx]: https://github.com/fletcher/MMD-Support/blob/master/Utilities/mmd_merge.pl

Includes can be nested; that is, a file can include another file that itself include other files, and so on. Index (or book) files are only processed as such when they are the primary input; they cannot be nested -- but the files listed in the index file are treated as normal input files (expanding include specifications found within).

## some examples

This example shows an include specification of another markdown file:

<pre><code class="markdown">This next bit is an included Markdown file. If it also has embedded include specifications, they will be processed as well; these kinds of includes are nested.

&lt;&lt;&#91;section-a.md&#93;

End of example.</code></pre>

This example shows an include specification for source code:

<pre><code class="markdown">This next bit is included source code. It is not examined for nested include specifications.

&lt;&lt;(example.c)

End of example.</code></pre>

This example shows a normal transclusion and a sourcde code transclusion, MultiMarkdown style:

<pre><code class="markdown">This demonstrates MultiMarkdown transclusions:

{{section-a.mmd}}

```C
{{example.c}}
```

End of example.</code></pre>

And of course there are raw file includes (`<<{raw.html}`) and index files. Read the documentation linked in the previous section or look at `docs/specifications.mmd` in one of the code branches.

## Installation

Installation packages are available on PyPI. For Python 3 (3.3 or later) install the  `MarkdownTools`; for Python 2 (2.6 or later) install the `MarkdownTools2` package.

Install the package using pip, like this (in a Python 3 environment):

~~~bash
$ pip install --pre MarkdownTools
~~~

or (in a Python 2 environment):

~~~bash
$ pip install --pre MarkdownTools2
~~~

## Usage

The command line looks like this:

    mdmerge [options] [-o outputfile] inputfiles
    mdmerge [options] [-o outputfile] -

### Command arguments

options
:   One or more of `--book`, `--export-target`, `-h`, `--help`, `--leanpub`, `--version`.

`--book`
:   Treat STDIN as an index file (a "book" file).

`--export-target [html|latex|lyx|opml|rtf|odf]`
:   Indicates the ultimate output target of the markdown processor, but primarily impacts wildcard substitution in Marked inclusion.

`-h`
:   Help information

`--help`
:   Same as `-h`.

`--ignore-transclusions`
:   Leave any MultiMarkdown transclusion specifications alone; do not include
the specified file. Useful if you want to mix Marked/LeanPub includes and
MultiMarkdown includes, but have MultiMarkdown handline the transclusions.

`--just-raw`
:   Ignore all include specifications except for raw includes; useful for
processing the output of the Markdown processor to pick up the raw file include
specifications that should have passed through untouched.

`--leanpub`
:   Indicates that any input file named `book.txt` should be treated as a LeanPub index file.

`--version`
:   Gives the version information about the utility.

`-o outputfile`
:   The filepath in which to store the merged text. If not specified, then STDOUT is used.

`--outfile outputfile`
:   same as `-o`.

`-`
:   The input comes from STDIN.

`inputfiles`
:   A list of space separated input files that can be merged together. If multiple files are given, they are treated as if they were specified in a LeanPub index file.

## Development

MarkdownTools are written in Python. The project repository contains `python2/*` branches that target Python 2 (2.6 and later) and `python3/*` branches that target Python 3 (3.3 and later). There are unit tests on each branch that can be executed using the `runtests` command script.

The `master` branch does not contain any source or tests; it contains the README file and a few other files that describe aspects of the project.

## Testing

To run the tests:

~~~bash
$ ./runtests.sh
~~~

For Python 2 environments you will need to install the *mock* package (e.g., `pip install mock`).

## Contributing

Similar to the contribution guidance from <https://github.com/github/markup>:

1. Fork it.
1. Create a branch (`git checkout -b my_MarkdownTools`)
1. Commit your changes (`git commit -am "Added Snarkdown"`)
1. Push to the branch (`git push origin my_MarkdownTools`)
1. Open a [Pull Request](http://github.com/jenesuispasdave/MarkdownTools/pulls)
1. Enjoy a refreshing beverage and wait

## License and Copyright

MarkdownTools is licensed with the [Mozilla Public License Version 2.0][mpl]. 

Copyright 2014 Dave Hein

[mpl]: http://www.mozilla.org/MPL/2.0/
