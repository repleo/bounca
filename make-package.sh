#!/usr/bin/env bash -e


BASEDIR=$(dirname "$0")
WORKDIR="$BASEDIR/out/bounca"
VERSION=$(git rev-parse --abbrev-ref HEAD)

if [ "$VERSION" == "master" ]; then
    VERSION="0.0.0-$VERSION"
fi

cd $BASEDIR
./run-checks.sh
./run-tests.sh


echo "Archive will be created ./out"
rm -rf $WORKDIR | true
mkdir -p $WORKDIR
git archive master | tar -x -C $WORKDIR

cd $WORKDIR
rm -rf ./vuetifyforms
cd front

sed -i '' -e s/\"version\":\ \"0.0.0-dev\"/\"version\":\ \"$VERSION\"/g package.json
npm install
npm run build --production
rm -rf node_modules public src
rm .babelrc .env .env.production .eslintignore .eslintrc.js .postcssrc.js
rm Makefile README.md babel.config.js package-lock.json package.json vue.config.js

cd "../.."
tar -czvf "bounca-$VERSION.tar.gz" bounca/
rm -rf $WORKDIR | true


