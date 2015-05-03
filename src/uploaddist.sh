#! /bin/bash
#
cp ../LICENSE.html .
python setup.py sdist upload
rm LICENSE.html
