# Markdown Tools

# mdMerge

mdMerge is a python CLI utility that produces a single Markdown document by merging a set of Markdown documents. The merge can be accomplished by passing a list of input files to be concatenated in sequence, or by parsing input files for __include__ declarations, or both.

mdMerge has been tested with documents containing these Markdown syntax variants:

* classic ([John Gruber's Markdown syntax][gruber])
* MultiMarkdown (Fletcher Penny's syntax, MultiMarkdown version 4)
* GHF (GitHub Flavored Markdown)

[gruber]: http://daringfireball.net/projects/markdown/syntax

mdMerge accepts include declarations in these styles

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

## Invoking the command

## Input examples


