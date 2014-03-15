#! /bin/sh
#
python setup.py --long-description | rst2html.py > output.html
