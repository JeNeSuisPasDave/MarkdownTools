#! /bin/bash
#
export PYTHONPATH=`pwd`/src
python -m mdmerge.cli $*
unset PYTHONPATH
