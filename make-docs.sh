#!/usr/bin/env -S bash -e

WORKDIR=`dirname "$0"`
PYTHON=`which python3`

virtualenv -p "$PYTHON" env
. env/bin/activate
cd "$WORKDIR"

pip install -r requirements.docs.txt

cd docs
make html
cd ..
rm -rf ./bounca/static/docs/* || true
cp -r ./docs/build/html/ ./bounca/static/docs/
