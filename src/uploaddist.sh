#! /bin/bash
#
cp ../LICENSE.html .
python setup.py sdist
rm LICENSE.html
