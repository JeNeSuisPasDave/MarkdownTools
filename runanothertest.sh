#! /bin/bash
#
export PYTHONPATH=`pwd`/src
python -m unittest tests.test_MarkdownMerge.MarkdownMergeTests.testMultiIncludesWith3FilesLastAtEndOfRoot
unset PYTHONPATH
