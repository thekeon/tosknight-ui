#!/usr/bin/env bash

ROOT=$(dirname "${BASH_SOURCE}")/..

cd ${ROOT}
rm -rf docs/
mkdir -p docs/source
cp -r content/* docs/
exec python3 ./src/generate.py --storage-dir ../storage --ui-dir ./$@
cd - > /dev/null
