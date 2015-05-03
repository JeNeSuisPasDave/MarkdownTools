# Change Log

## 1.0.1

* 3 May 2015
* Recognized "{{TOC}}" and do not treat as a file transclusion. MultiMarkdown 4.7.1 added the ability to generate a Table of Contents, triggered by the special string "{{TOC}}".
* Changed implementation to conform to PEP-8 and PEP-257.

## 1.0

* 30 March 2014
* First stable release
* Added developer docs. (To build them you'll need some tools, see `docs-support` and `docs` folders in the `master` branch.) If you want to contribute, I recommend building and reading through the docs.

## 1.0rc5

* 30 March 2014
* Now will pickup include spec found on last line of file. (issue #2)
* Now strips out MultiMarkdown metadata from all but first input or included file. (issue #3)

## 1.0rc4

* 24 March 2014
* Fixed further bug with unicode text handling in some locales. (issue #1)
* Fixed bug processing consecutive includes with no intervening text. (issue #2)

## 1.0rc3

* 23 March 2014
* Handle code fence specified with backticks (`` ` ``) or tildes (`~`)

## 1.0rc2

* 19 March 2014
* Add support for postprocessing raw includes (<<{filepath}); option `--just-raw`
* Add option to suppress processing MultiMarkdown file transclusions; option `--ignore-transclusions`
* Added the CHANGELOG.md file
* fixed bug with unicode text handling in the Python 2 implementation (MarkdownTools2)

## 1.0rc1

* 15 March 2014
* Initial release

