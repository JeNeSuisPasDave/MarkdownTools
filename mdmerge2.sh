#! /bin/bash
#
export PYTHONPATH=`pwd`/src
cd tests/data
python -m mdmerge.cli $*
cd ../..
unset PYTHONPATH
