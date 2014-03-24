#! /bin/bash
#
export PYTHONPATH=`pwd`/src
export PYTHONIOENCODING=ascii
python -m unittest discover -s ./tests
unset PYTHONIOENCODING
unset PYTHONPATH
