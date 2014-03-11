#! /bin/bash
#
export PYTHONPATH=`pwd`/src
python -m unittest tests.test_CLI.CoreCLITests
unset PYTHONPATH
