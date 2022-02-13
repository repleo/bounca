#!/usr/bin/env bash -ex


BASEDIR=$(dirname "$0")

cd front
rm -rf node_modules public src
rm .babelrc .env .env.production .eslintignore .eslintrc.js .postcssrc.js
rm Makefile README.md babel.config.js package.json vue.config.js

cd ..

mkdir -p out/bounca/
mv api out/bounca/
mv superuser_signup out/bounca/
mv bounca out/bounca/
mv certificate_engine out/bounca/
mv vuetifyforms out/bounca/
mv etc out/bounca/
mv front out/bounca/
mv logs out/bounca/
mv x509_pki out/bounca/
mv manage.py out/bounca/
mv CONTRIBUTING.md out/bounca/
mv LICENSE out/bounca/
mv README.md out/bounca/
mv changelog.md out/bounca/
mv requirements.txt out/bounca/

tar -czvf "bounca.tar.gz" --owner=0 --group=0 -C out .
