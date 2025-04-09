#!/bin/sh

# identify the QGIS Python interpreter
# explicitly provided via arg 1 or defaulted to interpreter on MacOS platform
tgt_python="${1:-/Applications/QGIS.app/Contents/MacOS/bin/python3.9}"
echo "using QGIS Python at ${tgt_python}"

# run all unit tests with coverage report
$tgt_python -m coverage run -m pytest -v plugin/test/* --tb=long --disable-pytest-warnings && $tgt_python -m coverage report -m && $tgt_python -m coverage html -d cover