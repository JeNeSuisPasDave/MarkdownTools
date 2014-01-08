#! /bin/bash
#
export PYTHONPATH=`pwd`/src
python -m mdMerge.markdownMerge $*
unset PYTHONPATH
