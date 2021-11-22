#!/usr/bin/env bash -ex


BASEDIR=$(dirname "$0")
WORKDIR="$BASEDIR/out/bounca"
VERSION=$(git rev-parse --abbrev-ref HEAD)

cd $BASEDIR
#./run-checks.sh
#./run-tests.sh


echo "Archive will be created ./out"
rm -rf $WORKDIR | true
mkdir -p $WORKDIR
git archive master | tar -x -C $WORKDIR

cd $WORKDIR
rm -rf ./vuetifyforms
cd front
sed -e s/\"version\":\ \"dev\"/\"version\":\ \"$VERSION\"/g package.json
npm install
npm run build --production
rm -rf node_modules public src
rm .babelrc .env .env.production .eslintignore .eslintrc.js .postcssrc.js
rm Makefile README.md babel.config.js package-lock.json package.json vue.config.js

cd "../.."
tar -czvf "bounca-$VERSION.tar.gz" bounca/

#cd ~/tmp/
#rm bounca-password.zip | true
#zip -P blox bounca-password.zip bounca.zip
#
#cd $basedir
#version=`python version.py`
#mv ~/tmp/bounca-password.zip $basedir/releases/bounca-v$version-password.zip
#cd $basedir/releases
#shasum bounca-v$version-password.zip > bounca-v$version-password.zip.sha1
##PYTHON=`which python3`
##
##virtualenv -p "$PYTHON" env
##. env/bin/activate
##cd "$WORKDIR"
##
##pip3.4 install -r requirements.txt
##
##python manage.py makemigrations
#
#
#WORKDIR=`dirname "$0"`
#PYTHON=`which python3`
#
#virtualenv -p "$PYTHON" env
#. env/bin/activate
#cd "$WORKDIR"
#
#pip3.4 install -r requirements.txt
#
#python manage.py makemigrations
