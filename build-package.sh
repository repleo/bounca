#!/usr/bin/env bash -ex


BASEDIR=$(dirname "$0")
VERSION=$(awk '{ sub(/.*\//, ""); print }' <<< "$CI_COMMIT_REF_NAME")

echo "$VERSION"

if [ "$VERSION" == "master" ]; then
    VERSION="0.0.0-$VERSION"
fi




cd front
#rm -rf node_modules public src
#rm .babelrc .env .env.production .eslintignore .eslintrc.js .postcssrc.js
#rm Makefile README.md babel.config.js package-lock.json package.json vue.config.js

cd ..

mkdir out
mv api out/
mv bounca out/
mv certifcate_engine out/
mv etc out/
mv front out/
mv logs out/
mv x509_pki out/
mv CONTRIBUTING.md out/
mv LICENSE out/
mv README out/
mv changelog.md out/
mv requirements.txt out/

tar -czvf "bounca-$VERSION.tar.gz" --owner=0 --group=0 out/
mkdir package
mv "bounca-$VERSION.tar.gz" package
