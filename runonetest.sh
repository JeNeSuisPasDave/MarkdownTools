#! /bin/bash
#
export PYTHONPATH=`pwd`/src
python -m unittest tests.test_MarkdownMerge.MarkdownMergeTests.testLeanpubIndexMissingFile
unset PYTHONPATH
