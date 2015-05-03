#! /bin/bash
#

# Capture the file name of this bash script
#
SCRIPTNAME_=$0

# Check whether we are running in a python virtual environment
#
VENV_RUNNING_=`env | grep VIRTUAL_ENV | wc -l | tr -d [[:space:]]`
if [ 0 == ${VENV_RUNNING_} ]; then
  echo "ERROR: Python virtual environment not running"
  echo
  echo "Try '. venv27/bin/activate' to start the virtual environment, and"
  echo "then try '${SCRIPTNAME_}' again."
  echo
  exit 1
fi

# Check whether we are running Python 2
#
export PYVER_=`python --version 2>&1 | grep "^Python 2\." | wc -l | tr -d [[:space:]]`
if [ 0 == ${PYVER_} ]; then
  echo "ERROR: Python 3 is required. Found "`python --version`"."
  echo
  echo "Deactivate the current virtual environment."
  echo "Try '. venv27/bin/activate' to start the virtual environment, and"
  echo "then try '${SCRIPTNAME_}' again."
  echo
  exit 1
fi

# Check whether flake8 is installed
#
FLAKE8_INSTALLED_=`pip list | grep "^flake8 (" | wc -l | tr -d [[:space:]]`
if [ 0 == ${FLAKE8_INSTALLED_} ]; then
  echo "ERROR: flake8 is not installed"
  echo
  echo "Try 'pip install flake8' to install flake8, and"
  echo "then try '${SCRIPTNAME_}' again."
  echo
  exit 1
fi

# Check whether pep8-naming is installed
#
PEP8NAMING_INSTALLED_=`pip list | grep "^pep8-naming (" | wc -l | tr -d [[:space:]]`
if [ 0 == ${PEP8NAMING_INSTALLED_} ]; then
  echo "ERROR: pep8-naming is not installed"
  echo
  echo "Try 'pip install pep8-naming' to install pep8-naming, and"
  echo "then try '${SCRIPTNAME_}' again."
  echo
  exit 1
fi

# Check whether pep257 is installed
#
PEP257_INSTALLED_=`pip list | grep "^pep257 (" | wc -l | tr -d [[:space:]]`
if [ 0 == ${PEP257_INSTALLED_} ]; then
  echo "ERROR: pep257 is not installed"
  echo
  echo "Try 'pip install pep257' to install pep257, and"
  echo "then try '${SCRIPTNAME_}' again."
  echo
  exit 1
fi

# lint the source
#
export PYTHONPATH=`pwd`/src
cd src
flake8 --exclude=ez_setup.py --max-complexity=10 . > fixme.lint.txt 2>&1
pep257 --match='(?!ez_setup).*\.py' . >> fixme.lint.txt 2>&1
cd ..
cd tests
flake8 --max-complexity=10 . > fixme.lint.txt 2>&1
pep257 --match='.*\.py' . >> fixme.lint.txt 2>&1
cd ..

