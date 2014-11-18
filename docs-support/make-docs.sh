#! /bin/sh
#
rbenv local 2.1.1
compass compile .
rbenv local --unset
