#!/usr/bin/env bash -ex


BASEDIR=$(dirname "$0")

cd front
#rm -rf node_modules public src
#rm .babelrc .env .env.production .eslintignore .eslintrc.js .postcssrc.js
#rm Makefile README.md babel.config.js package-lock.json package.json vue.config.js

cd ..

mkdir out
mv api out/
mv bounca out/
mv certificate_engine out/
mv etc out/
mv front out/
mv logs out/
mv x509_pki out/
mv CONTRIBUTING.md out/
mv LICENSE out/
mv README.md out/
mv changelog.md out/
mv requirements.txt out/

tar -czvf "bounca.tar.gz" --owner=0 --group=0 out/

